from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        'message': 'CineBook API v1.0',
        'endpoints': {
            'auth':      '/api/auth/',
            'movies':    '/api/movies/',
            'theatres':  '/api/movies/theatres/',
            'genres':    '/api/movies/genres/',
            'showtimes': '/api/movies/showtimes/',
            'seats':     '/api/seats/',
            'bookings':  '/api/bookings/',
            'payments':  '/api/payments/',
            'admin':     '/admin/',
        }
    })


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/seats/', include('seats.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
