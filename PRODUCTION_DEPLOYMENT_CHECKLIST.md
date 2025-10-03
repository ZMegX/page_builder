# 🚀 Production Deployment Checklist

## ✅ REQUIRED BEFORE PRODUCTION

### 1. Remove Test URLs and Views

#### A. Remove Test URLs from `page_builder/urls.py`
**DELETE these lines:**
```python
# Error page testing URLs (MUST be before catch-all patterns)
# TODO: Remove these before production deployment!
path('error-pages-test/', user_views.error_pages_test, name='error_pages_test'),
path('test-400/', user_views.test_400, name='test_400'),
path('test-403/', user_views.test_403, name='test_403'),
path('test-404/', user_views.test_404, name='test_404'),
path('test-500/', user_views.test_500, name='test_500'),
```

#### B. Remove Test Views from `users/views.py`
**DELETE these functions:**
```python
def error_pages_test(request):
    """Test suite dashboard for error pages"""
    return render(request, 'error_pages/error_pages_test.html')

def test_400(request):
    """Test view for 400 Bad Request error"""
    raise SuspiciousOperation("This is a test 400 error")

def test_403(request):
    """Test view for 403 Forbidden error"""
    raise PermissionDenied("This is a test 403 error")

def test_404(request):
    """Test view for 404 Not Found error"""
    raise Http404("This is a test 404 error")

def test_500(request):
    """Test view for 500 Server Error"""
    raise Exception("This is a test 500 error")
```

#### C. Remove Test Template (Optional)
**DELETE file:**
- `users/templates/error_pages/error_pages_test.html`

This file is not security-sensitive, but removing it saves space.

---

### 2. Remove Debug Logging

#### A. From `users/views_restaurant.py`
**REMOVE the print statement:**
```python
# Remove this line:
print(f"DEBUG - Status counts: Pending={pending_count}, In Progress={in_progress_count}, Completed={completed_count}, Cancelled={cancelled_count}")
```

#### B. From `users/templates/users/restaurant_orders_list.html`
**REMOVE console.log statements** (if any exist in JavaScript sections)

---

### 3. Configure Django Settings (`page_builder/settings.py`)

#### A. Set DEBUG to False
```python
# CRITICAL: Must be False in production
DEBUG = False
```

#### B. Configure ALLOWED_HOSTS
```python
# Add your actual domain(s)
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'your-server-ip',  # Optional: for IP access
]
```

#### C. Configure SECRET_KEY
```python
# NEVER commit your real secret key to version control!
# Use environment variable:
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Or use python-decouple or django-environ
```

#### D. Database Configuration
```python
# Use production database (not SQLite for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

#### E. Static Files Configuration
```python
# Collect static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# If using CDN or cloud storage (e.g., AWS S3, Cloudinary):
# Configure accordingly
```

#### F. Security Settings
```python
# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Other security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This copies all static files to `STATIC_ROOT` for serving in production.

---

### 5. Run Database Migrations

```bash
# Make sure all migrations are applied
python manage.py migrate

# Check for any pending migrations
python manage.py showmigrations
```

---

### 6. Test Error Pages in Production Mode

#### A. With DEBUG=False, test actual errors:
```bash
# Start server
python manage.py runserver

# Test error pages by triggering real errors:
# - Visit a non-existent page → Should show custom 404
# - Try accessing forbidden resource → Should show custom 403
# - Create a code error temporarily → Should show custom 500
```

#### B. Verify error handlers are working:
- Error pages should render with your custom templates
- No sensitive debug information should be visible
- All links and buttons should work

---

### 7. Environment Variables Setup

Create a `.env` file (do NOT commit this):
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

Add to `.gitignore`:
```
.env
*.env
.env.*
```

---

### 8. Security Audit

#### A. Check for exposed secrets:
```bash
# Search for potential secrets in code
grep -r "SECRET_KEY\s*=\s*['\"]" . --exclude-dir=venv --exclude-dir=staticfiles
grep -r "PASSWORD\s*=\s*['\"]" . --exclude-dir=venv --exclude-dir=staticfiles
```

