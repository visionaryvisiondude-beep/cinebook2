from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']  # add this

    def __str__(self):
        return self.name


class Movie(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'), ('HI', 'Hindi'), ('MR', 'Marathi'),
        ('TA', 'Tamil'), ('TE', 'Telugu'), ('KN', 'Kannada'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    duration_minutes = models.PositiveIntegerField()
    release_date = models.DateField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    trailer_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.title


class Theatre(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    total_screens = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} — {self.city}"


class Screen(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, related_name='screens')
    name = models.CharField(max_length=50)   # e.g. "Screen 1", "Audi 2"
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.theatre.name} / {self.name}"


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='showtimes')
    start_time = models.DateTimeField()
    price_regular = models.DecimalField(max_digits=8, decimal_places=2)
    price_premium = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_time']
        unique_together = ('screen', 'start_time')

    @property
    def end_time(self):
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.movie.duration_minutes)

    def __str__(self):
        return f"{self.movie.title} @ {self.start_time:%d %b %Y %H:%M} — {self.screen}"
