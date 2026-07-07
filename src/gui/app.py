"""Main application window for the Record Management System.

This module builds the GUI *shell*: the layout, navigation between the three
record sections (Clients, Airlines, Flights), and the view/edit/new controls.

Scope note: nothing here is wired to real persistence yet. Buttons call handler
methods so the flow is in place, but those handlers only manipulate the GUI (or
are ``# TODO`` stubs) -- they do not read from or write to the JSONL store. The
field definitions and sample rows below stand in for the record modules
(``record.client`` / ``record.airline`` / ``record.flight``) and will be sourced
from them once the data layer is integrated.
"""

import calendar
import datetime

import tkinter as tk
from tkinter import ttk

# Border colours for the detail fields. Each field widget sits inside a thin
# wrapper frame whose background acts as the border; recolouring that frame
# flags a required-but-empty field in red. The wrapper approach means the same
# validation cue works for both Entry and Combobox fields (ttk widgets can't be
# given a coloured border directly). tkinter has no rounded-corner support, so
# the cue is a red border rather than a red rounded outline -- rounded corners
# would need customtkinter or hand-drawn Canvas fields, avoided to stay
# dependency-free.
BORDER_NORMAL = "#cccccc"
BORDER_ERROR = "#d13438"

# Sort-direction glyphs shown in a sortable column header. Only the active
# column shows an arrow; inactive columns show just the field name.
SORT_ASCENDING = "▲"   # up
SORT_DESCENDING = "▼"  # down

# ---------------------------------------------------------------------------
# Section definitions.
#
# Each section mirrors a record type from the brief. ``fields`` is the ordered
# list of field names shown in the detail panel (these match the record
# modules' FIELDS tuples). ``auto`` lists fields the system assigns (ID, Type)
# which are always read-only. ``required`` lists the fields the user must fill
# before a record can be saved. ``list_fields`` are the columns summarised in
# the middle list. Records themselves are held in memory (see
# RecordManagerApp.section_records) and start empty until the data layer is
# wired to load them from the JSONL store.
# ---------------------------------------------------------------------------
SECTIONS = {
    "Clients": {
        "singular": "Client",
        # Pastel accent: shown as the button swatch and the panel tint.
        "color": "#DCE9F7",  # powder blue
        "fields": [
            "ID",
            "Type",
            "Name",
            "Address Line 1",
            "Address Line 2",
            "Address Line 3",
            "City",
            "State",
            "Zip Code",
            "Country",
            "Phone Number",
        ],
        # ID and Type are assigned by the system, never typed by the user.
        "auto": ["ID", "Type"],
        "required": [
            "Name",
            "Address Line 1",
            "City",
            "State",
            "Zip Code",
            "Country",
            "Phone Number",
        ],
        "list_fields": ["ID", "Name"],
        "sortable": True,  # Clickable, sortable column headers.
        "search_hint": "Search Client name",
    },
    "Airlines": {
        "singular": "Airline",
        "color": "#DDEFE0",  # mint green
        "fields": ["ID", "Type", "Company Name"],
        # ID and Type are assigned by the system, never typed by the user.
        "auto": ["ID", "Type"],
        "required": ["Company Name"],
        "list_fields": ["ID", "Company Name"],
        "sortable": True,
        "search_hint": "Search Company name",
    },
    "Flights": {
        "singular": "Flight",
        "color": "#F6E7CE",  # warm sand
        "fields": ["Client_ID", "Airline_ID", "Date", "Start City", "End City"],
        # Flights have no system-assigned ID of their own; the two link IDs are
        # chosen by the user (they reference existing Client/Airline records).
        "auto": [],
        # Every Flight field is required -- there are no optional ones.
        "required": ["Client_ID", "Airline_ID", "Date", "Start City", "End City"],
        # Reference fields: shown as dropdowns of human-readable names from
        # another section, but stored as that section's ID. ``label`` renames
        # the field in the UI (Client_ID -> "Client"); the data key is unchanged.
        "references": {
            "Client_ID": {"section": "Clients", "display": "Name", "label": "Client"},
            "Airline_ID": {
                "section": "Airlines",
                "display": "Company Name",
                "label": "Airline",
            },
        },
        # Composite field: the stored "Date" (ISO 8601 string) is entered via
        # separate Year/Month/Day dropdowns and 24-hour HH:MM boxes, then
        # reassembled on save. The record's data structure is unchanged.
        "datetime_field": "Date",
        "list_fields": ["Client_ID", "Airline_ID", "Date"],
        # All three list columns are sortable, including Date (ISO strings sort
        # chronologically).
        "sortable": True,
        "search_hint": "Search company or client name",
    },
}

SECTION_ORDER = ["Clients", "Airlines", "Flights"]


def _darken(hex_color, factor):
    """Return ``hex_color`` scaled toward black by ``factor`` (0..1).

    Used to derive the hover/pressed shades of a button's pastel base colour.
    """
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

