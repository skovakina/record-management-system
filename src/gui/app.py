"""Main window for the Record Management System.

GUI shell only: layout, section navigation and the view/edit/new/delete controls.
Not wired to persistence yet -- save/load are ``# TODO`` stubs and records are
held in memory (see ``RecordManagerApp.section_records``).
"""

import calendar
import datetime

import tkinter as tk
from tkinter import messagebox, ttk

# Each detail field sits in a wrapper frame whose background acts as its border,
# so the red required-field cue works for both Entry and Combobox (ttk widgets
# can't take a coloured border directly, and tkinter has no rounded corners).
BORDER_NORMAL = "#cccccc"
BORDER_ERROR = "#d13438"

# Arrow shown on the active sort column only; inactive columns show no arrow.
SORT_ASCENDING = "▲"
SORT_DESCENDING = "▼"

# Per-section config. Field names ARE the record's data keys (snake_case, matching
# the record.* dataclasses in src/record); the UI label is derived from the key by
# _label_for, or (for reference fields) taken from the reference's "label". Keys:
# fields (detail order), auto (system-set, read-only), required (must be filled),
# list_fields (list columns), plus colour, sortable, search_hint and (Flights)
# references / datetime_field.
SECTIONS = {
    "Clients": {
        "singular": "Client",
        "color": "#DCE9F7",  # powder blue
        "fields": [
            "id",
            "name",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "city",
            "state",
            "zip_code",
            "country",
            "phone_number",
        ],
        "auto": ["id"],
        "required": [
            "name",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "country",
            "phone_number",
        ],
        "list_fields": ["id", "name"],
        "sortable": True,
        "search_hint": "Search Client name",
    },
    "Airlines": {
        "singular": "Airline",
        "color": "#DDEFE0",  # mint green
        "fields": ["id", "company_name"],
        "auto": ["id"],
        "required": ["company_name"],
        "list_fields": ["id", "company_name"],
        "sortable": True,
        "search_hint": "Search Company name",
    },
    "Flights": {
        "singular": "Flight",
        "color": "#F6E7CE",  # warm sand
        "fields": ["client_id", "airline_id", "date", "start_city", "end_city"],
        "auto": [],  # Flights have no system ID; the link IDs are user-chosen.
        "required": ["client_id", "airline_id", "date", "start_city", "end_city"],
        # Shown as name dropdowns but stored as the referenced section's ID;
        # ``label`` renames the field in the UI.
        "references": {
            "client_id": {"section": "Clients", "display": "name", "label": "Client"},
            "airline_id": {
                "section": "Airlines",
                "display": "company_name",
                "label": "Airline",
            },
        },
        # "date" is entered as Y/M/D + HH:MM and reassembled into a stored ISO string.
        "datetime_field": "date",
        "list_fields": ["client_id", "airline_id", "date"],
        "sortable": True,  # Date sorts chronologically as an ISO string.
        "search_hint": "Search company or client name",
    },
}

SECTION_ORDER = ["Clients", "Airlines", "Flights"]


def _darken(hex_color, factor):
    """Return ``hex_color`` scaled toward black by ``factor`` (0..1)."""
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _label_for(key):
    """Turn a snake_case data key into a display label (``zip_code`` -> ``Zip Code``)."""
    return " ".join(
        "ID" if part == "id" else part.capitalize() for part in key.split("_")
    )

# Proportional widths (sidebar | list | detail), held on resize via uniform.
COLUMN_WEIGHTS = {"sidebar": 20, "list": 38, "detail": 42}


