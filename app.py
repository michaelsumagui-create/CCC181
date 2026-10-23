"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, render_template, abort

app = Flask(__name__)

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
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html", tickets=TICKETS, services=SERVICES)


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # Find the ticket with this number, or return a 404 if there isn't one.
    return render_template("ticket.html", ticket_id=ticket_id)


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello RegisTrak!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)