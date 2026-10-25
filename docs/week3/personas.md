## Gon, the student waiting

> "There's no need to line up. I can wait or pay in the cashier while virtually lining up in registrar, then come up when it's my turn (interview)"

| | |
| --- | --- |
| **Photo or sketch** | ![Icon of Gon](images/persona1_image.jpg) |
| **Age, role and background** | 22, 4th-year Computer Science student at MSU-IIT |
| **Goals** | 1. Get registrar services quickly. 2. Monitor queue status. 3. Avoid waiting in a long physical line. |
| **Frustrations** | 1. Long waiting times. 2. Uncertainty about when to be served. 3. Missing classes while waiting. |
| **Devices and context** | Uses a smartphone while waiting around campus or attending classes. |
| **Tech comfort** | High — comfortable using mobile apps. |
| **Accessibility needs** | Clear text, simple navigation, and notifications when their turn is near. |

### Scenario

Gon visits the MSU-IIT Registrar's Office to request a withdrawal and adding subject. Instead of waiting in a physical line, Gon opens RegisTrak, selects the needed service, and joins the virtual queue. Gon checks the queue number and estimated status on the phone while waiting nearby. When the turn is approaching, Gon receives a notification and returns to the counter.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Join a queue for registrar services | Join Queue | FR-01 |
| Check queue number and status | My Queue | FR-02 |
| Receive a notification when the turn is near | Notifications | FR-03 |

### What this means for my interface

1. Because Gon want to avoid long physical lines, the interface must make joining a queue easy.
2. Because Gon need to know their position, the app must display real-time queue status clearly.
3. Because Gon may be attending classes, the app must provide timely notifications.


---


## Killua, the Registrar Staff Member

> "I need an organized queue so I can serve students efficiently without confusion. (observation)"

| | |
| --- | --- |
| **Photo or sketch** | ![Icon of Gon](images/persona2_image.jpg) |
| **Age, role and background** | Unknown, registrar office staff member at MSU-IIT. |
| **Goals** | 1. Organize student queues. 2. Call the next student efficiently. 3. Track active and completed requests. |
| **Frustrations** | 1. Crowded waiting areas. 2. Confusion about whose turn is next. 3. Difficulty tracking multiple student requests. |
| **Devices and context** | Uses an office desktop computer while assisting students at the counter. |
| **Tech comfort** | Medium — comfortable using basic office software. |
| **Accessibility needs** | Readable text, clear ticket numbers, and simple controls for managing queues. |

### Scenario

Killua starts the workday by opening RegisTrak on the office computer. Killua views the active queue, calls the next ticket number, and serves the student at the counter. After completing the request, Killua marks the ticket as served and calls the next student. The system keeps the queue organized and reduces confusion.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| View students in the active queue | Queue Dashboard | FR-04 |
| Call the next student | Queue Management | FR-05 |
| Mark a ticket as served | Ticket Details | FR-06 |

### What this means for my interface

1. Because Killua need to manage students quickly, the dashboard must show the active queue clearly.
2. Because Killua must call students in order, the app must provide a simple Call Next button.
3. Because Killua need to track completed requests, the app must allow them to update ticket statuses easily.