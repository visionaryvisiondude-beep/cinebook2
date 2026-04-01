from django.contrib import admin
from .models import Genre, Movie, Theatre, Screen, Showtime


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'duration_minutes', 'release_date', 'rating', 'is_active')
    list_filter = ('language', 'is_active', 'genres')
    search_fields = ('title',)
    filter_horizontal = ('genres',)


class ScreenInline(admin.TabularInline):
    model = Screen
    extra = 1


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'total_screens')
    search_fields = ('name', 'city')
    inlines = [ScreenInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'screen', 'start_time', 'price_regular', 'price_premium', 'is_active')
    list_filter = ('is_active', 'screen__theatre')
    search_fields = ('movie__title',)
    ordering = ('start_time',)
