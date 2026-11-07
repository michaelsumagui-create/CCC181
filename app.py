"""CCC181 Week 2: RegisTrak starter app
 
Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
import re
 
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
 
from models import Service, Student, Ticket, db
 
load_dotenv()
 
app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"
 
db.init_app(app)
migrate = Migrate(app, db)



def ordinal(n):
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 4 -> 4th ..."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


@app.route("/")
def index():
    return render_template("index.html")


def all_services():
    """Services that are switched on, for the join form."""
    return db.session.scalars(
        db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
    ).all()


@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    id_number = form.get("id_number", "").strip()
    service_id = form.get("service_id", type=int)

    # The service must exist in the database and be switched on
    service = db.session.get(Service, service_id) if service_id else None
    if service is not None and not service.is_active:
        service = None

    errors = {}
    if not name or len(name) > 100:
        errors["name"] = "Please enter your name (up to 100 characters)."
    if not id_number:
        errors["id_number"] = "Please enter your Student ID."
    elif not re.fullmatch(r"[0-9]{4}-[0-9]{4}", id_number):
        errors["id_number"] = "Student ID should look like 2023-0001."
    if service is None:
        errors["service_id"] = "Please choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors=errors), 400

    # Find the student by Student ID
    student = db.session.scalar(db.select(Student).filter_by(id_number=id_number))
    if student is not None:
        # Already waiting or called? Send them to that ticket
        active = db.session.scalar(
            db.select(Ticket).where(
                Ticket.student_id == student.id,
                Ticket.status.in_(("waiting", "called")),
            )
        )
        if active is not None:
            flash(f"You're already in the queue. Your ticket is R-{active.id:03d}.", "info")
            return redirect(url_for("ticket", ticket_id=active.id))
        student.name = name  # the latest name typed wins
    else:
        student = Student(id_number=id_number, name=name)

    ticket = Ticket(student=student, service=service)
    db.session.add(ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is R-{ticket.id:03d}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # Find the ticket, or show a 404 page if it doesn't exist
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)

    # People still waiting ahead of you, for the same service
    ahead = [x for x in TICKETS
             if x["service_id"] == t["service_id"]
             and x["status"] == "waiting"
             and x["number"] < t["number"]]

    service = next(s for s in SERVICES if s["id"] == t["service_id"])

    # Who is being served right now
    now_serving = next((x for x in TICKETS if x["status"] == "called"), None)

    # If nobody is called, show the most recently served ticket instead
    last_served = None
    if not now_serving:
        served = [x for x in TICKETS if x["status"] == "served"]
        last_served = max(served, key=lambda x: x["number"]) if served else None

    return render_template(
        "ticket.html",
        ticket=t,
        service=service,
        ahead=len(ahead),
        position=ordinal(len(ahead) + 1),
        wait=len(ahead) * 4,          # rough guess: 4 minutes per person
        now_serving=now_serving,
        last_served=last_served,
    )


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


@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""
    starting = [
        "Transcript of Records",
        "Certificate of Enrollment",
        "Enrollment / Change of Subjects",
    ]
    for name in starting:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name))
    db.session.commit()
    print("Services are ready.")


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)