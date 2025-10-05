from django.urls import path
from . import views
from . import report_views

urlpatterns = [
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('sales/', views.manager_sales_view, name='manager_sales'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('rooms/edit-individual/<int:room_id>/', views.edit_individual_room, name='edit_individual_room'),
    path('rooms/delete-individual/<int:room_id>/', views.delete_individual_room, name='delete_individual_room'),
    path('users/', views.users_view, name='users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('reservations/', views.reservations_view, name='reservations'),
        path('reservations/<int:reservation_id>/', views.reservation_details, name='reservation_details'),
        path('reservations/by-booking-id/<str:booking_id>/', views.reservation_details_by_booking_id, name='reservation_details_by_booking_id'),
        path('reservations/by-booking-id/<str:booking_id>/checkout/', views.checkout_reservation_by_booking_id, name='checkout_reservation_by_booking_id'),
        path('reservations/<int:reservation_id>/checkin/', views.checkin_existing_reservation, name='checkin_existing_reservation'),
        path('reservations/<int:reservation_id>/rooms/', views.get_available_rooms, name='get_available_rooms'),
        path('reservations/<int:reservation_id>/confirm/', views.confirm_reservation, name='confirm_reservation'),
        path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
        path('checkin/', views.checkin_view, name='checkin'),
        path('checkin/process/', views.process_checkin, name='process_checkin'),
        path('rooms/type/<int:room_type_id>/rooms/', views.get_rooms_for_type, name='get_rooms_for_type'),
        path('rooms/type/<int:room_type_id>/all-rooms/', views.get_all_rooms_for_type, name='get_all_rooms_for_type'),
    path('rooms-management/', views.rooms_management_view, name='rooms_management'),
    
    # Report URLs
    path('reports/checkin/', report_views.generate_checkin_report, name='generate_checkin_report'),
    path('reports/sales/', report_views.generate_sales_report, name='generate_sales_report'),
    path('reports/reservations/', report_views.generate_reservations_report, name='generate_reservations_report'),
    
    # Report Template URLs
    path('reports/checkin/template/', report_views.checkin_report_template, name='checkin_report_template'),
    path('reports/sales/template/', report_views.sales_report_template, name='sales_report_template'),
    path('reports/reservations/template/', report_views.reservations_report_template, name='reservations_report_template'),
    
    # PDF Download URLs
    path('reports/checkin/pdf/', report_views.download_checkin_report_pdf, name='download_checkin_report_pdf'),
    path('reports/reservations/pdf/', report_views.download_reservations_report_pdf, name='download_reservations_report_pdf'),
    path('reports/sales/pdf/', report_views.download_sales_report_pdf, name='download_sales_report_pdf'),
]
