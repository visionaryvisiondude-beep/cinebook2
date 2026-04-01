# In MIDDLEWARE, add after SecurityMiddleware:
'whitenoise.middleware.WhiteNoiseMiddleware',

# Update ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Add static files config
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Media files — disable on Render free tier (no persistent disk)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Only serve media in development
if DEBUG:
    from django.conf.urls.static import static
# Celery — use eager mode if no Redis (tasks run synchronously, no broker needed)
REDIS_URL = config('REDIS_URL', default=None)

if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    CELERY_TASK_ALWAYS_EAGER = True   # run tasks inline, no broker
    CELERY_TASK_EAGER_PROPAGATES = False
