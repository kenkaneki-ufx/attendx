# AttendX - QR Code Attendance System

A web-based attendance management system using QR codes for easy and accurate attendance tracking.

## 🎯 Features

### For Faculty
- **QR Code Generation** - Generate unique QR codes for each lecture
- **Live Attendance** - See students check in real-time
- **Dashboard** - View attendance statistics and reports
- **Student Management** - Manage student records and sections

### For Students
- **Mobile QR Scanner** - Scan QR codes to mark attendance
- **Attendance Portal** - View attendance history and statistics
- **Subject-wise Reports** - Check attendance per subject

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django (Python) |
| Database | PostgreSQL (Supabase) |
| Frontend | Bootstrap 5 + HTML/CSS |
| QR Codes | qrcode + Pillow |
| Hosting | Render |

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/kenkaneki-ufx/AttendX.git
cd AttendX

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

### Access Points

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Home page |
| `http://localhost:8000/admin/` | Django Admin |
| `http://localhost:8000/faculty/dashboard/` | Faculty Dashboard |
| `http://localhost:8000/students/login/` | Student Login |

## 📱 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Faculty   │────▶│  Generate   │────▶│  Display    │
│   Login     │     │  QR Code    │     │  on Screen  │
└─────────────┘     └─────────────┘     └─────────────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Attendance │◀────│   Verify    │◀────│   Student   │
│  Marked ✓   │     │   & Mark    │     │  Scan QR    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 🗂️ Project Structure

```
AttendX/
├── apps/
│   ├── accounts/      # User authentication
│   ├── attendance/    # Attendance records
│   ├── faculty/       # Faculty management
│   ├── lectures/      # Lecture scheduling
│   ├── qr_codes/      # QR code generation
│   ├── students/      # Student management
│   └── subjects/      # Subject management
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── config/           # Django settings
```

## 🔐 User Roles

| Role | Access |
|------|--------|
| **Admin** | Full access to all features |
| **Faculty** | Generate QR, view attendance, manage lectures |
| **Student** | Scan QR, view own attendance |

## 📊 Database Schema (Simplified)

```
Faculty ──┬── Lecture ──┬── AttendanceRecord
          │            │
Subject ──┘            └── QRCodeSession
                                
Student ──────────────────┘
```

## 🚀 Deployment

The app is deployed on **Render**:
- **URL**: https://attendx.onrender.com
- **Database**: PostgreSQL (Supabase)

## 💡 Future Enhancements

| Feature | Description |
|---------|-------------|
| 📍 **Geofencing** | Location-based attendance verification |
| 📸 **Facial Recognition** | AI-powered student identification |
| 🔔 **Push Notifications** | Real-time attendance alerts |
| 📈 **Advanced Analytics** | Predictive attendance insights |
| 📱 **Mobile App** | Native iOS/Android application |
| 🌐 **Offline Mode** | Work without internet |
| 📧 **Email Reports** | Automated attendance reports |
| 🔄 **Biometric Integration** | Fingerprint/face ID verification |

## 📝 License

MIT License - Free to use for educational purposes

---

**Mini Project** - QR Code Based Attendance System
