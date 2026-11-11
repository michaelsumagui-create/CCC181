# RegisTrak requirements

**Setting:** MSU-IIT Registrar's Office, during office hours (Mon-Fri, 8:00 AM - 5:00 PM)

**People who wait:** Students who need a registrar service, like Gon in [docs/week3/personas.md](week3/personas.md)

**People who serve:** Registrar staff at the counter, like Killua in [docs/week3/personas.md](week3/personas.md)

**Problem statement:** A student who visits the Registrar's Office needs a way to know when it is their turn without standing in a physical line, because they miss classes or lose time waiting in a crowded area.

## Functional requirements

| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 | A student can join the queue for a registrar service by entering their name, Student ID and service. | Must | **Yes** | Built (Week 3) |
| FR-02 | A student can see their ticket number, status and how many people are ahead of them. | Must | **Yes** | Built (Week 3) |
| FR-03 | A student is notified when their turn is near or when they are called. | Should | **Yes** | Later |
| FR-04 | A staff member can see the active queue (waiting and called tickets) in order. | Must | **Yes** | Built (Week 3) |
| FR-05 | A staff member can call the next waiting ticket, for all services or for one service. | Must | **Yes** | Built (Week 3) |
| FR-06 | A staff member can mark a called ticket as served or no-show. | Must | **Yes** | Built (Week 3) |
| FR-07 | A student can leave the queue after joining. | Must | **Yes** | Built (Week 3) |
| FR-08 | A staff member can filter the queue by service. | Should | No | Built (Week 3) |
| FR-09 ★ | The app accepts only a Student ID in the form 2023-0001, and a student who is already waiting is sent to their existing ticket instead of getting a second one. | Must | **Yes** | Built (Week 3) |
| FR-10 ★ | A staff member can see how many people are waiting for each registrar service. | Should | No | Built (Week 3) |
| FR-11 | A staff member can add, rename and switch off a service. | Must | **Yes** | This week |
| FR-12 | A staff member can see completed tickets (served and no-show) in a separate list. | Should | **Yes** | Built (Week 3) |
| FR-13 ★ | A graduating student can join a priority lane that is served first. | Could | **Yes** | Later |
| FR-14 | A student can see an estimated waiting time based on the real average service time. | Won't | **Yes** | Dropped |

## Non-functional requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | No ticket is lost when the server or the database restarts. | Reliability | Must |
| NFR-02 | Two students can never get the same ticket number, even if they join at the same moment. | Data integrity | Must |
| NFR-03 | My place shows a status change within 10 seconds after a staff action, without a reload. | Performance | Should |
| NFR-04 | Every screen scores 90 or higher in the Lighthouse accessibility check. | Accessibility | Must |
| NFR-05 | No password or secret key is stored in the repository. | Security | Must |
| NFR-06 | Buttons and form fields are at least 44 px tall on a phone. | Usability | Should |

## MVP

**MVP:** FR-01, FR-02, FR-04, FR-05, FR-06, FR-07, FR-09, FR-11, NFR-01, NFR-02, NFR-04 and NFR-05.

This is the smallest version that still solves the problem. A student can join, see their place and leave, and staff can call and finish tickets, with every ticket saved in the database.

**Out of scope (this semester):**

- **Payment or cashier integration.** It needs another office's system and is not part of the registrar queue itself.
- **A native mobile app.** The website already works on a phone, and building two apps is too much for one semester.
- **Student login with the MSU-IIT account.** It needs the school's identity system, so students enter their Student ID in the form instead.
- **Online requests with file uploads.** Uploading documents (for example a withdrawal form) is a different workflow from queueing, so students still bring papers to the counter.
- **Appointment booking for a future date.** RegisTrak handles same-day queues only, because booking needs a calendar and limits per day.
- **Several counters or windows with their own queues.** The app has one queue per service, and assigning tickets to Window 1, 2 or 3 would need a larger data design.
- **Reports and charts for the whole office.** Staff only see the live queue and the completed list, because analytics is not needed for the minimum version.

## Check with a real person

| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| A student who experience adding and withdrawing a subject. | "Not necessary na mag butang ug estimation time kay naay mga circumstances na dili accurate kay basin naay unexpected na happenings sa sulod so dili na sya necessary, what necessary is kanang kabalo sya pangkapila sya sa line instead of time estimation" | I dropped the FR-14 from "Later" to Dropped and I kept its ID so I don't use it again. |