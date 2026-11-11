## Browser layer

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Name is at most 100 characters | Browser | Typed a very long name in the Name box on `/join` | The box stopped accepting characters at 100 (`maxlength="100"`) |

## Flask layer (requests sent with curl, skipping the form)

The ticket count was the same before and after every request.

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Name, Student ID and service are all required and valid | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=" -d "id_number=abc" -d "service_id=999"` | `HTTP/1.1 400 BAD REQUEST`, nothing saved |
| Student ID must look like 2023-0001 | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Test" -d "id_number=12345" -d "service_id=1"` | `HTTP/1.1 400 BAD REQUEST`, nothing saved |
| Name is at most 100 characters | Flask | PowerShell: `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=$('A'*200)" -d "id_number=2023-0001" -d "service_id=1"` | `HTTP/1.1 400 BAD REQUEST`, nothing saved |
| A switched-off service is treated like a missing one | Flask | Unticked Active on a service, then `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Test" -d "id_number=2023-0001" -d "service_id=<that id>"` | `HTTP/1.1 400 BAD REQUEST`, nothing saved |

## Database layer (statements typed directly in psql, skipping Flask)

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Ticket needs a real service | Database (FOREIGN KEY) | `INSERT INTO tickets (student_id, service_id) VALUES (1, 999);` | `ERROR:  insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey"` |
| Status must be an allowed value | Database (CHECK) | `UPDATE tickets SET status = 'lost' WHERE id = (SELECT min(id) FROM tickets);` | `ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_status"` |
| Student ID must match the format | Database (CHECK) | `INSERT INTO students (id_number, name) VALUES ('abc', 'Bad');` | `ERROR:  new row for relation "students" violates check constraint "ck_students_id_number"` |
| Service names are unique | Database (UNIQUE) | `INSERT INTO services (name) VALUES ((SELECT name FROM services LIMIT 1));` | `ERROR:  duplicate key value violates unique constraint "services_name_key"` |
| A student can have only one waiting or called ticket | Database (UNIQUE partial index) | Copied an active ticket with `INSERT INTO tickets (student_id, service_id) SELECT student_id, service_id FROM tickets WHERE status IN ('waiting', 'called') LIMIT 1;` | `ERROR:  duplicate key value violates unique constraint "uq_tickets_one_active_per_student"` |
| Student name cannot be empty | Database (NOT NULL) | `INSERT INTO students (id_number, name) VALUES ('2099-0001', NULL);` | `ERROR:  null value in column "name" of relation "students" violates not-null constraint` |
| Service name is at most 80 characters | Database (column length) | `INSERT INTO services (name) VALUES (repeat('x', 81));` | `ERROR:  value too long for type character varying(80)` |
| A service with tickets cannot be deleted | Database (ON DELETE RESTRICT) | `DELETE FROM services WHERE id = (SELECT service_id FROM tickets LIMIT 1);` | `ERROR:  update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets"` |
| Defaults are filled in by the database | Database (DEFAULT) | `INSERT INTO tickets (student_id, service_id) VALUES (<new student id>, <service id>) RETURNING id, status, created_at;` | A row came back with `status = waiting` and `created_at` set to the current time |

## SQL injection check

`git grep -nE "f.(SELECT|INSERT|UPDATE|DELETE)" -- "*.py"` printed nothing. All queries use SQLAlchemy (`db.select(...)`, `filter_by(...)`), which sends values separately from the SQL.