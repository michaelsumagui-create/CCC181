"""CCC181 Week 2: RegisTrak starter app

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import re
from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

SERVICES = [
    {"id": 1, "name": "Transcript of Records"},
    {"id": 2, "name": "Certificate of Enrollment"},
    {"id": 3, "name": "Enrollment / Change of Subjects"},
]

# Each ticket: number, name, id_number, service_id, status
# status is one of: waiting, called, served, no-show
TICKETS = [
    {"number": 1, "name": "Joshua Kenezo", "id_number": "2023-0001", "service_id": 1, "status": "waiting"},
    {"number": 2, "name": "Shasheenah Lumasag", "id_number": "2023-0002", "service_id": 2, "status": "waiting"},
    {"number": 3, "name": "Joash Casino", "id_number": "2023-0003", "service_id": 1, "status": "waiting"},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    # Show an empty form
    return render_template("join.html", services=SERVICES, form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    id_number = form.get("id_number", "").strip()
    service_id = form.get("service_id", type=int)

    errors = {}
    if not name:
        errors["name"] = "Please enter your name."
    if not id_number:
        errors["id_number"] = "Please enter your Student ID."
    elif not re.fullmatch(r"\d{4}-\d{4}", id_number):
        errors["id_number"] = "Student ID should look like 2023-0001."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Please choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    # Already in the queue? Send them to their existing ticket
    for t in TICKETS:
        if t["id_number"] == id_number and t["status"] in ("waiting", "called"):
            flash(f"You're already in the queue. Your ticket is #{t['number']}.", "info")
            return redirect(url_for("ticket", ticket_id=t["number"]))

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({
        "number": number,
        "name": name,
        "id_number": id_number,
        "service_id": service_id,
        "status": "waiting",
    })
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # Find the ticket, or show a 404 page if it doesn't exist
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)

    # Count people still waiting ahead of this ticket, for the same service
    ahead = [x for x in TICKETS
             if x["service_id"] == t["service_id"]
             and x["status"] == "waiting"
             and x["number"] < t["number"]]

    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template("ticket.html", ticket=t, service=service, ahead=len(ahead))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)

    ahead = sum(1 for x in TICKETS
                if x["service_id"] == t["service_id"]
                and x["status"] == "waiting" and x["number"] < t["number"])

    # Who is being served now (so the "Now serving" box can update too)
    serving = next((x for x in TICKETS if x["status"] == "called"), None)

    return {
        "status": t["status"],
        "ahead": ahead,
        "now_serving": serving["number"] if serving else None,
    }


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)

    # Only people still waiting or called can leave
    if t["status"] in ("waiting", "called"):
        t["status"] = "no-show"
        flash("You left the queue.", "info")
    else:
        flash("This ticket is already closed.", "warning")
    return redirect(url_for("index"))


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)

    # show one service only
    tickets = TICKETS
    if service_id:
        tickets = [t for t in TICKETS if t["service_id"] == service_id]

    queue = sorted(
        [t for t in tickets if t["status"] in ("waiting", "called")],
        key=lambda t: t["number"],
    )
    done = [t for t in tickets if t["status"] in ("served", "no-show")]

    now_serving = next((t for t in queue if t["status"] == "called"), None)

    names = {s["id"]: s["name"] for s in SERVICES}

    waiting_per_service = {
        s["id"]: sum(1 for t in TICKETS
                     if t["service_id"] == s["id"] and t["status"] == "waiting")
        for s in SERVICES
    }

    return render_template(
        "staff.html",
        queue=queue,
        done=done,
        now_serving=now_serving,
        services=SERVICES,
        names=names,
        selected=service_id,
        waiting_per_service=waiting_per_service,
        waiting_count=sum(1 for t in queue if t["status"] == "waiting"),
        served_count=sum(1 for t in done if t["status"] == "served"),
    )


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)

    # First waiting ticket (lowest number), for the chosen service if filtered
    waiting = sorted(
        [t for t in TICKETS
         if t["status"] == "waiting"
         and (not service_id or t["service_id"] == service_id)],
        key=lambda t: t["number"],
    )
    if waiting:
        waiting[0]["status"] = "called"
        flash(f"Called ticket R-{waiting[0]['number']:03d}.", "success")
    else:
        flash("No one is waiting right now.", "warning")

    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"call": "called", "serve": "served", "no-show": "no-show"}.get(action)
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None or new_status is None:
        abort(404)

    t["status"] = new_status
    flash(f"Ticket R-{ticket_id:03d} marked {new_status}.", "info")
    return redirect(url_for("staff_dashboard"))


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello RegisTrak!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)