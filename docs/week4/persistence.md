# Persistence: The Restart test

1. Create at least **five tickets** across at least two services. Call one, serve one, and let one person leave.

2. 📷 The staff dashboard, and the result of SELECT id, status, service_id, created_at FROM tickets ORDER BY id; in psql.

![Staff dashboard before restart](screenshots/before-restart-dashboard.png)
![SQL before restart](screenshots/before-restart-sql.png)

3. Stop Flask with Ctrl+C. Run docker compose down. Run docker compose ps and see that nothing is running.

4. Run docker compose up -d, wait until docker compose ps says healthy, then start Flask again.

5. 📷 The same dashboard and the same SQL query. Every ticket, status and time must be exactly as before.

![Staff dashboard before restart](screenshots/after-restart-dashboard.png)
![SQL before restart](screenshots/after-restart-sql.png)