"""CCC181 Week 2: RegisTrak starter app
 
Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
import re
from datetime import timedelta, timezone
 
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


PH_TIME = timezone(timedelta(hours=8))  # Philippine time has no daylight saving


@app.template_filter("local")
def local_time(value):
    """Show a database time in Philippine time, e.g. Nov 07, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


def people_ahead(t):
    """Count tickets still waiting that joined before t (one line for the whole office)."""
    stmt = (db.select(func.count())
            .select_from(Ticket)
            .where(Ticket.status == "waiting",
                   Ticket.created_at < t.created_at))
    return db.session.scalar(stmt)


def current_called():
    """The ticket being served right now, or None."""
    return db.session.scalar(
        db.select(Ticket).where(Ticket.status == "called").order_by(Ticket.id)
    )


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
    t = db.get_or_404(Ticket, ticket_id)
    ahead = people_ahead(t)

    now_serving = current_called()
    last_served = None
    if now_serving is None:
        last_served = db.session.scalar(
            db.select(Ticket).where(Ticket.status == "served").order_by(Ticket.id.desc())
        )

    return render_template(
        "ticket.html",
        ticket=t,
        service=t.service,
        ahead=ahead,
        position=ordinal(ahead + 1),
        wait=ahead * 4,          # rough guess: 4 minutes per person
        now_serving=now_serving,
        last_served=last_served,
    )


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    serving = current_called()
    return {
        "status": t.status,
        "ahead": people_ahead(t),
        "now_serving": serving.id if serving else None,
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

    def only_this_service(stmt):
        return stmt.where(Ticket.service_id == service_id) if service_id else stmt

    # Waiting and called tickets, in the order they joined
    queue = db.session.scalars(only_this_service(
        db.select(Ticket)
        .where(Ticket.status.in_(["waiting", "called"]))
        .order_by(Ticket.created_at)
    )).all()

    # Finished tickets stay visible (shown in grey)
    done = db.session.scalars(only_this_service(
        db.select(Ticket)
        .where(Ticket.status.in_(["served", "no-show", "left"]))
        .order_by(Ticket.id.desc())
    )).all()

    now_serving = next((t for t in queue if t.status == "called"), None)

    # ★ How many are waiting for each service
    counts = dict(db.session.execute(
        db.select(Ticket.service_id, func.count())
        .where(Ticket.status == "waiting")
        .group_by(Ticket.service_id)
    ).all())
    services = db.session.scalars(db.select(Service).order_by(Service.name)).all()

    return render_template(
        "staff.html",
        queue=queue,
        done=done,
        now_serving=now_serving,
        services=services,
        selected=service_id,
        waiting_per_service={s.id: counts.get(s.id, 0) for s in services},
        waiting_count=sum(1 for t in queue if t.status == "waiting"),
        served_count=sum(1 for t in done if t.status == "served"),
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