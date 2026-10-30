RegisTrak is a school registrar queue management designed specifically for registrar office to organize and optimize student service workflows in MSU-IIT. Students join virtual lines and monitor their real-time queue status for registrar services, while staff members call numbers and manage active tickets. To run it, create a virtual environment, run `pip install -r requirements.txt`, then run `flask --app app run --debug` and open http://127.0.0.1:5000 in your browser.

Requirements: [docs/requirements.md](docs/requirements.md)

Note: The staff dashboard is open (no login) for now. Staff login comes in a later week.

★ Staff feature: the “Waiting per service” list on the left counts the waiting people for each service.