class RecordManagerApp(tk.Tk):
    """The main window: sidebar navigation + list + detail/edit panel."""

    def __init__(self):
        super().__init__()
        self.title("Travel Agent - Record Management System")
        self.geometry("960x560")
        self.minsize(820, 460)

        # Use the 'clam' ttk theme on all platforms. macOS's native 'aqua' theme
        # ignores background colours on ttk frames/labels (leaving the section
        # tints grey); 'clam' honours them, so colours render consistently
        # across macOS, Windows and Linux.
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.current_section = None
        # Records per section, held in memory (empty until persistence is wired).
        self.section_records = {name: [] for name in SECTIONS}
        self.current_records = []
        # Rows currently shown (differs from current_records when a search filters).
        self.displayed_records = []
        # field -> (widget, var, border_frame).
        self.detail_entries = {}
        # field -> {"to_id": {name: id}, "to_display": {id: name}} for Flight dropdowns.
        self.ref_index = {}
        # Required-field labels, so the trailing "*" tracks the red border.
        self.detail_labels = {}
        self.dt_labels = {}
        # Composite date/time parts: part -> (widget, var, border). Empty off Flights.
        self.dt = {}
        # A record is shown (vs blank); the Edit button only appears when one is.
        self._record_shown = False
        self.sort_field = None
        self.sort_ascending = True
        self._search_job = None  # pending debounced search (after id), or None
        self._search_hint = ""
        self._placeholder_active = False
        self.editing = False

        self._build_body()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start on the welcome panel; dismissed on the first selection.
        self._show_welcome()

    # -- Layout construction ------------------------------------------------

    def _build_body(self):
        """Sidebar on the left; to its right a full-width header bar above a
        list | details two-column area."""
        body = ttk.Frame(self)
        body.pack(side="top", fill="both", expand=True)

        # Top level: sidebar | content.
        body.columnconfigure(0, weight=COLUMN_WEIGHTS["sidebar"], uniform="cols")
        body.columnconfigure(
            1,
            weight=COLUMN_WEIGHTS["list"] + COLUMN_WEIGHTS["detail"],
            uniform="cols",
        )
        body.rowconfigure(0, weight=1)

        self._build_sidebar(body)

        # Content: a full-width header row (0) over a list | details row (1).
        content = ttk.Frame(body)
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=0)  # header: natural height
        content.rowconfigure(1, weight=1)  # panels: expand

        self._build_header(content)

        self.two_col = ttk.Frame(content)
        self.two_col.grid(row=1, column=0, sticky="nsew")
        self.two_col.columnconfigure(0, weight=COLUMN_WEIGHTS["list"], uniform="lr")
        self.two_col.columnconfigure(1, weight=COLUMN_WEIGHTS["detail"], uniform="lr")
        self.two_col.rowconfigure(0, weight=1)

        self._build_list_panel(self.two_col)
        self._build_detail_panel(self.two_col)
        self._build_welcome(content)

    def _build_header(self, parent):
        """Full-width bar above the panels: section name, search, Clear, New."""
        header = self.header_panel = ttk.Frame(parent, padding=(10, 10, 10, 6))
        header.grid(row=0, column=0, sticky="ew")

        self.list_header = ttk.Label(
            header, text="", font=("Segoe UI", 15, "bold")
        )
        self.list_header.pack(side="left", anchor="w")

        # Pack New from the right so the search entry fills the middle;
        # left->right result: section name | search (expanding) | New.
        self.new_button = ttk.Button(header, text="New", command=self.on_new)
        self.new_button.pack(side="right", padx=(6, 0))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._schedule_search())
        self.search_entry = ttk.Entry(header, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(12, 0))
        self._search_fg = self.search_entry.cget("foreground")  # for placeholder
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

    def _build_sidebar(self, parent):
        """Left column: header, coloured section buttons, auto-save hint."""
        sidebar = ttk.Frame(parent, padding=10)
        sidebar.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            sidebar, text="Travel Records", font=("Segoe UI", 15, "bold")
        ).pack(side="top", anchor="w", pady=(0, 8))

        # Coloured section buttons as tk.Label, not tk.Button/ttk.Button: only
        # classic tk widgets honour `bg` on macOS's Aqua, and Label does so on
        # every OS. They're already flat, so a Label looks the same as the flat
        # button did. Hover/press/click are wired via the bindings below.
        self.nav_buttons = {}
        for name in SECTION_ORDER:
            base = SECTIONS[name]["color"]
            hover = _darken(base, 0.93)
            pressed = _darken(base, 0.85)
            btn = tk.Label(
                sidebar,
                text=name,
                font=("Segoe UI", 12),
                bg=base,
                fg="black",
                cursor="hand2",
            )
            btn.pack(side="top", fill="x", pady=2, ipady=8)
            btn.bind("<Enter>", lambda e, b=btn, c=hover: b.configure(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=base: b.configure(bg=c))
            btn.bind("<ButtonPress-1>", lambda e, b=btn, c=pressed: b.configure(bg=c))
            btn.bind(
                "<ButtonRelease-1>",
                lambda e, b=btn, c=hover, n=name: (
                    b.configure(bg=c), self.select_section(n)),
            )
            self.nav_buttons[name] = btn

        ttk.Label(
            sidebar,
            text="Data auto-saves on exit",
            foreground="grey",
            font=("Segoe UI", 8),
            wraplength=140,
        ).pack(side="bottom", anchor="w")

    def _build_list_panel(self, parent):
        """Bottom-left: the records list (Treeview) for the selected section."""
        middle = self.middle_panel = ttk.Frame(parent, padding=(10, 0, 10, 10))
        middle.grid(row=0, column=0, sticky="nsew")

        # Treeview so the list can show column headings; columns are set per
        # section in _populate_list.
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
        right = self.right_panel = ttk.Frame(parent, padding=(10, 0, 10, 10))
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right, text="Details", font=("Segoe UI", 15, "bold")).pack(
            side="top", anchor="w", pady=(0, 6)
        )

        self.fields_frame = ttk.Frame(right)
        self.fields_frame.pack(side="top", fill="both", expand=True)

        # time_hint and required_legend are shown only while editing (_set_editing).
        self.time_hint = ttk.Label(
            right,
            text="Time uses the 24-hour clock (HH 00-23, MM 00-59)",
            foreground="grey",
            font=("Segoe UI", 8),
        )
        self.required_legend = ttk.Label(
            right,
            text="*  Required field",
            foreground=BORDER_ERROR,
            font=("Segoe UI", 8),
        )

        buttons = ttk.Frame(right)
        buttons.pack(side="bottom", fill="x", pady=(8, 0))

        self.edit_button = ttk.Button(buttons, text="Edit", command=self.on_edit)
        self.delete_button = ttk.Button(
            buttons, text="Delete", command=self.on_delete
        )
        self.save_button = ttk.Button(buttons, text="Save", command=self.on_save)
        self.cancel_button = ttk.Button(
            buttons, text="Cancel", command=self.on_cancel
        )

        # Footer buttons are packed per state (View / Edit / New) in _set_editing.

    def _build_welcome(self, parent):
        """Welcome panel shown on launch, covering the list + detail columns.

        Dismissed the first time the user picks a section (see select_section)
        and does not return for the rest of the session.
        """
        credits = [  # sorted by surname
            "Kovakina, Svetlana",
            "Mekwunye, Victor",
            "Nguyen, Khanh Ngoc",
            "Onat, Yagiz",
            "Sirin, Kerem",
        ]

        self.welcome_panel = ttk.Frame(parent, padding=20)
        self.welcome_panel.grid(row=0, column=0, rowspan=2, sticky="nsew")

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

        ttk.Label(
            self.welcome_panel,
            text="Credits: " + "  •  ".join(credits),
            foreground="grey",
            font=("Segoe UI", 8),
            wraplength=520,
            justify="center",
        ).pack(side="bottom")

    def _show_welcome(self):
        """Show the welcome panel, covering the header + list/detail panels."""
        self.header_panel.grid_remove()
        self.two_col.grid_remove()
        self.welcome_panel.grid()

    def _hide_welcome(self):
        """Hide the welcome panel and restore the header + list/detail panels."""
        self.welcome_panel.grid_remove()
        self.header_panel.grid()
        self.two_col.grid()

    # -- Detail field rendering --------------------------------------------

    def _build_ref_index(self, section):
        """Map each reference field's IDs to display names and back.

        Lets Flight dropdowns show client/airline names while the record keeps
        the ID. Reads from the in-memory records of the referenced section.
        """
        self.ref_index = {}
        for field, ref in SECTIONS[section].get("references", {}).items():
            to_id, to_display = {}, {}
            for record in self.section_records[ref["section"]]:
                display = str(record.get(ref["display"], ""))
                rec_id = record.get("id")
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

        # The composite date/time field spans two rows, so track the row here.
        row = 0
        for field in SECTIONS[section]["fields"]:
            if field == datetime_field:
                row = self._render_datetime_rows(row, field in required)
                continue

            base_label = references[field]["label"] if field in references else _label_for(field)
            label = ttk.Label(self.fields_frame, text=f"{base_label}:")
            label.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
            if field in required:
                self.detail_labels[field] = (label, base_label)

            border = tk.Frame(self.fields_frame, background=BORDER_NORMAL)
            border.grid(row=row, column=1, sticky="ew", pady=2)
            var = tk.StringVar()

            if field in references:
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

            var.trace_add("write", lambda *_: self._validate_required())
            self.detail_entries[field] = (widget, var, border)
            row += 1

        self.fields_frame.columnconfigure(1, weight=1)

    def _bordered(self, parent, widget_factory):
        """Wrap a sub-widget in a border frame; return (widget, var, border)."""
        border = tk.Frame(parent, background=BORDER_NORMAL)
        var = tk.StringVar()
        widget = widget_factory(border, var)
        widget.pack(padx=1, pady=1)
        var.trace_add("write", lambda *_: self._validate_required())
        return widget, var, border

    def _render_datetime_rows(self, row, required):
        """Render the Date (Y/M/D dropdowns) and Time (HH:MM) rows.

        Returns the next free grid row and populates ``self.dt`` with the five
        parts, reassembled in _datetime_value().
        """
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
        for key in ("year", "month", "day"):
            self.dt[key][2].pack(side="left", padx=(0, 4))
        # Valid day count depends on the chosen year+month.
        self.dt["year"][1].trace_add("write", lambda *_: self._update_days())
        self.dt["month"][1].trace_add("write", lambda *_: self._update_days())
        self._update_days()

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
        """Reassemble the parts into ``YYYY-MM-DDTHH:MM``, or None if incomplete."""
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
        """Show a record in the detail panel (or blank it when record is None).

        Reference fields translate the stored ID to its display name.
        """
        self._record_shown = record is not None
        for field, (widget, var, _) in self.detail_entries.items():
            if record is None:
                var.set("")
            elif field in self.ref_index:
                var.set(self.ref_index[field]["to_display"].get(record.get(field), ""))
            else:
                var.set(str(record.get(field, "")))
        if self.dt:
            datetime_field = SECTIONS[self.current_section]["datetime_field"]
            self._set_datetime(None if record is None else record.get(datetime_field))
        self._set_editing(False)

    def _field_state(self, field, editing):
        """Return the widget state for a field in the given mode.

        Dropdowns use readonly/disabled (readonly is still selectable); text
        fields use normal/readonly; system-assigned fields stay read-only.
        """
        if field in SECTIONS[self.current_section]["auto"]:
            return "readonly"
        if field in self.ref_index:
            return "readonly" if editing else "disabled"
        return "normal" if editing else "readonly"

    def _set_editing(self, editing):
        """Toggle the detail panel between read-only and editable."""
        self.editing = editing
        for field, (widget, _, _) in self.detail_entries.items():
            widget.configure(state=self._field_state(field, editing))
        for key, (widget, _, _) in self.dt.items():
            if key in ("hour", "minute"):
                widget.configure(state="normal" if editing else "readonly")
            else:
                widget.configure(state="readonly" if editing else "disabled")

        # Footer buttons: clear all four, then show the set for this state.
        for button in (self.edit_button, self.delete_button,
                       self.save_button, self.cancel_button):
            button.pack_forget()

        if editing:
            if self.dt:
                self.time_hint.pack(side="top", anchor="w", pady=(6, 0))
            self.required_legend.pack(side="top", anchor="w", pady=(2, 0))
            # Edit / New: Cancel + Save right-aligned, Save rightmost.
            self.save_button.pack(side="right")
            self.cancel_button.pack(side="right", padx=(0, 6))
            self.new_button.configure(state="disabled")
            self._validate_required()
        else:
            self.time_hint.pack_forget()
            self.required_legend.pack_forget()
            # View: Delete far-left, Edit far-right -- only when a record is shown.
            if self._record_shown:
                self.delete_button.pack(side="left")
                self.edit_button.pack(side="right")
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
        """Flag empty required fields red (with a '*') and gate the Save button.

        Runs only while editing.
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

        # Composite date/time: flag each empty/invalid part and require a valid
        # reassembled value.
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
        self._hide_welcome()  # no-op after the first selection

        self.current_section = section
        singular = SECTIONS[section]["singular"]
        self.list_header.configure(text=section)
        self.new_button.configure(text=f"New {singular}")

        if SECTIONS[section].get("sortable"):
            self.sort_field = SECTIONS[section]["list_fields"][0]
            self.sort_ascending = True

        self._search_hint = SECTIONS[section]["search_hint"]
        self._show_placeholder()

        self._render_fields(section)
        self.current_records = self.section_records[section]
        self._populate_list(self.current_records)
        self._show_record(None)
        self._apply_section_color(section)

    def _apply_section_color(self, section):
        """Tint the list + detail panels with the section's pastel colour.

        The panels' ttk frames/labels share two styles (Panel.TFrame /
        Panel.TLabel), so recolouring those styles retints everything at once.
        Input fields (Treeview, Entry, Combobox) keep their default look.
        """
        color = SECTIONS[section].get("color")
        if not color:
            return
        style = ttk.Style()
        style.configure("Panel.TFrame", background=color)
        style.configure("Panel.TLabel", background=color)
        for panel in (self.header_panel, self.middle_panel, self.right_panel):
            self._tint_subtree(panel)

    def _tint_subtree(self, widget):
        """Assign the Panel styles to ttk frames/labels in a widget subtree."""
        cls = widget.winfo_class()
        if cls == "TFrame":
            widget.configure(style="Panel.TFrame")
        elif cls == "TLabel":
            widget.configure(style="Panel.TLabel")
        for child in widget.winfo_children():
            self._tint_subtree(child)

    def _populate_list(self, records):
        """Fill the list with ``records``; each row's iid is its index.

        Columns/headings come from the section's list_fields; sortable sections
        get an arrow on the active column and clickable headers.
        """
        fields = SECTIONS[self.current_section]["list_fields"]
        sortable = SECTIONS[self.current_section].get("sortable", False)
        rows = self._sorted(records) if sortable else list(records)

        self.tree["columns"] = fields
        for field in fields:
            label = _label_for(field)
            if sortable:
                if field == self.sort_field:
                    arrow = SORT_ASCENDING if self.sort_ascending else SORT_DESCENDING
                    heading_text = f"{label} {arrow}"
                else:
                    heading_text = label
                self.tree.heading(
                    field, text=heading_text,
                    command=lambda f=field: self.on_sort(f),
                )
            else:
                self.tree.heading(field, text=label, command="")
            # ID columns are fixed-width and sized to fit the heading + arrow;
            # others stretch to absorb the leftover width.
            is_id = field == "id" or field.endswith("_id")
            id_width = max(70, len(label) * 8 + 40)
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
        """Sort by the current field/direction (strings case-insensitive)."""
        def key(record):
            value = record.get(self.sort_field, "")
            return value.lower() if isinstance(value, str) else value

        return sorted(records, key=key, reverse=not self.sort_ascending)

    def on_sort(self, field):
        """Header click: toggle the active column's direction, or switch column."""
        if self.sort_field == field:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_field = field
            self.sort_ascending = True
        # Rebuild, keeping any active search filter.
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
        """Debounce live search so rapid typing triggers a single filter run."""
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(200, self._run_search)

    def _run_search(self):
        self._search_job = None
        self.on_search()

    def on_search(self):
        """Filter the list by the search box text."""
        # The hint is not a query -- while it shows, show the full list.
        if self._placeholder_active:
            self._populate_list(self.current_records)
            return
        query = self.search_var.get().strip().lower()
        if not query:
            self._populate_list(self.current_records)
            return
        fields = SECTIONS[self.current_section]["fields"]
        matches = [
            r
            for r in self.current_records
            if any(query in self._search_text(r, f) for f in fields)
        ]
        self._populate_list(matches)

    def _search_text(self, record, field):
        """Return a field's searchable text, lower-cased.

        Reference fields match on their resolved name (not the stored ID), so a
        Flight can be found by company or client name.
        """
        if field in self.ref_index:
            value = self.ref_index[field]["to_display"].get(record.get(field), "")
        else:
            value = record.get(field, "")
        return str(value).lower()

    def on_edit(self):
        """Make the currently shown record editable."""
        self._set_editing(True)

    def _flight_dependents(self, record):
        """Return Flights that reference this Client/Airline record by its ID."""
        ref_field = {"Clients": "client_id", "Airlines": "airline_id"}.get(
            self.current_section
        )
        if not ref_field:
            return []
        rec_id = record.get("id")
        return [
            f for f in self.section_records["Flights"]
            if f.get(ref_field) == rec_id
        ]

    def on_delete(self):
        """Delete the currently shown record (View mode only), with confirmation.

        Blocks deletion of a Client/Airline still referenced by a Flight.
        TODO: persist the deletion through RecordStore (#7/#8).
        """
        if not self._record_shown:
            return
        selection = self.tree.selection()
        if not selection:
            return
        record = self.displayed_records[int(selection[0])]
        singular = SECTIONS[self.current_section]["singular"]

        dependents = self._flight_dependents(record)
        if dependents:
            messagebox.showerror(
                "Cannot delete",
                f"This {singular} is referenced by {len(dependents)} "
                "flight(s). Remove or reassign those flights first.",
            )
            return

        if not messagebox.askyesno(
            "Confirm delete",
            f"Delete this {singular}? This cannot be undone.",
        ):
            return

        records = self.section_records[self.current_section]
        if record in records:
            records.remove(record)
        self.tree.selection_remove(selection)
        self._populate_list(self.current_records)
        self._show_record(None)

    def _field_value(self, field):
        """Return a field's value as the record stores it.

        Reference dropdowns map the shown name back to its ID, and the composite
        date/time collapses to its ISO string -- so the data structure is
        unchanged regardless of how the field is displayed.
        """
        if self.dt and field == SECTIONS[self.current_section].get("datetime_field"):
            return self._datetime_value()
        _, var, _ = self.detail_entries[field]
        value = var.get()
        if field in self.ref_index:
            return self.ref_index[field]["to_id"].get(value)
        return value

    def on_save(self):
        """Exit edit mode (Save is only clickable once required fields are valid).

        TODO: wire to the data layer -- build the record via
        ``{f: self._field_value(f) for f in fields}`` and persist through
        RecordStore. Nothing is written to disk yet.
        """
        self._set_editing(False)

    def on_cancel(self):
        """Discard edits and return to view mode."""
        selection = self.tree.selection()
        record = self.displayed_records[int(selection[0])] if selection else None
        self._show_record(record)

    def _next_id(self):
        """Return the next auto-assigned ID (one past the highest, or 0)."""
        ids = [
            r["id"]
            for r in self.current_records
            if isinstance(r.get("id"), int)
        ]
        return max(ids) + 1 if ids else 0

    def on_new(self):
        """Open a blank, editable record; ID is pre-filled and read-only.

        TODO: wire to the data layer -- on save, create the record via the
        section's factory (which sets the record's type) and add it to the
        shared store.
        """
        self.tree.selection_remove(self.tree.selection())
        self._show_record(None)
        if "id" in self.detail_entries:
            self.detail_entries["id"][1].set(str(self._next_id()))
        self._set_editing(True)

    def on_close(self):
        """Close the window.

        TODO: wire to the data layer -- call RecordStore.save() here so the
        records are written to JSONL on exit.
        """
        # save_records()  # <- to be connected to the store
        self.destroy()


def main():
    RecordManagerApp().mainloop()


if __name__ == "__main__":
    main()
