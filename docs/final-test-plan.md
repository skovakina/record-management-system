# Final Application Test Plan

This Test Plan defines the testing strategy, scope, responsibilities, environment, and test cases for the Record Management System developed for a specialist travel agent. 
The system manages three record types:
Client Records
Airline Records
Flight Records
The purpose of this Test Plan is to ensure the system behaves correctly, reliably, and consistently across all required operations: Create, Search, Update, Delete, and Persist.

---
##Testers

- Khanh Ngoc Nguyen (MAC Operating System)
- Victor Mekwunye (Windows Operating System)

##Responsibilities
Execute all test cases

Log defects in GitHub Issues

Verify fixes

Perform regression testing


Maintain test documentation


## 1. Application Startup

- [ ] Application launches successfully.
- [ ] No exceptions are raised on startup.
- [ ] Existing records are loaded correctly.
- [ ] Missing or Empty data files are handled without crashing.

---

## 2. Client Records

### Create
- [ ] Create a new client.
- [ ] Client appears in the list immediately.
- [ ] A unique Integer ID is generated automatically.
- [ ] Validation prevents missing fields.
- [ ] Validation prevents invalid data types.

### Search
- [ ] Search returns the correct client.
- [ ] Searching for a non-existent client returns no results.
- [ ] Search handles empty database

### Update
- [ ] Update client details successfully.
- [ ] Only the selected client is modified.
- [ ] Client UUID remains unchanged.

### Delete
- [ ] Delete the selected client.
- [ ] Client is removed from the list.
- [ ] No other records are affected.
- [ ] Deleting non-existent ID handled gracefully.

---

## 3. Airline Records

### Create
- [ ] Create a new airline.
- [ ] Airline appears in the list.
- [ ] A unique Integer ID is generated automatically.

### Search
- [ ] Search returns the correct airline.
- [ ] Searching for a non-existent airline returns no results.

### Update
- [ ] Update airline details successfully.
- [ ] Only the selected airline is modified.
- [ ] Airline unique Integer ID remains unchanged.

### Delete
- [ ] Delete the selected airline.
- [ ] Airline is removed from the list.
- [ ] No other records are affected.

---

## 4. Flight Records

### Create
- [ ] Create a new flight.
- [ ] Client dropdowns display available records.
- [ ] Airline dropdowns display available records.
- [ ] Flight appears in the list.
- [ ] A unique Integer ID is generated automatically.

### Search
- [ ] Search returns the correct flight.
- [ ] Searching for a non-existent flight returns no results.

### Update
- [ ] Update flight details successfully.
- [ ] Only the selected flight is modified.
- [ ] Flight unique Integer ID remains unchanged.

### Delete
- [ ] Delete the selected flight.
- [ ] Flight is removed from the list.
- [ ] No other records are affected.

---

## 5. Data Persistence

- [ ] Save changes.
- [ ] Close the application.
- [ ] Reopen the application.
- [ ] Created records persist.
- [ ] Updated records persist.
- [ ] Deleted records remain deleted.
- [ ] File format remains valid

---

## 6. GUI Behaviour

- [ ] All buttons respond correctly.
- [ ] Dropdown menus populate correctly.
- [ ] Lists refresh after create, update and delete.
- [ ] Invalid operations are handled gracefully.
- [ ] The application closes without errors.

---
## 7. Negative Test 
- [ ] Create record with missing fields.
- [ ] Create record with invalid data types.
- [ ] Duplicate ID creation.
- [ ] Update non-existent record.
- [ ] Delete non-existent record.
- [ ] Search with invalid input.
- [ ] Enter extremely long strings.
- [ ] Invalid date formats.

## 8. Regression Test

Verify the complete workflow:
- [ ] Create Client
- [ ] Create Airline
- [ ] Create Flight
- [ ] Search records
- [ ] Update records
- [ ] Delete records
- [ ] Save data
- [ ] Restart the application
- [ ] Verify all remaining records are correct

---

## Test Result

| Test Area | Status | Notes |
|-----------|--------|-------|
| Startup | ☐ Pass ☐ Fail | |
| Client | ☐ Pass ☐ Fail | |
| Airline | ☐ Pass ☐ Fail | |
| Flight | ☐ Pass ☐ Fail | |
| Persistence | ☐ Pass ☐ Fail | |
| GUI | ☐ Pass ☐ Fail | |
| Regression | ☐ Pass ☐ Fail | |
| GUI | ☐ Pass ☐ Fail | |
| Regression | ☐ Pass ☐ Fail | |
