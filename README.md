# AttendX — QR Code Attendance System

College mini project. Attendance for lectures, marked by scanning a QR code with your phone — instead of someone calling out sixty names and marking a register.

**Live:** https://attendx.onrender.com (free tier, so it might take a few seconds to wake up on first load)

## How it works

A faculty member starts a lecture from the dashboard. The app generates a QR code that's valid for a short window (60 seconds by default), and it shows up on the screen. Students point their phone camera at it — the code is just a link to `/attendance/scan/<token>/` — and the page marks them present (or late) and tells them the result. On the faculty side the counts update live, so you can watch the room fill in as people scan.

A few things I added because college WiFi is what it is:

- QR tokens expire and can't be reused after the window closes.
- One scan per student per lecture — duplicates are ignored.
- Scanning is rate limited per IP, so nobody scripts the whole class in two seconds.
- A lecture has to actually be in progress for a scan to count.

## Who uses it

- **Admin** — manages faculty, students, sections, subjects and the faculty–subject assignments.
- **Faculty** — dashboard, start/end lectures, generate QR, live attendance, "my subjects", lecture history.
- **Student** — look up their portal by roll number, or log in with roll number + password to scan and see subject-wise attendance and history.

## Tech

Django 5 with SQLite locally (Postgres/Supabase in production), Bootstrap 5 templates, `qrcode` + Pillow for the codes. Served on Render with WhiteNoise handling static files.

## Running it locally

```bash
git clone https://github.com/kenkaneki-ufx/attendx.git
cd AttendX

python -m venv venv
venv\Scripts\activate          # Windows; on Linux/mac: source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000.

There are a couple of seed commands if you want sample AKTU CSE data (departments, branches, sections, subjects):

```bash
python manage.py seedaktu       # run this first
python manage.py seedfaculty
```

### A database gotcha

The repo has a `.env` file whose `DATABASE_URL` points at the Supabase Postgres used by the deployed app. If you're working offline or just want the local SQLite database, comment that line out (or run commands with `DATABASE_URL=`) and Django falls back to `db.sqlite3`.

## Where things live

- `apps/` — one Django app per concern: accounts (faculty login), students, sections, subjects, lectures, attendance, qr_codes, plus departments/branches for the academic hierarchy and small core/common helpers.
- `templates/` — Bootstrap HTML.
- `config/` — settings split into base / development / production.
- Logs go to `logs/django.log` (the folder is created automatically).

The data model basically runs Department → Branch → Section → Student, and faculty are assigned to a subject + section for an academic year. Lectures happen against those assignments, and every QR session belongs to one lecture.

## What I'd add with more time

Geofencing so scanning only works inside the classroom, push notifications when a lecture starts, and maybe a real mobile app instead of phone-camera scanning. The QR-based flow works fine for a demo, though.

MIT licensed.
