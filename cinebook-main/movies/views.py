from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, Movie, Theatre, Showtime
from .serializers import (
    GenreSerializer, MovieListSerializer, MovieDetailSerializer,
    TheatreSerializer, ShowtimeSerializer,
)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.filter(is_active=True).prefetch_related('genres')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language', 'genres']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'rating', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        return MovieDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class TheatreViewSet(viewsets.ModelViewSet):
    queryset = Theatre.objects.prefetch_related('screens')
    serializer_class = TheatreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ShowtimeViewSet(viewsets.ModelViewSet):
    serializer_class = ShowtimeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movie', 'screen__theatre', 'is_active']
    ordering_fields = ['start_time']

    def get_queryset(self):
        qs = Showtime.objects.filter(is_active=True).select_related(
            'movie', 'screen', 'screen__theatre'
        )
        movie_id = self.kwargs.get('movie_pk')
        if movie_id:
            qs = qs.filter(movie_id=movie_id)
        return qs

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
