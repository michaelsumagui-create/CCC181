## Self-review of Personas and Wireframes

Screen 1 | Frames: join-phone, join-laptop

**Works well:** The form has three inputs and one big "Join Queue" button, so Gon can tell what to do within 5 seconds and finish it with one thumb. The service choices are always visible, so he does not have to remember them. This follows Gon rule 1 (make joining a queue easy).

**Problem:** Error prevention. Nothing shows what happens if the Student ID is blank or wrong, or if Gon joins twice. The labels are also small for Gon, who needs clear text.

**Change (kept):** I am keeping the layout because three fields and one button is the simplest form that meets FR-01. In the HTML I will add error messages (for example, "Please enter your Student ID"), open My Queue if Gon already has a number, and use a large font (16 px or more).

---

Screen 2 | Frames: my-place-phone, my-place-laptop

**Works well:** The queue number (R-027) is the largest thing on screen, followed by the status and "3 people ahead", so Gon sees what he needs at a glance. The alert banner is at the top. This follows Gon rules 2 and 3 (clear real-time status and timely notifications).

**Problem:** Visibility of system status. If Gon loses signal, "Last updated: just now" could be false and he could miss being called. The wireframe also only shows the WAITING state.

**Change (kept):** I am keeping the layout because the order already matches what Gon needs first. In the HTML I will build the CALLED state with the same frame, show the real update time ("Last updated 9:12 AM"), and show "No connection - retrying..." when a refresh fails. I will also show a message if notifications are blocked.

---

Screen 3 | dashboard-phone, dashboard-laptop

**Works well:** "Call next" is the biggest button, top-left on the laptop, and a "Next up" line shows who is called. "Mark served" is right under the current ticket. This follows Killua rules 1, 2 and 3 (clear queue, simple Call Next, easy status updates).

**Problem:** Error prevention. "Mark served" and "Skip / no-show" are next to each other, so a wrong tap is possible. The wireframe also does not show how served tickets look, and Killua needs to track completed requests.

**Change (kept):** I am keeping the layout because the two buttons already look different (filled and outlined). In the HTML, Skip / no-show will ask for confirmation, and served tickets will turn grey but stay in the list so completed requests remain visible.