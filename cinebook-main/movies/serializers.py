from rest_framework import serializers
from .models import Genre, Movie, Theatre, Screen, Showtime


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id', 'title', 'genres', 'language', 'duration_minutes',
            'release_date', 'poster', 'rating', 'is_active',
        )


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, source='genres'
    )

    class Meta:
        model = Movie
        fields = (
            'id', 'title', 'description', 'genres', 'genre_ids', 'language',
            'duration_minutes', 'release_date', 'poster', 'trailer_url',
            'rating', 'is_active', 'created_at',
        )


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ('id', 'name', 'total_seats')


class TheatreSerializer(serializers.ModelSerializer):
    screens = ScreenSerializer(many=True, read_only=True)

    class Meta:
        model = Theatre
        fields = ('id', 'name', 'address', 'city', 'total_screens', 'screens')


class ShowtimeSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    screen_name = serializers.CharField(source='screen.name', read_only=True)
    theatre_name = serializers.CharField(source='screen.theatre.name', read_only=True)
    end_time = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Showtime
        fields = (
            'id', 'movie', 'movie_title', 'screen', 'screen_name', 'theatre_name',
            'start_time', 'end_time', 'price_regular', 'price_premium',
            'available_seats', 'is_active',
        )

    def get_end_time(self, obj):
        return obj.end_time

    def get_available_seats(self, obj):
        return obj.showtime_seats.filter(status='available').count()
