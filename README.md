# Record Management System

>decided to keep a few notes in readme for the future report

## Changelog

### Record IDs switched to UUID

Record ids (`Client`, `Airline`, `Flight`) are now auto-generated `uuid4` strings instead of integers:

- Every record's `id` is generated automatically on creation (`str(uuid.uuid4())`)
- `Flight` previously had no `id` field of its own; it now gets one, consistent with `Client` and `Airline`.
- Since `Flight.client_id` and `Flight.airline_id` reference `Client.id` / `Airline.id`


**Why UUID over alternatives:** other options considered were a utility function generating a random integer, or assigning ids based on list index. Those approaches can work for a simple project, but they're more prone to bugs — random integers need a uniqueness check to avoid collisions, and index-based ids shift or collide once records are deleted or reordered. Python's built-in `uuid4()` is a well-tested, standard-library solution that guarantees uniqueness, 
