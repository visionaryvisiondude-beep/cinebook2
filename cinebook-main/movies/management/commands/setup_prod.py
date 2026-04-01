"""
python manage.py setup_prod

Runs automatically on first deploy:
- Creates superuser from environment variables
- Seeds demo data if database is empty
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = 'Create superuser and seed demo data for production.'

    def handle(self, *args, **options):
        # ── Create superuser ──────────────────────────────────
        email    = config('DJANGO_SUPERUSER_EMAIL',    default='admin@cinebook.com')
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='Admin@1234')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
        else:
            self.stdout.write(f'Superuser already exists: {email}')

        # ── Seed demo data only if DB is empty ────────────────
        from movies.models import Movie
        if Movie.objects.count() == 0:
            self.stdout.write('Seeding demo data...')
            from django.core.management import call_command
            call_command('seed_demo')
        else:
            self.stdout.write('Demo data already present, skipping seed.')
