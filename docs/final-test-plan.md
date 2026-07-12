# Final Application Test Plan

This document is intended as a manual testing checklist for the integrated application. It complements the unit tests by verifying end-to-end behaviour from a user's perspective.

---

## 1. Application Startup

- [ ] Application launches successfully.
- [ ] No exceptions are raised on startup.
- [ ] Existing records are loaded correctly.
- [ ] Empty data files are handled without crashing.

---

## 2. Client Records

### Create
- [ ] Create a new client.
- [ ] Client appears in the list immediately.
- [ ] A unique UUID is generated automatically.

### Search
- [ ] Search returns the correct client.
- [ ] Searching for a non-existent client returns no results.

### Update
- [ ] Update client details successfully.
- [ ] Only the selected client is modified.
- [ ] Client UUID remains unchanged.

### Delete
- [ ] Delete the selected client.
- [ ] Client is removed from the list.
- [ ] No other records are affected.

---

## 3. Airline Records

### Create
- [ ] Create a new airline.
- [ ] Airline appears in the list.
- [ ] A unique UUID is generated automatically.

### Search
- [ ] Search returns the correct airline.
- [ ] Searching for a non-existent airline returns no results.

### Update
- [ ] Update airline details successfully.
- [ ] Only the selected airline is modified.
- [ ] Airline UUID remains unchanged.

### Delete
- [ ] Delete the selected airline.
- [ ] Airline is removed from the list.
- [ ] No other records are affected.

---

## 4. Flight Records

### Create
- [ ] Create a new flight.
- [ ] Client and Airline dropdowns display available records.
- [ ] Flight appears in the list.
- [ ] A unique UUID is generated automatically.

### Search
- [ ] Search returns the correct flight.
- [ ] Searching for a non-existent flight returns no results.

### Update
- [ ] Update flight details successfully.
- [ ] Only the selected flight is modified.
- [ ] Flight UUID remains unchanged.

### Delete
- [ ] Delete the selected flight.
- [ ] Flight is removed from the list.
- [ ] No other records are affected.

---

## 5. Data Persistence

- [ ] Save changes.
- [ ] Close the application.
- [ ] Reopen the application.
- [ ] Previously created records are still present.
- [ ] Updated records remain updated.
- [ ] Deleted records remain deleted.

---

## 6. GUI Behaviour

- [ ] All buttons respond correctly.
- [ ] Dropdown menus populate correctly.
- [ ] Lists refresh after create, update and delete.
- [ ] Invalid operations are handled gracefully.
- [ ] The application closes without errors.

---

## 7. Regression Test

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
