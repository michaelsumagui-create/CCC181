"""CCC181 Week 2: a "Hello, Flask" starter app.

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

    # 1. Check every field and collect the problems
    errors = {}
    if not name:
        errors["name"] = "Please enter your name."
    if not id_number:
        errors["id_number"] = "Please enter your Student ID."
    elif not re.fullmatch(r"\d{4}-\d{4}", id_number):
        errors["id_number"] = "Student ID should look like 2023-0001."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Please choose a service."

    # 2. If anything is wrong, show the form again with the messages
    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    # 3. Already in the queue? Send them to their existing ticket
    for t in TICKETS:
        if t["id_number"] == id_number and t["status"] in ("waiting", "called"):
            flash(f"You're already in the queue. Your ticket is #{t['number']}.", "info")
            return redirect(url_for("ticket", ticket_id=t["number"]))

    # 4. Everything is fine, so create the ticket
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


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # Find the ticket with this number, or 404 if there isn't one
    found = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if found is None:
        abort(404)
    service = next((s for s in SERVICES if s["id"] == found["service_id"]), None)
    return render_template("ticket.html", ticket=found, service=service)


@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello RegisTrak!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)