# AttendX: QR Code Attendance System

**Scan. Verify. Attend.**

A modern QR Code-based Attendance Management System designed for educational institutions.

---

## Features

| Feature | Description |
|---------|-------------|
| Dynamic QR Codes | Auto-expiring tokens regenerated every 60 seconds |
| Real-time Attendance | Live tracking during lectures |
| Automatic Absence | Students not scanned marked absent when lecture ends |
| Analytics Dashboard | Charts, reports, and insights |
| Role-based Access | Faculty, Admin, Student roles |
| Export Reports | PDF, Excel, CSV formats |
| Dark Mode | Toggle dark/light theme with OLED-friendly pure black |
| Multi-Theme Colors | 5 accent colors: Indigo, Rose, Emerald, Amber, Cyan |
| Student Portal | Public attendance lookup by roll number |
| Email Alerts | Low attendance notifications |

---

## Tech Stack

- **Backend**: Python 3.10+, Django 5.2 LTS
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript, Glass Morphism UI
- **Database**: SQLite (Development), MySQL (Production)
- **Libraries**: qrcode, Pillow, Chart.js, ReportLab

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AttendX.git
cd AttendX

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create admin superuser
python manage.py seed_data

# Run development server
python manage.py runserver
```

### Login Credentials

- **Admin**: admin / admin123
- **Faculty**: Create via Django admin panel at `/admin/`

---

## Project Structure

```
AttendX/
├── config/                 # Project configuration
│   ├── settings/          # Split settings (base, development, production)
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Business applications
│   ├── accounts/          # Authentication & user management
│   ├── attendance/        # Attendance processing
│   ├── dashboard/         # Faculty dashboard
│   ├── departments/       # Department management
│   ├── branches/          # Branch management
│   ├── sections/          # Section management
│   ├── students/          # Student management
│   ├── subjects/          # Subject management
│   ├── faculty/           # Faculty subject assignments
│   ├── lectures/          # Lecture management
│   ├── qr_codes/          # QR code generation
│   ├── reports/           # Report generation & export
│   ├── analytics/         # Analytics and charts
│   ├── system/            # System settings
│   └── core/              # Core utilities
├── templates/              # Global templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── docs/                   # Documentation
├── manage.py
├── requirements.txt
└── README.md
```

---

## Usage

### Faculty Workflow

1. **Login** at `/accounts/login/`
2. **Start Lecture** - Select subject, section, and period
3. **Generate QR** - Display QR code for students to scan
4. **Monitor Attendance** - View live attendance updates
5. **End Lecture** - Automatically marks absent students
6. **View Reports** - Export daily/weekly reports as PDF or CSV

### Student Workflow

1. **Scan QR Code** - Use any QR scanner app
2. **Enter Roll Number** - Submit attendance
3. **Check Attendance** - Visit `/students/portal/` to view history

### Admin Workflow

1. **Login** at `/admin/`
2. **Manage Users** - Create faculty accounts
3. **Manage Academic Structure** - Departments, branches, sections, subjects
4. **View Audit Logs** - Track system activity

---

## Management Commands

```bash
# Create admin superuser
python manage.py seed_data

# Cleanup expired QR sessions (default: 30 days)
python manage.py cleanup_expired --days 30

# Check low attendance and send alerts
python manage.py check_low_attendance --threshold 75

# Dry run (preview without changes)
python manage.py cleanup_expired --dry-run
python manage.py check_low_attendance --dry-run
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/attendance/scan/<token>/` | GET | Student attendance scan |
| `/qr/api/regenerate/` | POST | Regenerate QR code |
| `/attendance/api/refresh/` | GET | Refresh attendance list |
| `/reports/export/daily/csv/` | GET | Export daily CSV |
| `/reports/export/daily/pdf/` | GET | Export daily PDF |
| `/reports/export/attendance/csv/` | GET | Export all records CSV |
| `/students/portal/` | GET | Student attendance portal |

---

## Testing

```bash
# Run all tests
python manage.py test apps.accounts.tests apps.students.tests apps.lectures.tests apps.attendance.tests

# Run specific app tests
python manage.py test apps.accounts.tests --verbosity=2
```

---

## Security Features

- CSRF Protection
- XSS Prevention
- SQL Injection Prevention (Django ORM)
- Secure QR Token Generation (secrets module)
- Session Management
- Rate Limiting on Login
- Password Hashing (PBKDF2)

---

## Deployment

### Production Settings

```bash
# Set environment variable
export DJANGO_SETTINGS_MODULE=config.settings.production

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Secret key for Django | Required |
| `DJANGO_DEBUG` | Debug mode | False |
| `DB_NAME` | Database name | attendx |
| `DB_USER` | Database user | Required |
| `DB_PASSWORD` | Database password | Required |
| `DB_HOST` | Database host | localhost |
| `EMAIL_HOST` | SMTP host | smtp.gmail.com |
| `QR_EXPIRY_SECONDS` | QR code expiry time | 60 |

---

## License

This project is licensed under the MIT License.

---

**Built with ❤️ for educational institutions**