#### B. Review dependencies for vulnerabilities:
```bash
pip install safety
safety check
```

#### C. Run Django security checks:
```bash
python manage.py check --deploy
```

---

### 9. Setup Logging

Configure proper logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django_errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

Create logs directory:
```bash
mkdir logs
touch logs/.gitkeep
```

Add to `.gitignore`:
```
logs/*.log
```

---

### 10. Configure Web Server

#### Option A: Nginx + Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn page_builder.wsgi:application --bind 0.0.0.0:8000
```

#### Option B: Apache + mod_wsgi
Configure Apache with your WSGI file.

#### Option C: Cloud Platform (Heroku, AWS, DigitalOcean, etc.)
Follow platform-specific deployment guides.

---

## 📋 QUICK PRE-DEPLOYMENT CHECKLIST

Before you deploy, verify:

- [ ] **DEBUG = False** in settings.py
- [ ] **SECRET_KEY** from environment variable (not hardcoded)
- [ ] **ALLOWED_HOSTS** configured with your domain(s)
- [ ] **Test URLs removed** from page_builder/urls.py
- [ ] **Test views removed** from users/views.py
- [ ] **Debug logging removed** from views_restaurant.py
- [ ] **Database configured** for production (PostgreSQL, MySQL, etc.)
- [ ] **Static files collected** (`collectstatic`)
- [ ] **Migrations applied** (`migrate`)
- [ ] **Error pages tested** with DEBUG=False
- [ ] **Security settings enabled** (SSL, HSTS, secure cookies)
- [ ] **Environment variables** configured
- [ ] **Sensitive data** not in version control (.env in .gitignore)
- [ ] **Security audit passed** (`python manage.py check --deploy`)
- [ ] **Dependencies updated** and vulnerability-free
- [ ] **Logging configured** for production
- [ ] **Backup strategy** in place for database
- [ ] **Monitoring/alerting** set up (optional but recommended)

---

## 🔒 SECURITY BEST PRACTICES

1. **Never commit secrets** to version control
2. **Use HTTPS** in production (SSL certificate)
3. **Regular security updates** for Django and dependencies
4. **Database backups** scheduled regularly
5. **Rate limiting** for forms and API endpoints
6. **CSRF protection** enabled (Django default)
7. **SQL injection protection** (use ORM, not raw SQL)
8. **XSS protection** (escape user input, use Django templates)
9. **Monitor error logs** for suspicious activity
10. **Use strong passwords** for admin accounts

---

## 📚 USEFUL COMMANDS

```bash
# Check deployment readiness
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (for new production database)
python manage.py createsuperuser

# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated
```

---

## 🆘 TROUBLESHOOTING

### Error pages not showing:
- Verify DEBUG=False
- Check ALLOWED_HOSTS includes your domain
- Verify error handlers are registered in urls.py
- Check template paths are correct

### Static files not loading:
- Run `collectstatic` again
- Verify STATIC_ROOT and STATIC_URL settings
- Check web server configuration for static files
- Verify file permissions

### Database connection errors:
- Check database credentials in environment variables
- Verify database server is running
- Check firewall rules allow connection
- Test connection with database client

---

## 📞 POST-DEPLOYMENT

After deployment:
1. **Test all major features** on production site
2. **Monitor error logs** for first 24-48 hours
3. **Check performance** (page load times, database queries)
4. **Verify SSL certificate** is working
5. **Test mobile responsiveness**
6. **Verify email sending** (if applicable)
7. **Check payment processing** (if applicable)
8. **Setup monitoring** (e.g., Sentry, New Relic)

---

## 🎯 SUMMARY

**IMMEDIATE ACTIONS (Before Production):**
1. Remove test URLs from `page_builder/urls.py`
2. Remove test views from `users/views.py`
3. Remove debug print from `users/views_restaurant.py`
4. Set `DEBUG = False`
5. Configure `ALLOWED_HOSTS`
6. Use environment variables for secrets
7. Run `collectstatic`
8. Test with `python manage.py check --deploy`

**Good luck with your deployment! 🚀**
