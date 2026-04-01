"""
python manage.py seed_demo

Creates sample genres, movies, theatres, screens, seats, and showtimes
so you can test the API immediately after migrations.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from movies.models import Genre, Movie, Theatre, Screen, Showtime
from seats.models import Seat, ShowtimeSeat


GENRES = ['Action', 'Drama', 'Comedy', 'Sci-Fi', 'Thriller', 'Horror', 'Romance']

MOVIES = [
    {
        'title': 'Galactic Drift',
        'description': 'A crew of astronauts fights to survive after their ship is pulled into a rogue black hole.',
        'language': 'EN',
        'duration_minutes': 148,
        'genres': ['Action', 'Sci-Fi'],
        'rating': 8.4,
    },
    {
        'title': 'Mumbaikar',
        'description': 'A slice-of-life drama following three strangers whose lives intertwine over a single monsoon night.',
        'language': 'HI',
        'duration_minutes': 132,
        'genres': ['Drama'],
        'rating': 8.1,
    },
    {
        'title': 'The Last Laugh',
        'description': 'A stand-up comedian\'s comeback tour goes hilariously wrong at every stop.',
        'language': 'EN',
        'duration_minutes': 105,
        'genres': ['Comedy'],
        'rating': 7.6,
    },
]

THEATRES = [
    {'name': 'PVR Cinemas', 'city': 'Pune', 'address': 'Phoenix MarketCity, Nagar Rd'},
    {'name': 'INOX Multiplex', 'city': 'Pune', 'address': 'Bund Garden Road, Camp'},
]


class Command(BaseCommand):
    help = 'Seed the database with demo movies, theatres, and showtimes.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding genres...')
        genre_objs = {}
        for g in GENRES:
            obj, _ = Genre.objects.get_or_create(name=g)
            genre_objs[g] = obj

        self.stdout.write('Seeding movies...')
        movie_objs = []
        for m in MOVIES:
            movie, _ = Movie.objects.get_or_create(
                title=m['title'],
                defaults={
                    'description': m['description'],
                    'language': m['language'],
                    'duration_minutes': m['duration_minutes'],
                    'release_date': timezone.now().date(),
                    'rating': m['rating'],
                    'is_active': True,
                }
            )
            movie.genres.set([genre_objs[g] for g in m['genres']])
            movie_objs.append(movie)

        self.stdout.write('Seeding theatres and screens...')
        for t_data in THEATRES:
            theatre, _ = Theatre.objects.get_or_create(
                name=t_data['name'],
                defaults={
                    'city': t_data['city'],
                    'address': t_data['address'],
                    'total_screens': 2,
                }
            )

            for screen_num in range(1, 3):
                screen, created = Screen.objects.get_or_create(
                    theatre=theatre,
                    name=f'Screen {screen_num}',
                    defaults={'total_seats': 60}
                )

                if created:
                    self._create_seats(screen)

                # Create 3 showtimes per screen per movie for the next 3 days
                for movie in movie_objs:
                    for day_offset in range(3):
                        for hour in [10, 14, 19]:
                            start = timezone.now().replace(
                                hour=hour, minute=0, second=0, microsecond=0
                            ) + timedelta(days=day_offset)
                            showtime, _ = Showtime.objects.get_or_create(
                                screen=screen,
                                start_time=start,
                                defaults={
                                    'movie': movie,
                                    'price_regular': 180,
                                    'price_premium': 280,
                                    'is_active': True,
                                }
                            )
                            # Create ShowtimeSeat rows if missing
                            seats = Seat.objects.filter(screen=screen)
                            for seat in seats:
                                ShowtimeSeat.objects.get_or_create(
                                    showtime=showtime,
                                    seat=seat,
                                    defaults={'status': 'available'}
                                )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))

    def _create_seats(self, screen):
        """Create a 6-row × 10-seat layout with rows A-D regular, E-F premium."""
        rows = ['A', 'B', 'C', 'D', 'E', 'F']
        for row in rows:
            seat_type = 'premium' if row in ('E', 'F') else 'regular'
            for num in range(1, 11):
                Seat.objects.get_or_create(
                    screen=screen, row=row, number=num,
                    defaults={'seat_type': seat_type}
                )
