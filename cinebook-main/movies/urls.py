"""
MOVIES ENDPOINTS
================
GET         /api/movies/                            List all active movies
POST        /api/movies/                            Create movie (admin only)
GET         /api/movies/{id}/                       Movie detail
PUT/PATCH   /api/movies/{id}/                       Update movie (admin only)
DELETE      /api/movies/{id}/                       Delete movie (admin only)
GET         /api/movies/{id}/showtimes/             All showtimes for a specific movie

GET         /api/movies/genres/                     List all genres
POST        /api/movies/genres/                     Create genre (admin only)
GET         /api/movies/genres/{id}/                Genre detail

GET         /api/movies/theatres/                   List all theatres
POST        /api/movies/theatres/                   Create theatre (admin only)
GET         /api/movies/theatres/{id}/              Theatre detail with screens
PUT/PATCH   /api/movies/theatres/{id}/              Update theatre (admin only)
DELETE      /api/movies/theatres/{id}/              Delete theatre (admin only)

GET         /api/movies/showtimes/                  List all showtimes (filter: movie, screen__theatre)
POST        /api/movies/showtimes/                  Create showtime (admin only)
GET         /api/movies/showtimes/{id}/             Showtime detail
PUT/PATCH   /api/movies/showtimes/{id}/             Update showtime (admin only)
DELETE      /api/movies/showtimes/{id}/             Delete showtime (admin only)

Query params for /api/movies/:
  ?search=title           Full-text search on title/description
  ?language=HI            Filter by language code
  ?genres=1               Filter by genre id
  ?ordering=-rating       Sort by rating desc
  ?ordering=release_date  Sort by release date asc

Query params for /api/movies/showtimes/:
  ?movie=1                Filter by movie id
  ?screen__theatre=1      Filter by theatre id
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, MovieViewSet, TheatreViewSet, ShowtimeViewSet

app_name = 'movies'

router = DefaultRouter()
router.register(r'genres',    GenreViewSet,    basename='genre')
router.register(r'theatres',  TheatreViewSet,  basename='theatre')
router.register(r'showtimes', ShowtimeViewSet, basename='showtime')
router.register(r'',          MovieViewSet,    basename='movie')

# Nested: GET /api/movies/{movie_pk}/showtimes/
movie_showtime_list = ShowtimeViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('<int:movie_pk>/showtimes/', movie_showtime_list, name='movie-showtimes'),
    path('', include(router.urls)),
]