# Proportional widths of the three columns (sidebar | list | details). Kept as
# grid weights with a shared uniform group so the panels hold these ratios as
# the window is resized, rather than one column absorbing all the extra space.
COLUMN_WEIGHTS = {"sidebar": 20, "list": 38, "detail": 42}


class RecordManagerApp(tk.Tk):
    """The main window: sidebar navigation + list + detail/edit panel."""

    def __init__(self):
        super().__init__()
        self.title("Travel Agent - Record Management System")
        self.geometry("960x560")
        self.minsize(820, 460)

        # Currently selected section (e.g. "Clients") and the record dict the
        # detail panel is showing. The detail entry widgets are kept keyed by
        # field name so we can read/populate them and toggle their state.
        self.current_section = None
        # In-memory records per section, empty until wired to the JSONL store.
        # (New/Save would append here; load would replace these lists.)
        self.section_records = {name: [] for name in SECTIONS}
        self.current_records = []
        # The records currently visible in the list (== current_records unless a
        # search has filtered it). List selection is mapped back through this.
        self.displayed_records = []
        # field -> (widget, var, border): widget is an Entry or Combobox, var
        # holds its shown text, border is the wrapper frame used for the red
        # required-field cue.
        self.detail_entries = {}
        # field -> {"to_id": {display: id}, "to_display": {id: display}} for the
        # Flight reference dropdowns (Client_ID/Airline_ID).
        self.ref_index = {}
        # Required-field labels whose trailing "*" is shown only while the field
        # is flagged red. field -> (label_widget, base_text) for normal fields;
        # {"date"/"time": (label_widget, base_text)} for the composite field.
        self.detail_labels = {}
        self.dt_labels = {}
        # part-name -> (widget, var, border) for the composite Date/Time field
        # (keys: year, month, day, hour, minute). Empty for non-Flight sections.
        self.dt = {}
        # Whether the detail panel is currently showing a selected record (vs
        # blank). The Edit button only appears when a record is shown.
        self._record_shown = False
        # Current sort for sortable sections: which list_field, ascending or not.
        self.sort_field = None
        self.sort_ascending = True
        # Pending debounced search job id (from ``after``), or None.
        self._search_job = None
        # Placeholder (hint) state for the search box: the current hint text and
        # whether the box is currently showing it (rather than a real query).
        self._search_hint = ""
        self._placeholder_active = False
        self.editing = False

        self._build_title_bar()
        self._build_body()

        # Route the window-close (X) button through our own handler so the
        # app has a single, well-defined shutdown path.
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start on the welcome panel; it is dismissed on the first selection.
        self._show_welcome()

    # -- Layout construction ------------------------------------------------

    def _build_title_bar(self):
        """The banner across the top of the window."""
        title = ttk.Label(
            self,
            text="Travel Agent - Record Management System",
            anchor="center",
            padding=(10, 8),
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(side="top", fill="x")
        ttk.Separator(self, orient="horizontal").pack(side="top", fill="x")

    def _build_body(self):
        """The three columns: sidebar | list | details, in fixed proportions."""
        body = ttk.Frame(self)
        body.pack(side="top", fill="both", expand=True)

        # Proportional columns via grid weights sharing one uniform group.
        body.columnconfigure(0, weight=COLUMN_WEIGHTS["sidebar"], uniform="cols")
        body.columnconfigure(1, weight=COLUMN_WEIGHTS["list"], uniform="cols")
        body.columnconfigure(2, weight=COLUMN_WEIGHTS["detail"], uniform="cols")
        body.rowconfigure(0, weight=1)

        self._build_sidebar(body)
        self._build_list_panel(body)
        self._build_detail_panel(body)
        self._build_welcome(body)

    def _build_sidebar(self, parent):
        """Left column: 'Travel Records' header, section buttons, auto-save hint."""
        sidebar = ttk.Frame(parent, padding=10)
        sidebar.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            sidebar, text="Travel Records", font=("Segoe UI", 11, "bold")
        ).pack(side="top", anchor="w", pady=(0, 8))

        # Nav buttons carry their section's pastel colour, with darker hover and
        # pressed shades. Classic tk.Button is used (not ttk) because the Windows
        # ttk theme ignores button background; tk.Button honours bg directly and
        # lets us drive hover/press states via bindings.
        self.nav_buttons = {}
        for name in SECTION_ORDER:
            base = SECTIONS[name]["color"]
            hover = _darken(base, 0.93)
            pressed = _darken(base, 0.85)
            btn = tk.Button(
                sidebar,
                text=name,
                font=("Segoe UI", 12),
                bg=base,
                fg="black",
                activebackground=pressed,
                activeforeground="black",
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda n=name: self.select_section(n),
            )
            # ipady sets button height; pady is the gap between buttons.
            btn.pack(side="top", fill="x", pady=2, ipady=8)
            # Hover and press feedback (base -> hover -> pressed -> hover).
            btn.bind("<Enter>", lambda e, b=btn, c=hover: b.configure(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=base: b.configure(bg=c))
            btn.bind("<ButtonPress-1>", lambda e, b=btn, c=pressed: b.configure(bg=c))
            btn.bind("<ButtonRelease-1>", lambda e, b=btn, c=hover: b.configure(bg=c))
            self.nav_buttons[name] = btn

        # Greyed-out reassurance that closing the app is safe -- it saves.
        ttk.Label(
            sidebar,
            text="Data auto-saves on exit",
            foreground="grey",
            font=("Segoe UI", 8),
            wraplength=140,
        ).pack(side="bottom", anchor="w")

    def _build_list_panel(self, parent):
        """Middle column: section header, search row, entry list."""
        middle = self.middle_panel = ttk.Frame(parent, padding=10)
        middle.grid(row=0, column=1, sticky="nsew")

        self.list_header = ttk.Label(middle, text="", font=("Segoe UI", 12, "bold"))
        self.list_header.pack(side="top", anchor="w", pady=(0, 6))

        # Search row sits directly above the list it filters. The list updates
        # as you type (debounced); Clear resets the box and the filter.
        search_row = ttk.Frame(middle)
        search_row.pack(side="top", fill="x", pady=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._schedule_search())
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        # Default text colour, so the placeholder can go grey and back.
        self._search_fg = self.search_entry.cget("foreground")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        ttk.Button(search_row, text="Clear", command=self.on_clear_search).pack(
            side="left", padx=(6, 0)
        )

        # The entry list, as a Treeview so it can show column headings for the
        # fields being displayed. Columns are (re)configured per section in
        # _populate_list. Selecting a row loads it into the detail panel.
        list_wrap = ttk.Frame(middle)
        list_wrap.pack(side="top", fill="both", expand=True)
        self.tree = ttk.Treeview(list_wrap, show="headings", selectmode="browse")
        scroll = ttk.Scrollbar(
            list_wrap, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_entry)

    def _build_detail_panel(self, parent):
        """Right column: field details, required-field legend, action buttons."""
        right = self.right_panel = ttk.Frame(parent, padding=10)
        right.grid(row=0, column=2, sticky="nsew")

        ttk.Label(right, text="Details", font=("Segoe UI", 12, "bold")).pack(
            side="top", anchor="w", pady=(0, 6)
        )

        # Fields get rebuilt whenever the section changes.
        self.fields_frame = ttk.Frame(right)
        self.fields_frame.pack(side="top", fill="both", expand=True)

        # Hint for the composite time entry. Shown only while editing/creating a
        # Flight (see _set_editing), sitting just above the required-field legend.
        self.time_hint = ttk.Label(
            right,
            text="Time uses the 24-hour clock (HH 00-23, MM 00-59)",
            foreground="grey",
            font=("Segoe UI", 8),
        )

        # Legend explaining the asterisk / red border on required fields. Only
        # shown while editing or creating a record (see _set_editing).
        self.required_legend = ttk.Label(
            right,
            text="*  Required field",
            foreground=BORDER_ERROR,
            font=("Segoe UI", 8),
        )

        # Button row. Edit is shown by default; Save/Cancel are hidden until
        # editing starts. New is always visible and renamed per section.
        buttons = ttk.Frame(right)
        buttons.pack(side="bottom", fill="x", pady=(8, 0))

        self.edit_button = ttk.Button(buttons, text="Edit", command=self.on_edit)
        self.save_button = ttk.Button(buttons, text="Save", command=self.on_save)
        self.cancel_button = ttk.Button(
            buttons, text="Cancel", command=self.on_cancel
        )
        self.new_button = ttk.Button(buttons, text="New", command=self.on_new)

        self.edit_button.pack(side="left")
        self.new_button.pack(side="right")
        # Save/Cancel are packed on demand in _set_editing().

    def _build_welcome(self, parent):
        """Welcome panel shown on launch, covering the list + detail columns.

        It is dismissed the first time the user picks a section (see
        select_section) and does not return for the rest of the session.
        """
        # Team credits, sorted by surname ("Lastname, Firstname").
        credits = [
            "Kovakina, Svetlana",
            "Mekwunye, Victor",
            "Nguyen, Khanh Ngoc",
            "Onat, Yagiz",
            "Sirin, Kerem",
        ]

        self.welcome_panel = ttk.Frame(parent, padding=20)
        self.welcome_panel.grid(row=0, column=1, columnspan=2, sticky="nsew")

        # Centred welcome message.
        message_area = ttk.Frame(self.welcome_panel)
        message_area.pack(side="top", fill="both", expand=True)
        centred = ttk.Frame(message_area)
        centred.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(
            centred,
            text="Welcome to the Travel Agent - Record Management System",
            font=("Segoe UI", 14, "bold"),
            wraplength=420,
            justify="center",
        ).pack()
        ttk.Label(
            centred,
            text="Select an option on the left to get started.",
            foreground="grey",
            justify="center",
        ).pack(pady=(8, 0))

        # Credits footer.
        ttk.Label(
            self.welcome_panel,
            text="Credits: " + "  •  ".join(credits),
            foreground="grey",
            font=("Segoe UI", 8),
            wraplength=520,
            justify="center",
        ).pack(side="bottom")

    def _show_welcome(self):
        """Show the welcome panel and hide the list + detail columns."""
        self.middle_panel.grid_remove()
        self.right_panel.grid_remove()
        self.welcome_panel.grid()

    def _hide_welcome(self):
        """Hide the welcome panel and restore the list + detail columns."""
        self.welcome_panel.grid_remove()
        self.middle_panel.grid()
        self.right_panel.grid()

    # -- Detail field rendering --------------------------------------------

    def _build_ref_index(self, section):
        """Build display<->id maps for the section's reference (dropdown) fields.

        For each reference field (e.g. Flight's Client_ID) this reads the target
        section's records and maps each ID to a human-readable display string
        (e.g. the client's Name) and back. Stored so the dropdowns can show names
        while the record keeps the ID. Uses sample data for now; will read from
        the shared store once wired.
        """
        self.ref_index = {}
        for field, ref in SECTIONS[section].get("references", {}).items():
            to_id, to_display = {}, {}
            for record in self.section_records[ref["section"]]:
                display = str(record.get(ref["display"], ""))
                rec_id = record.get("ID")
                to_id[display] = rec_id
                to_display[rec_id] = display
            self.ref_index[field] = {"to_id": to_id, "to_display": to_display}

    def _render_fields(self, section):
        """Rebuild the detail form for the given section's fields."""
        for child in self.fields_frame.winfo_children():
            child.destroy()
        self.detail_entries = {}
        self.dt = {}
        self.detail_labels = {}
        self.dt_labels = {}
        self._build_ref_index(section)

        required = SECTIONS[section]["required"]
        references = SECTIONS[section].get("references", {})
        datetime_field = SECTIONS[section].get("datetime_field")

        # ``fields`` maps 1:1 to rows except the composite date/time field,
        # which spans two rows, so track the grid row explicitly.
        row = 0
        for field in SECTIONS[section]["fields"]:
            if field == datetime_field:
                row = self._render_datetime_rows(row, field in required)
                continue

            # Reference fields may show a friendlier label (Client_ID -> Client).
            base_label = references[field]["label"] if field in references else field
            label = ttk.Label(self.fields_frame, text=f"{base_label}:")
            label.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
            # Required labels get a "*" only while flagged red (see
            # _validate_required); keep the label + base text to toggle it.
            if field in required:
                self.detail_labels[field] = (label, base_label)

            # The wrapper frame's background is the (recolourable) field border.
            border = tk.Frame(self.fields_frame, background=BORDER_NORMAL)
            border.grid(row=row, column=1, sticky="ew", pady=2)
            var = tk.StringVar()

            if field in references:
                # A dropdown of names; the record still stores the ID.
                widget = ttk.Combobox(
                    border,
                    textvariable=var,
                    values=list(self.ref_index[field]["to_id"].keys()),
                    state="disabled",
                )
            else:
                widget = tk.Entry(
                    border, textvariable=var, width=28, state="readonly",
                    relief="flat", highlightthickness=0,
                )
            widget.pack(fill="both", expand=True, padx=1, pady=1)

            # Re-validate live as the field's value changes.
            var.trace_add("write", lambda *_: self._validate_required())
            self.detail_entries[field] = (widget, var, border)
            row += 1

        self.fields_frame.columnconfigure(1, weight=1)

    def _bordered(self, parent, widget_factory):
        """Create a border-wrapped sub-widget and return (widget, var, border).

        Used for the composite date/time parts so each part can be flagged red
        individually, matching the wrapper-frame border used elsewhere.
        """
        border = tk.Frame(parent, background=BORDER_NORMAL)
        var = tk.StringVar()
        widget = widget_factory(border, var)
        widget.pack(padx=1, pady=1)
        var.trace_add("write", lambda *_: self._validate_required())
        return widget, var, border

    def _render_datetime_rows(self, row, required):
        """Render the Date (Y/M/D dropdowns) and Time (HH:MM) rows.

        Returns the next free grid row. Populates ``self.dt`` with the five
        parts; the stored value is reassembled from them in _datetime_value().
        """
        # -- Date row: Year / Month / Day dropdowns --
        date_label = ttk.Label(self.fields_frame, text="Date:")
        date_label.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        if required:
            self.dt_labels["date"] = (date_label, "Date")
        date_row = ttk.Frame(self.fields_frame)
        date_row.grid(row=row, column=1, sticky="w", pady=2)

        this_year = datetime.date.today().year
        years = [str(y) for y in range(this_year - 5, this_year + 11)]
        months = [f"{m:02d}" for m in range(1, 13)]

        self.dt["year"] = self._bordered(
            date_row,
            lambda p, v: ttk.Combobox(
                p, textvariable=v, values=years, width=6, state="disabled"
            ),
        )
        self.dt["month"] = self._bordered(
            date_row,
            lambda p, v: ttk.Combobox(
                p, textvariable=v, values=months, width=4, state="disabled"
            ),
        )
        self.dt["day"] = self._bordered(
            date_row,
            lambda p, v: ttk.Combobox(p, textvariable=v, width=4, state="disabled"),
        )
        # Pack the three date parts left-to-right with small gaps.
        for key in ("year", "month", "day"):
            self.dt[key][2].pack(side="left", padx=(0, 4))
        # Valid days depend on the chosen year+month.
        self.dt["year"][1].trace_add("write", lambda *_: self._update_days())
        self.dt["month"][1].trace_add("write", lambda *_: self._update_days())
        self._update_days()

        # -- Time row: HH : MM (24-hour), digit-and-range validated --
        time_label = ttk.Label(self.fields_frame, text="Time:")
        time_label.grid(row=row + 1, column=0, sticky="w", padx=(0, 8), pady=2)
        if required:
            self.dt_labels["time"] = (time_label, "Time")
        time_row = ttk.Frame(self.fields_frame)
        time_row.grid(row=row + 1, column=1, sticky="w", pady=2)

        hh_check = (self.register(lambda p: self._valid_time_part(p, 23)), "%P")
        mm_check = (self.register(lambda p: self._valid_time_part(p, 59)), "%P")
        self.dt["hour"] = self._bordered(
            time_row,
            lambda p, v: tk.Entry(
                p, textvariable=v, width=3, justify="center", state="readonly",
                relief="flat", highlightthickness=0,
                validate="key", validatecommand=hh_check,
            ),
        )
        self.dt["minute"] = self._bordered(
            time_row,
            lambda p, v: tk.Entry(
                p, textvariable=v, width=3, justify="center", state="readonly",
                relief="flat", highlightthickness=0,
                validate="key", validatecommand=mm_check,
            ),
        )
        self.dt["hour"][2].pack(side="left")
        ttk.Label(time_row, text=":").pack(side="left", padx=3)
        self.dt["minute"][2].pack(side="left")

        return row + 2

    def _update_days(self):
        """Refresh the Day dropdown to the valid range for the chosen month."""
        year_str = self.dt["year"][1].get()
        month_str = self.dt["month"][1].get()
        if year_str.isdigit() and month_str.isdigit():
            count = calendar.monthrange(int(year_str), int(month_str))[1]
        else:
            count = 31
        days = [f"{d:02d}" for d in range(1, count + 1)]
        self.dt["day"][0].configure(values=days)
        # Drop a day that no longer fits (e.g. 31 -> February).
        if self.dt["day"][1].get() and self.dt["day"][1].get() not in days:
            self.dt["day"][1].set("")

    @staticmethod
    def _valid_time_part(proposed, maximum):
        """Allow empty or a 1-2 digit number within 0..maximum (Entry key check)."""
        if proposed == "":
            return True
        if not proposed.isdigit() or len(proposed) > 2:
            return False
        return int(proposed) <= maximum

    def _datetime_value(self):
        """Reassemble the composite parts into an ISO 8601 string, or None.

        Returns ``YYYY-MM-DDTHH:MM`` when every part is present and valid,
        otherwise None (so validation can gate Save).
        """
        year = self.dt["year"][1].get()
        month = self.dt["month"][1].get()
        day = self.dt["day"][1].get()
        hour = self.dt["hour"][1].get()
        minute = self.dt["minute"][1].get()
        if not (year and month and day and hour != "" and minute != ""):
            return None
        if int(hour) > 23 or int(minute) > 59:
            return None
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}T{int(hour):02d}:{int(minute):02d}"

    def _set_datetime(self, value):
        """Populate the composite parts from a stored ISO string (or clear)."""
        date_part, _, time_part = str(value or "").partition("T")
        year, month, day = (date_part.split("-") + ["", "", ""])[:3]
        hour, minute = (time_part.split(":") + ["", ""])[:2]
        # Year/month first so _update_days sees them before day is set.
        self.dt["year"][1].set(year)
        self.dt["month"][1].set(month)
        self.dt["day"][1].set(day)
        self.dt["hour"][1].set(hour)
        self.dt["minute"][1].set(minute)

    def _show_record(self, record):
        """Populate the detail fields from a record dict (view mode).

        Reference fields translate the stored ID to its display name; all other
        fields show their value as-is.
        """
        self._record_shown = record is not None
        for field, (widget, var, _) in self.detail_entries.items():
            if record is None:
                var.set("")
            elif field in self.ref_index:
                var.set(self.ref_index[field]["to_display"].get(record.get(field), ""))
            else:
                var.set(str(record.get(field, "")))
        # Composite date/time field, if this section has one.
        if self.dt:
            datetime_field = SECTIONS[self.current_section]["datetime_field"]
            self._set_datetime(None if record is None else record.get(datetime_field))
        self._set_editing(False)

    def _field_state(self, field, editing):
        """Return the widget state a field should have for the given mode.

        Reference dropdowns use readonly/disabled (a readonly Combobox is still
        selectable); text fields use normal/readonly. System-assigned fields
        (ID, Type) stay read-only in every mode.
        """
        if field in SECTIONS[self.current_section]["auto"]:
            return "readonly"
        if field in self.ref_index:
            return "readonly" if editing else "disabled"
        return "normal" if editing else "readonly"

    def _set_editing(self, editing):
        """Toggle the detail panel between read-only and editable.

        When editing, user fields become writable and the Edit button is
        swapped for Save + Cancel. New is disabled mid-edit to keep the flow
        simple.
        """
        self.editing = editing
        for field, (widget, _, _) in self.detail_entries.items():
            widget.configure(state=self._field_state(field, editing))
        # Date/time parts: dropdowns readonly/disabled, HH:MM boxes normal/readonly.
        for key, (widget, _, _) in self.dt.items():
            if key in ("hour", "minute"):
                widget.configure(state="normal" if editing else "readonly")
            else:
                widget.configure(state="readonly" if editing else "disabled")

        if editing:
            if self.dt:
                self.time_hint.pack(side="top", anchor="w", pady=(6, 0))
            self.required_legend.pack(side="top", anchor="w", pady=(2, 0))
            self.edit_button.pack_forget()
            self.save_button.pack(side="left")
            self.cancel_button.pack(side="left", padx=(6, 0))
            self.new_button.configure(state="disabled")
            self._validate_required()
        else:
            self.time_hint.pack_forget()
            self.required_legend.pack_forget()
            self.save_button.pack_forget()
            self.cancel_button.pack_forget()
            # Edit only makes sense when a record is selected/shown.
            if self._record_shown:
                self.edit_button.pack(side="left")
            else:
                self.edit_button.pack_forget()
            self.new_button.configure(state="normal")
            self._clear_borders()

    @staticmethod
    def _mark_label(label_base, invalid):
        """Show a trailing '*' on a label only while its field is flagged red."""
        if label_base is None:
            return
        label, base = label_base
        label.configure(text=f"{base} *:" if invalid else f"{base}:")

    def _validate_required(self):
        """Flag empty required fields in red and gate the Save button.

        Runs only while editing. Any required field left blank gets a red
        border and its label shows a '*'; Save stays disabled until every
        required field is filled.
        """
        if not self.editing:
            return
        required = SECTIONS[self.current_section]["required"]
        all_filled = True
        for field, (_, var, border) in self.detail_entries.items():
            invalid = field in required and not var.get().strip()
            border.configure(background=BORDER_ERROR if invalid else BORDER_NORMAL)
            self._mark_label(self.detail_labels.get(field), invalid)
            if invalid:
                all_filled = False

        # Composite date/time field: flag each empty/invalid part, mark the
        # Date/Time labels, and gate Save on it reassembling into a valid value.
        if self.dt:
            datetime_field = SECTIONS[self.current_section]["datetime_field"]
            dt_required = datetime_field in required
            date_invalid = False
            for key in ("year", "month", "day"):
                bad = dt_required and not self.dt[key][1].get()
                self.dt[key][2].configure(
                    background=BORDER_ERROR if bad else BORDER_NORMAL
                )
                date_invalid = date_invalid or bad
            time_invalid = False
            for key, hi in (("hour", 23), ("minute", 59)):
                value = self.dt[key][1].get()
                bad = dt_required and (value == "" or not value.isdigit() or int(value) > hi)
                self.dt[key][2].configure(
                    background=BORDER_ERROR if bad else BORDER_NORMAL
                )
                time_invalid = time_invalid or bad
            self._mark_label(self.dt_labels.get("date"), date_invalid)
            self._mark_label(self.dt_labels.get("time"), time_invalid)
            if dt_required and self._datetime_value() is None:
                all_filled = False

        self.save_button.configure(state="normal" if all_filled else "disabled")

    def _clear_borders(self):
        """Reset field borders to normal and remove the '*' marks (view mode)."""
        for _, _, border in self.detail_entries.values():
            border.configure(background=BORDER_NORMAL)
        for _, _, border in self.dt.values():
            border.configure(background=BORDER_NORMAL)
        for label_base in self.detail_labels.values():
            self._mark_label(label_base, False)
        for label_base in self.dt_labels.values():
            self._mark_label(label_base, False)

    # -- Navigation / event handlers ---------------------------------------

    def select_section(self, section):
        """Switch the visible section (Clients / Airlines / Flights)."""
        # Dismiss the welcome panel on the first selection (no-op afterwards).
        self._hide_welcome()

        self.current_section = section
        singular = SECTIONS[section]["singular"]

        # Reflect the active section in the header and the New button label.
        self.list_header.configure(text=section)
        self.new_button.configure(text=f"New {singular}")

        # Sortable sections open sorted by their first column, ascending.
        if SECTIONS[section].get("sortable"):
            self.sort_field = SECTIONS[section]["list_fields"][0]
            self.sort_ascending = True

        # Reset the search box to this section's greyed hint.
        self._search_hint = SECTIONS[section]["search_hint"]
        self._show_placeholder()

        # Rebuild the detail form for this section's fields, then reload the
        # list from the in-memory store (empty until persistence is wired).
        self._render_fields(section)
        self.current_records = self.section_records[section]
        self._populate_list(self.current_records)
        self._show_record(None)
        self._apply_section_color(section)

    def _apply_section_color(self, section):
        """Tint the list + detail panels with the section's pastel colour.

        The panels and their ttk frame/label descendants share two styles
        (``Panel.TFrame`` / ``Panel.TLabel``); recolouring those styles retints
        everything at once. Input fields (Treeview, Entry, Combobox, buttons)
        keep their default look so text stays crisp and readable.
        """
        color = SECTIONS[section].get("color")
        if not color:
            return
        style = ttk.Style()
        style.configure("Panel.TFrame", background=color)
        style.configure("Panel.TLabel", background=color)
        for panel in (self.middle_panel, self.right_panel):
            self._tint_subtree(panel)

    def _tint_subtree(self, widget):
        """Assign the Panel styles to ttk frames/labels in a widget subtree.

        Called after rebuilds so freshly created fields pick up the tint. Only
        ttk frames and labels are restyled; other widgets are left untouched.
        """
        cls = widget.winfo_class()
        if cls == "TFrame":
            widget.configure(style="Panel.TFrame")
        elif cls == "TLabel":
            widget.configure(style="Panel.TLabel")
        for child in widget.winfo_children():
            self._tint_subtree(child)

    def _populate_list(self, records):
        """Fill the list with the given records, one row per record.

        Columns and their headings are set from the section's ``list_fields``
        so the header row names exactly what is shown (e.g. ID / Name for
        Clients). Each row's iid is its index into ``records`` so selection can
        be mapped straight back.
        """
        fields = SECTIONS[self.current_section]["list_fields"]
        sortable = SECTIONS[self.current_section].get("sortable", False)
        rows = self._sorted(records) if sortable else list(records)

        self.tree["columns"] = fields
        for field in fields:
            if sortable:
                # Only the active column shows an arrow; others show just the name.
                if field == self.sort_field:
                    arrow = SORT_ASCENDING if self.sort_ascending else SORT_DESCENDING
                    heading_text = f"{field} {arrow}"
                else:
                    heading_text = field
                self.tree.heading(
                    field, text=heading_text,
                    command=lambda f=field: self.on_sort(f),
                )
            else:
                # Reset any command left over from a sortable section.
                self.tree.heading(field, text=field, command="")
            # ID columns are fixed-width; other columns absorb the extra width.
            # Without stretch=False on the IDs, ttk splits leftover space evenly
            # and every column ends up about the same size. The width must fit
            # the heading label plus the sort arrow, else the arrow is clipped
            # (a plain "ID" needs little; "Client_ID"/"Airline_ID" need more).
            is_id = "ID" in field
            id_width = max(70, len(field) * 8 + 40)
            self.tree.column(
                field,
                width=id_width if is_id else 140,
                minwidth=id_width if is_id else 100,
                stretch=not is_id,
                anchor="w",
            )

        self.tree.delete(*self.tree.get_children())
        for index, record in enumerate(rows):
            values = [record.get(f, "") for f in fields]
            self.tree.insert("", "end", iid=str(index), values=values)
        self.displayed_records = rows

    def _sorted(self, records):
        """Return ``records`` sorted by the current sort field and direction.

        Strings sort case-insensitively; other types (e.g. int IDs) sort
        naturally. Values within a single column are of one type.
        """
        def key(record):
            value = record.get(self.sort_field, "")
            return value.lower() if isinstance(value, str) else value

        return sorted(records, key=key, reverse=not self.sort_ascending)

    def on_sort(self, field):
        """Handle a header click: toggle direction, or switch the sort column.

        Clicking the active column flips ascending/descending; clicking another
        column makes it the active sort, ascending. The list is then rebuilt,
        preserving any active search filter.
        """
        if self.sort_field == field:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_field = field
            self.sort_ascending = True
        # Re-run the current view (respects the search box) with the new order.
        if self.search_var.get().strip():
            self.on_search()
        else:
            self._populate_list(self.current_records)

    def on_select_entry(self, event=None):
        """Load the highlighted list row into the detail panel."""
        selection = self.tree.selection()
        if not selection:
            return
        self._show_record(self.displayed_records[int(selection[0])])

    def _show_placeholder(self):
        """Display the greyed hint text in the empty search box."""
        self._placeholder_active = True
        self.search_entry.configure(foreground="grey")
        self.search_var.set(self._search_hint)

    def _hide_placeholder(self):
        """Remove the hint so the user can type a real query."""
        self._placeholder_active = False
        self.search_entry.configure(foreground=self._search_fg)
        self.search_var.set("")

    def _on_search_focus_in(self, event=None):
        """Clear the hint when the user clicks into the search box."""
        if self._placeholder_active:
            self._hide_placeholder()

    def _on_search_focus_out(self, event=None):
        """Restore the hint if the box is left empty."""
        if not self.search_var.get():
            self._show_placeholder()

    def _schedule_search(self):
        """Debounce live search: run the filter shortly after typing stops.

        Rebuilding the list on every keystroke is wasteful once the data set is
        large, so coalesce rapid edits into a single filter run.
        """
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(200, self._run_search)

    def _run_search(self):
        self._search_job = None
        self.on_search()

    def on_search(self):
        """Filter the list by the search box text.

        Filtering is done here against the in-memory ``current_records`` (which
        will later be the records loaded from the store). No persistence is
        involved -- this only narrows what the list shows.
        """
        # The hint is not a query -- while it is showing, show the full list.
        if self._placeholder_active:
            self._populate_list(self.current_records)
            return
        query = self.search_var.get().strip().lower()
        if not query:
            self._populate_list(self.current_records)
            return
        # Search every field except Type: it is a constant per section, so it
        # only ever matches all rows or none (e.g. "e" hitting "Airline").
        fields = [f for f in SECTIONS[self.current_section]["fields"] if f != "Type"]
        matches = [
            r
            for r in self.current_records
            if any(query in self._search_text(r, f) for f in fields)
        ]
        self._populate_list(matches)

    def _search_text(self, record, field):
        """Return a field's searchable text, lower-cased.

        Reference fields (Flight's Client_ID/Airline_ID) are matched on their
        resolved name (e.g. "Emirates", "Ada Lovelace"), not the stored ID, so
        searching a Flight by company or client name works.
        """
        if field in self.ref_index:
            value = self.ref_index[field]["to_display"].get(record.get(field), "")
        else:
            value = record.get(field, "")
        return str(value).lower()

    def on_clear_search(self):
        """Clear the search box and show the full list again."""
        # Restore the greyed hint (the box is no longer focused after a click).
        self._show_placeholder()
        # Setting the box schedules a debounced run; cancel it and refresh now.
        if self._search_job is not None:
            self.after_cancel(self._search_job)
            self._search_job = None
        self._populate_list(self.current_records)

    def on_edit(self):
        """Make the currently shown record editable."""
        self._set_editing(True)

    def _field_value(self, field):
        """Return a field's value in the form the record stores.

        Reference dropdowns display a name but store the referenced ID, so this
        maps the shown name back to its ID. All other fields store their text
        as shown. This keeps the record's data structure unchanged (Client_ID /
        Airline_ID remain IDs) regardless of what the dropdown displays.
        """
        if self.dt and field == SECTIONS[self.current_section].get("datetime_field"):
            return self._datetime_value()
        _, var, _ = self.detail_entries[field]
        value = var.get()
        if field in self.ref_index:
            return self.ref_index[field]["to_id"].get(value)
        return value

    def on_save(self):
        """Confirm edits in the UI and return to view mode.

        TODO: wire to the data layer -- build the record dict via
        ``{f: self._field_value(f) for f in fields}`` (which resolves reference
        dropdowns back to IDs) and persist through RecordStore. For now this
        only exits edit mode; nothing is written to disk. (Save is only
        clickable once all required fields are filled -- see _validate_required.)
        """
        self._set_editing(False)

    def on_cancel(self):
        """Discard edits and return to view mode."""
        selection = self.tree.selection()
        record = self.displayed_records[int(selection[0])] if selection else None
        self._show_record(record)

    def _next_id(self):
        """Return the next auto-assigned ID for the current section.

        IDs start at 0 and ascend. The next ID is one past the highest existing
        ID in this section (0 when there are none yet). Assignment is per record
        type. Uses the in-memory ``current_records``; once wired to the store
        this will read from the shared records list instead.
        """
        ids = [
            r["ID"]
            for r in self.current_records
            if isinstance(r.get("ID"), int)
        ]
        return max(ids) + 1 if ids else 0

    def on_new(self):
        """Start a blank record for the current section.

        Opens the detail panel empty and editable, with required fields flagged
        red until filled. The system-assigned fields are pre-filled and stay
        read-only: ``Type`` is set from the section, and ``ID`` gets the next
        auto-assigned value.

        TODO: wire to the data layer -- on save this should create a new record
        via the section's factory and add it to the shared store.
        """
        self.tree.selection_remove(self.tree.selection())
        self._show_record(None)
        # Pre-fill the system-assigned fields where the section has them.
        if "Type" in self.detail_entries:
            self.detail_entries["Type"][1].set(SECTIONS[self.current_section]["singular"])
        if "ID" in self.detail_entries:
            self.detail_entries["ID"][1].set(str(self._next_id()))
        self._set_editing(True)

    def on_close(self):
        """Shutdown path: trigger record saving, then close the window.

        TODO: wire to the data layer -- call RecordStore.save() here so the
        shared records list is written to JSONL on exit. The hook lives here so
        persistence only needs plugging in, not restructuring.
        """
        # save_records()  # <- to be connected to the store
        self.destroy()


def main():
    RecordManagerApp().mainloop()


if __name__ == "__main__":
    main()
