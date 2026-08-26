# AttendX - Complete User Guide & Tutorial

**Learn how to set up and use the AttendX QR Code Attendance System**

---

## 📚 Table of Contents

1. [Getting Started](#1-getting-started)
2. [Setting Up the Project](#2-setting-up-the-project)
3. [Admin Setup](#3-admin-setup)
4. [Creating Academic Structure](#4-creating-academic-structure)
5. [Adding Faculty Members](#5-adding-faculty-members)
6. [Adding Students](#6-adding-students)
7. [Faculty Workflow](#7-faculty-workflow)
8. [Student Portal](#8-student-portal)
9. [Reports & Analytics](#9-reports--analytics)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Getting Started

### What is AttendX?

AttendX is a modern QR Code-based Attendance Management System that allows:
- **Faculty** to generate QR codes during lectures
- **Students** to scan QR codes to mark their attendance
- **Admins** to manage the entire system

### System Requirements

- Python 3.10 or higher
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Edge)
- (Optional) MySQL for production

---

## 2. Setting Up the Project

### Step 2.1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/AttendX.git

# Navigate to project folder
cd AttendX
```

### Step 2.2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2.3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2.4: Run Migrations

```bash
python manage.py migrate
```

### Step 2.5: Create Initial Data

```bash
python manage.py seed_data
```

This creates:
- Admin superuser: `admin` / `admin123`
- Sample departments, branches, and sections

### Step 2.6: Start the Server

```bash
python manage.py runserver
```

**Server will be running at:** http://localhost:8000

---

## 3. Admin Setup

### Step 3.1: Access Django Admin

1. Open your browser and go to: `http://localhost:8000/admin/`
2. Login with:
   - **Username:** `admin`
   - **Password:** `admin123`

> **Note:** If you used `seed_data` command, departments and sections are already created.

### Step 3.2: Configure Departments

1. In the admin panel, click on **Departments**
2. Click **Add Department**
3. Fill in:
   - **Name:** e.g., "Computer Science Engineering"
   - **Code:** e.g., "CSE"
4. Click **Save**

### Step 3.3: Configure Branches

1. Click on **Branches**
2. Click **Add Branch**
3. Fill in:
   - **Name:** e.g., "Information Technology"
   - **Code:** e.g., "IT"
   - **Department:** Select the department
4. Click **Save**

### Step 3.4: Configure Sections

1. Click on **Sections**
2. Click **Add Section**
3. Fill in:
   - **Name:** e.g., "Section A"
   - **Branch:** Select the branch
   - **Semester:** e.g., "1" to "8"
4. Click **Save**

### Step 3.5: Configure Subjects

1. Click on **Subjects**
2. Click **Add Subject**
3. Fill in:
   - **Name:** e.g., "Data Structures"
   - **Code:** e.g., "CS201"
   - **Department:** Select department
   - **Semester:** e.g., "3"
4. Click **Save**

---

## 4. Creating Academic Structure

### Visual Guide: Academic Hierarchy

```
Department (e.g., CSE)
    └── Branch (e.g., Computer Science)
         └── Section (e.g., Section A)
              └── Subjects (e.g., Data Structures, OS, etc.)
```

### Quick Setup via Admin Panel

**For a complete department setup:**

1. Create Department: "Computer Science Engineering" (CSE)
2. Create Branch: "Computer Science" under CSE
3. Create Sections: "Section A", "Section B" under Computer Science
4. Create Subjects: Multiple subjects under CSE department

---

## 5. Adding Faculty Members

### Method 1: Via Admin Panel

1. Go to: `http://localhost:8001/admin/`
2. Click on **Faculty** (or **Users**)
3. Click **Add Faculty** or **Add User**
4. Fill in the required fields:

| Field | Example |
|-------|---------|
| Username | faculty1 |
| Email | faculty1@college.edu |
| First Name | John |
| Last Name | Smith |
| Employee ID | EMP001 |
| Phone | 9876543210 |
| Department | Computer Science |
| Password | password123 |
| Is Active | ✅ Checked |
| Is Staff | ☐ Unchecked |
| Is Admin | ☐ Unchecked |

5. Click **Save**

### Method 2: Via Faculty Management Page (Admin User)

1. Login as admin at: `http://localhost:8001/accounts/login/`
2. Click **Faculty** in the sidebar
3. Click **Add Faculty** button
4. Fill in the form:
   - **Username:** faculty1
   - **Email:** faculty1@college.edu
   - **First Name:** John
   - **Last Name:** Smith
   - **Employee ID:** EMP001
   - **Phone:** 9876543210
   - **Department:** Select from dropdown
   - **Password:** password123 (minimum 8 characters)
5. Click **Create Faculty**

### Assign Subjects to Faculty

After creating a faculty member, you need to assign them subjects:

1. Go to **Faculty** → **Assignments**
2. Click **Create Assignment**
3. Select:
   - **Faculty:** John Smith
   - **Subject:** Data Structures
   - **Section:** Section A
   - **Academic Year:** 2025-2026
4. Click **Create**

---

## 6. Adding Students

### Method 1: Via Django Admin Panel

1. Login at: `http://localhost:8001/admin/`
2. Click on **Students**
3. Click **Add Student**
4. Fill in the required fields:

| Field | Example |
|-------|---------|
| Registration Number | REG2025001 |
| Roll Number | 22CSE001 |
| First Name | Jane |
| Last Name | Doe |
| Email | jane.doe@student.edu |
| Phone | 9876543211 |
| Section | Section A |
| Password | student123 |
| Is Active | ✅ Checked |

5. Click **Save**

### Adding Student Passwords

Students need passwords to login to the student portal. To set passwords:

1. Go to Django Admin → Students
2. Select a student
3. Set the password in the password field
4. Click **Save**

> **Tip:** Use the same password format for all students (e.g., `student123`) for easier onboarding.

---

## 7. Faculty Workflow

### Step 7.1: Login

1. Go to: `http://localhost:8001/accounts/login/`
2. Enter your **Username** and **Password**
3. Click **Login**

### Step 7.2: View Dashboard

After login, you'll see the **Faculty Dashboard** with:
- Total lectures conducted
- Today's attendance overview
- Quick actions
- Recent activity

### Step 7.3: Start a Lecture

1. Click **Start Lecture** in the sidebar
2. Select:
   - **Subject:** Data Structures
   - **Section:** Section A
   - **Lecture Number:** 1 (Period 1)
3. Click **Start Lecture**

### Step 7.4: Generate QR Code

1. After starting a lecture, click **Generate QR Code**
2. A QR code will be displayed on screen
3. The QR code:
   - Auto-refreshes every 60 seconds
   - Has a visible timer showing expiry
   - Can be manually refreshed if needed

### Step 7.5: Monitor Live Attendance

1. Click **Live Attendance** in the sidebar
2. You'll see:
   - Real-time list of students who scanned
   - Present count vs total students
   - Auto-refresh every 10 seconds

### Step 7.6: End the Lecture

1. Click **End Lecture** on the active lecture page
2. Confirm the action
3. All students who didn't scan will be marked **Absent**

---

## 8. Student Portal

### Public Attendance Lookup (No Login Required)

Students can check attendance without logging in:

1. Go to: `http://localhost:8001/students/portal/`
2. Enter **Roll Number** (e.g., 22CSE001)
3. Click **Check Attendance**
4. View:
   - Total lectures attended
   - Present/Late/Absent counts
   - Attendance percentage
   - Detailed lecture-wise attendance

### Student Login (For Dashboard Access)

1. Go to: `http://localhost:8001/students/login/`
2. Enter:
   - **Roll Number:** 22CSE001
   - **Password:** student123
3. Click **Login**

### Student Dashboard Features

After login, students can see:
- **Attendance Overview:** Present/Late/Absent counts
- **Subject-wise Attendance:** Breakdown by subject
- **Weekly Trend:** Chart showing attendance over time
- **Monthly Trend:** Long-term attendance pattern
- **Recent Lectures:** List of recent lectures attended

---

## 9. Reports & Analytics

### Faculty Reports

1. Click **Reports** in the sidebar
2. Choose report type:
   - **Daily Report:** Today's attendance summary
   - **Weekly Report:** Last 7 days summary
   - **Monthly Report:** Last 30 days summary

### Export Reports

**Export as CSV:**
1. Go to **Reports** → **Daily Report**
2. Click **Export CSV** button
3. File will be downloaded

**Export as PDF:**
1. Go to **Reports** → **Daily Report**
2. Click **Export PDF** button
3. PDF will be generated and downloaded

### Analytics Dashboard

1. Click **Analytics** in the sidebar
2. View:
   - **Overall Statistics:** Total present/late/absent
   - **Weekly Trend Chart:** Bar chart of daily attendance
   - **Subject-wise Chart:** Doughnut chart by subject
   - **Section-wise Chart:** Bar chart by section
   - **Top Students:** Leaderboard of best attendance
   - **Low Attendance Alerts:** Students below 75%

---

## 10. Troubleshooting

### Common Issues & Solutions

#### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001
```

#### Issue: "No active lecture to generate QR for"

**Solution:**
- Make sure you've started a lecture first
- Go to **Start Lecture** and create a new lecture

#### Issue: "Student not found with roll number"

**Solution:**
- Verify the student exists in the database
- Check if the roll number is correct (case-insensitive)
- Ensure the student is marked as **Active**

#### Issue: "Cannot deactivate your own account"

**Solution:**
- This is by design to prevent accidental self-deactivation
- Ask another admin to deactivate accounts

#### Issue: QR code not refreshing

**Solution:**
- Click the **Regenerate QR** button manually
- Check your internet connection
- Refresh the page

---

## Quick Reference Card

### Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Faculty | (created by admin) | (set by admin) |
| Student | (roll number) | (set by admin) |

### Important URLs

| Page | URL |
|------|-----|
| Login (Faculty) | http://localhost:8000/accounts/login/ |
| Login (Student) | http://localhost:8000/students/login/ |
| Student Portal | http://localhost:8000/students/portal/ |
| Admin Panel | http://localhost:8000/admin/ |
| Dashboard | http://localhost:8000/dashboard/ |
| Start Lecture | http://localhost:8000/lectures/start/ |
| Generate QR | http://localhost:8000/qr/generate/ |
| Live Attendance | http://localhost:8000/attendance/live/ |
| Reports | http://localhost:8000/reports/daily/ |
| Analytics | http://localhost:8000/analytics/ |
| Faculty Management | http://localhost:8000/faculty/ |

---

---

## Additional Resources

- **Project README:** See `README.md`
- **License:** MIT License

---

**Last Updated:** August 8, 2026
