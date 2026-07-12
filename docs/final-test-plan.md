# Final Application Test Plan

This document defines the final manual and automated tests for the Record Management System.

The application manages three record types:

- Client
- Airline
- Flight

Records are stored as dictionaries in a shared `RecordStore`, identified by automatically generated UUIDs, and persisted in JSONL.

---

## 1. Test Environments

| Tester | Operating System | Browser | Python Version |
|---|---|---|---|
| Khanh Ngoc Nguyen | macOS | Chrome / Safari | Python 3.14 |
| Victor Mekwunye | Windows | Chrome / Edge | Python 3.14 |

Record the exact operating system, browser, and Python versions used during final testing.

---

## 2. Automated Unit Tests

Verify that unit tests cover the core data and persistence behaviour.

- [ ] `Client` creation and dictionary conversion
- [ ] `Airline` creation and dictionary conversion
- [ ] `Flight` creation and dictionary conversion
- [ ] UUID generation and uniqueness
- [ ] `RecordStore` create logic
- [ ] `RecordStore` search and display logic
- [ ] `RecordStore` update logic
- [ ] `RecordStore` delete logic
- [ ] JSONL load behaviour
- [ ] JSONL save behaviour
- [ ] Save-and-reload round trip
- [ ] Full test command is documented and passes

Record the final test command and result in the README or final report.

---

## 3. Application Startup

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Start the application | The server starts and the application opens without errors. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Load existing records | Saved Client, Airline, and Flight records are displayed correctly. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Start with missing or empty data files | The application opens with empty collections and does not crash. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 4. Client Records

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Create a valid client | The client appears in the list with an automatically generated UUID. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for an existing client | The correct client is displayed. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for a non-existent client | No results are displayed and the application remains responsive. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Update a client | Only the selected client changes and its UUID remains unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Delete a client | The selected client is removed and unrelated records remain unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 5. Airline Records

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Create a valid airline | The airline appears in the list with an automatically generated UUID. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for an existing airline | The correct airline is displayed. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for a non-existent airline | No results are displayed and the application remains responsive. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Update an airline | Only the selected airline changes and its UUID remains unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Delete an airline | The selected airline is removed and unrelated records remain unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 6. Flight Records

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Open the flight form | Client and Airline dropdowns show available records. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Create a valid flight | The flight appears in the list with an automatically generated UUID. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Verify linked records | The selected Client and Airline are stored correctly. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for an existing flight | The correct flight is displayed. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for a non-existent flight | No results are displayed and the application remains responsive. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Update a flight | Only the selected flight changes and its UUID remains unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Delete a flight | The selected flight is removed and unrelated records remain unchanged. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 7. Validation and Negative Tests

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Submit a form with missing required fields | The record is not created and a clear validation message is shown. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Enter invalid data or date format | The input is rejected and the application does not crash. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Search for a non-existent record | No result is returned and the application remains usable. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Update without selecting a record | No record changes and the user is informed that a selection is required. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Delete without selecting a record | No record is deleted and the user is informed that a selection is required. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Enter a very long string | The application remains stable and handles the input appropriately. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Create multiple records | Each record receives a different UUID. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 8. Data Persistence

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Save created records | New records are written to the JSONL file. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Save updated records | Updated values are written correctly. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Save deleted records | Deleted records are absent from the saved data. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Restart the application | Saved records load correctly. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Inspect the data file | The JSONL file remains valid and readable. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 9. Web Interface

| Test | Expected Result | macOS | Windows | Notes |
|---|---|:---:|:---:|---|
| Test all buttons | Each button performs its intended action. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Test dropdowns | Dropdowns contain the correct Client and Airline options. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Test list refresh | Displays update after create, update, and delete operations. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Test validation messages | Messages are clear and understandable. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Test browser layout | Forms and records remain usable in the selected browsers. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Stop and restart the server | The application closes cleanly and saved data remains available. | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 10. Regression Testing

After a bug fix, merge, or feature change, rerun the core tests to confirm that previously working behaviour still works.

- [ ] Application startup and loading
- [ ] Client create, search, update, and delete
- [ ] Airline create, search, update, and delete
- [ ] Flight create, search, update, and delete
- [ ] Dropdown behaviour
- [ ] Validation messages
- [ ] Data saving and reloading
- [ ] Web interface refresh

---

## 11. Final Results

| Test Area | macOS Result | Windows Result | Notes |
|---|:---:|:---:|---|
| Unit tests | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Startup and loading | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Client CRUD | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Airline CRUD | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Flight CRUD | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Validation and negative tests | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Persistence | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Web interface | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |
| Regression testing | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | |

---

## 12. Defects

Log defects as GitHub Issues and record them below.

| Defect ID | Description | Environment | GitHub Issue | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 13. Final Sign-Off

The application is ready for submission when:

- [ ] Critical tests pass on macOS and Windows.
- [ ] The full automated unit test suite passes.
- [ ] High-priority defects are fixed and verified.
- [ ] Remaining limitations are documented.
- [ ] Final test results are available for the report.
