#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**`requirements.txt`** — add these two lines if not already there:
```
gunicorn>=21.2
whitenoise>=6.6