# Ember SMP Store

Production-style Flask store with player accounts, manual UPI/QR order claims, admin verification, Socket.IO updates, PostgreSQL/SQLAlchemy, audit logs and revenue periods.

## Quick setup

1. Create a virtual environment: `python -m venv .venv` then activate it.
2. Install: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and load it in your shell/deployment platform. Never commit real secrets.
4. Create PostgreSQL database and set `DATABASE_URL`. For quick local testing, omit it to use SQLite.
5. Initialize schema: `flask --app app db init` (first time), `flask --app app db migrate -m "initial"`, `flask --app app db upgrade`.
6. Generate an admin password hash: `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('CHANGE_ME'))"` and put it in `ADMIN_PASSWORD_HASH`.
7. Create the first admin: `flask --app app create-admin` (command is registered by the app).
8. Run: `flask --app app run --debug` or `python app.py`.

## Production

Use PostgreSQL, a long random `SECRET_KEY`, `COOKIE_SECURE=1` behind HTTPS, and a WSGI server compatible with Socket.IO. Example: `gunicorn --worker-class eventlet -w 1 app:app`. Put the app behind Nginx/your platform proxy and configure HTTPS. Run migrations during deploy.

## Branding already configured

- SMP: Ember SMP
- Server IP: `purgee.playwithbao.com:33446`
- Discord: `https://discord.gg/K3TwyZJ9m`
- Uploaded Ember image: `static/images/ember_smp.jpg`
- Uploaded payment QR: `static/images/payment_qr.png`

All can be replaced through environment variables or static image replacement.

## Security notes

Prices/product names/categories are taken only from the server-side catalog. Orders begin as `PENDING`; only authenticated admin routes can approve/reject. Passwords use Werkzeug hashing. CSRF, HttpOnly/SameSite sessions, login rate limiting, ORM queries and server-side authorization are enabled. Never treat the Next button as proof of payment.
# Ember_SMP_Store
