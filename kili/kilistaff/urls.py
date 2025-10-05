from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # Sales Analytics
    path('sales/', views.staff_sales_view, name='staff_sales'),
    
    # Room Management
    path('rooms/', views.staff_rooms_view, name='staff_rooms'),
    
    # Reservation Management
    path('reservations/', views.staff_reservations_view, name='staff_reservations'),
    path('reservations/<int:reservation_id>/', views.staff_reservation_details, name='staff_reservation_details'),
    path('reservations/<int:reservation_id>/rooms/', views.staff_get_available_rooms, name='staff_get_available_rooms'),
    path('reservations/<int:reservation_id>/confirm/', views.staff_confirm_reservation, name='staff_confirm_reservation'),
    path('reservations/<int:reservation_id>/cancel/', views.staff_cancel_reservation, name='staff_cancel_reservation'),
    
    # Check-in Management
    path('checkin/', views.staff_checkin_view, name='staff_checkin'),
    path('checkin/process/', views.staff_process_checkin, name='staff_process_checkin'),
    path('reservations/by-booking-id/<str:booking_id>/', views.staff_reservation_details_by_booking_id, name='staff_reservation_details_by_booking_id'),
    path('reservations/by-booking-id/<str:booking_id>/checkout/', views.staff_checkout_reservation_by_booking_id, name='staff_checkout_reservation_by_booking_id'),
    path('reservations/<int:reservation_id>/checkin/', views.staff_checkin_existing_reservation, name='staff_checkin_existing_reservation'),
    path('rooms/type/<int:room_type_id>/rooms/', views.staff_get_rooms_for_type, name='staff_get_rooms_for_type'),
    path('rooms/type/<int:room_type_id>/all-rooms/', views.staff_get_all_rooms_for_type, name='staff_get_all_rooms_for_type'),
    
    # Room Type CRUD
    path('rooms/add-room-type/', views.add_room_type, name='add_room_type'),
    path('rooms/edit-room-type/', views.edit_room_type, name='edit_room_type'),
    path('rooms/delete-room-type/<int:room_type_id>/', views.delete_room_type, name='delete_room_type'),
    
    # Room CRUD
    path('rooms/add-room/', views.add_room, name='add_room'),
    path('rooms/edit-room/', views.edit_room, name='edit_room'),
    path('rooms/delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
]
