# AttendX - Quick Deployment Reference

## 🚀 Deploy to Koyeb + Neon (Free)

### Step 1: Get Database URL from Neon
1. Sign up at https://neon.tech
2. Create project → Copy connection string

### Step 2: Deploy to Koyeb
1. Sign up at https://koyeb.com
2. Create App → Docker → Connect GitHub repo
3. Add environment variables:
   ```
   DATABASE_URL=<your-neon-url>
   DJANGO_SECRET_KEY=<generate-one>
   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_DEBUG=false
   ALLOWED_HOSTS=*
   ```

### Step 3: Run Initial Setup
```bash
# In Koyeb Shell:
python manage.py migrate --noinput
python manage.py createsuperuser
```

### Step 4: Access Your App
- App: `https://your-app.koyeb.app`
- Admin: `https://your-app.koyeb.app/admin/`
- Login: `admin` / `admin123`

---

## 📁 Files Created/Modified

| File | Purpose |
|------|---------|
| `Dockerfile` | Container configuration for Koyeb |
| `.koyeb.yaml` | Koyeb service configuration |
| `DEPLOYMENT-GUIDE.md` | Full deployment guide |
| `QUICK-START.md` | This file |
| `config/settings/production.py` | Updated for Koyeb support |

---

## 🔧 Useful Commands

```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Test locally with Docker
docker build -t attendx .
docker run -p 8000:8000 -e DATABASE_URL=... attendx

# Push to GitHub (auto-deploys)
git add . && git commit -m "Update" && git push
```

---

## 💡 Tips

- Koyeb free tier sleeps after 1 hour of inactivity
- First request after sleep takes 30-60 seconds
- Neon free tier: 0.5 GB storage (plenty for AttendX)
- Both platforms: No credit card required!

---

## 🆘 Need Help?

- Full guide: See `DEPLOYMENT-GUIDE.md`
- Koyeb docs: https://docs.koyeb.com
- Neon docs: https://neon.tech/docs