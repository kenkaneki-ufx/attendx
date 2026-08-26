# AttendX Deployment Guide - Koyeb + Neon

## Overview

This guide will help you deploy AttendX on **Koyeb** (app hosting) with **Neon** (PostgreSQL database) - both with generous free tiers.

---

## Prerequisites

- GitHub account with AttendX repository
- Koyeb account (https://koyeb.com)
- Neon account (https://neon.tech)

---

## Step 1: Set Up Neon PostgreSQL Database

### 1.1 Create Neon Account
1. Go to https://neon.tech and sign up
2. Create a new project
3. Choose the **Free tier** (0.5 GB storage, enough for AttendX)

### 1.2 Get Connection String
1. In Neon dashboard, go to **Connection Details**
2. Copy the connection string (it looks like):
   ```
   postgresql://neondb_owner:xxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. **Save this string** - you'll need it for Koyeb

---

## Step 2: Push Code to GitHub

Make sure your latest code is pushed to GitHub:

```bash
cd Desktop/AttendX
git add .
git commit -m "Add Koyeb deployment config"
git push origin main
```

---

## Step 3: Deploy to Koyeb

### 3.1 Create Koyeb Account
1. Go to https://koyeb.com and sign up (no credit card required)

### 3.2 Create New App
1. Click **Create App**
2. Choose **Docker** as the deployment method
3. Connect your GitHub repository

### 3.3 Configure Build Settings
- **Dockerfile Path**: `./Dockerfile`
- **Build Context**: `.` (root directory)

### 3.4 Configure Service Settings
- **Service Name**: `attendx`
- **Port**: `8000` (or use `$PORT`)

### 3.5 Set Environment Variables
Add these environment variables in Koyeb:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | (from Neon) | Your Neon connection string |
| `DJANGO_SECRET_KEY` | (generate new) | Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | |
| `DJANGO_DEBUG` | `false` | |
| `ALLOWED_HOSTS` | `*` | Or your specific Koyeb domain |
| `PORT` | `8000` | |

### 3.6 Deploy
1. Click **Deploy**
2. Wait for build to complete (2-5 minutes)
3. Your app will be available at: `https://your-app-name.koyeb.app`

---

## Step 4: Run Initial Commands

After deployment, you need to run migrations and create a superuser.

### 4.1 Access Koyeb Shell
1. Go to your service in Koyeb dashboard
2. Click **Shell** tab
3. Run the following commands:

```bash
# Run migrations
python manage.py migrate --noinput

# Create superuser
python manage.py shell -c "
from apps.accounts.models import Faculty
if not Faculty.objects.filter(username='admin').exists():
    Faculty.objects.create_superuser(
        username='admin',
        email='admin@attendx.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        employee_id='ADMIN001'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
```

---

## Step 5: Verify Deployment

1. Visit your Koyeb app URL
2. Go to `/admin/` to access Django admin
3. Login with:
   - Username: `admin`
   - Password: `admin123`

---

## Troubleshooting

### Issue: Database Connection Error
- Verify `DATABASE_URL` is correctly set
- Ensure Neon database is running
- Check that `sslmode=require` is in your connection string

### Issue: Static Files Not Loading
- WhiteNoise should handle this automatically
- Check `STATICFILES_STORAGE` in settings

### Issue: Build Fails
- Check Koyeb build logs for errors
- Ensure all dependencies are in `requirements.txt`

### Issue: App Sleeps After Inactivity
- Koyeb free tier apps sleep after 1 hour of inactivity
- First request after sleep may take 30-60 seconds

---

## Cost Comparison

| Service | Render (Paid) | Koyeb + Neon (Free) |
|---------|---------------|---------------------|
| App Hosting | $7/month | Free (512MB RAM) |
| PostgreSQL | $7/month | Free (0.5GB) |
| **Total** | **$14/month** | **$0/month** |

---

## Next Steps (Optional)

### Set Up Custom Domain
1. In Koyeb dashboard, go to **Settings** > **Domains**
2. Add your custom domain
3. Update DNS records as instructed

### Set Up Auto-Deploy
Koyeb automatically deploys on GitHub push if connected.

### Set Up Monitoring
Koyeb provides built-in metrics and logs in the dashboard.

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `DJANGO_SETTINGS_MODULE` | Settings module path | Yes |
| `DJANGO_DEBUG` | Debug mode (false in production) | Yes |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | Yes |
| `PORT` | Server port (Koyeb sets this) | Auto |
| `REDIS_URL` | Redis URL for caching | Optional |
| `EMAIL_HOST` | SMTP server | Optional |
| `EMAIL_HOST_USER` | SMTP username | Optional |
| `EMAIL_HOST_PASSWORD` | SMTP password | Optional |

---

**Congratulations!** Your AttendX app is now running on Koyeb + Neon for free! 🎉