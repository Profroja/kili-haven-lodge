from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login_api, name='login_api'),
    path('room-types/', views.room_types, name='room_types'),
    
    # Booking Management API endpoints
    path('bookings/<str:booking_id>/', views.get_booking_details, name='get_booking_details'),
    path('bookings/<str:booking_id>/checkout/', views.checkout_booking, name='checkout_booking'),
    path('bookings/<str:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<str:booking_id>/status/', views.get_booking_status, name='get_booking_status'),
]
