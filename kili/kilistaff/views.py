from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Sum
from kilimanager.models import RoomType, Room, Customer, Reservation, CheckIn, CheckOut
import json
import base64
from datetime import datetime
from django.db import transaction

User = get_user_model()

@login_required
def staff_dashboard(request):
    """Staff dashboard view"""
    # Check if user is staff (lodge_attendant)
    if request.user.role == 'manager':
        return redirect('/manager/dashboard/')
    
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%B %Y')
    
    # Get dashboard statistics
    total_rooms = RoomType.objects.count()
    total_reservations = Reservation.objects.count()
    # Count all check-ins (both checked_in and checked_out - they all went through check-in process)
    total_checkins = Reservation.objects.filter(status__in=['checked_in', 'checked_out']).count()
    
    # Yearly statistics
    yearly_reservations = Reservation.objects.filter(
        created_at__year=current_year
    ).count()
    yearly_checkins = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        created_at__year=current_year
    ).count()
    yearly_pending = Reservation.objects.filter(
        status__in=['pending', 'waiting_checkin'],
        created_at__year=current_year
    ).count()
    
    # Monthly statistics
    monthly_reservations = Reservation.objects.filter(
        created_at__year=current_year,
        created_at__month=datetime.now().month
    ).count()
    monthly_checkins = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        created_at__year=current_year,
        created_at__month=datetime.now().month
    ).count()
    current_checked_in = Reservation.objects.filter(
        status='checked_in'
    ).count()
    
    context = {
        'user': request.user,
        'role': 'Staff',
        'current_year': current_year,
        'current_month': current_month,
        'total_rooms': total_rooms,
        'total_reservations': total_reservations,
        'total_checkins': total_checkins,
        'yearly_reservations': yearly_reservations,
        'yearly_checkins': yearly_checkins,
        'yearly_pending': yearly_pending,
        'monthly_reservations': monthly_reservations,
        'monthly_checkins': monthly_checkins,
        'current_checked_in': current_checked_in
    }
    return render(request, 'kilistaff/StaffDashbaord.html', context)

@login_required
def staff_sales_view(request):
    """Staff sales analytics view with month/year filtering"""
    if request.user.role == 'manager':
        return redirect('/manager/sales/')
    
    # Get filter parameters from request
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    # Set current year and month (default to current if not specified)
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Use selected year/month or default to current
    filter_year = int(selected_year) if selected_year else current_year
    filter_month = int(selected_month) if selected_month else current_month
    
    # Get available years for dropdown (last 5 years + current year)
    available_years = list(range(current_year - 4, current_year + 1))
    
    # Calculate monthly sales for selected period
    monthly_sales = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        created_at__year=filter_year,
        created_at__month=filter_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate yearly sales for selected year
    yearly_sales = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        created_at__year=filter_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate total bookings for selected month
    total_bookings = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        created_at__year=filter_year,
        created_at__month=filter_month
    ).count()
    
    # Room type profit breakdown for selected period
    room_type_profits = []
    room_types = RoomType.objects.all()
    
    for room_type in room_types:
        # Get reservations for this room type in selected period
        monthly_reservations = Reservation.objects.filter(
            room_type=room_type,
            status__in=['checked_in', 'checked_out'],
            created_at__year=filter_year,
            created_at__month=filter_month
        )
        
        # Calculate total revenue for this room type
        total_revenue = monthly_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Count number of bookings
        booking_count = monthly_reservations.count()
        
        # Include all room types (even with 0 sales) for complete overview
        room_type_profits.append({
            'room_type': room_type,
            'total_revenue': total_revenue,
            'booking_count': booking_count,
            'average_revenue': total_revenue / booking_count if booking_count > 0 else 0
        })
    
    # Sort by total revenue (highest first)
    room_type_profits.sort(key=lambda x: x['total_revenue'], reverse=True)
    # Format current month display
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    current_month_display = f"{month_names.get(filter_month, 'Unknown')} {filter_year}"
    
    context = {
        'user': request.user,
        'role': 'Staff',
        'current_year': filter_year,
        'current_month': current_month_display,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'total_bookings': total_bookings,
        'room_type_profits': room_type_profits,
        'available_years': available_years,
        'selected_month': selected_month,
        'selected_year': selected_year
    }
    return render(request, 'kilistaff/staffsales.html', context)

@login_required
def staff_rooms_view(request):
    """Staff rooms view - view only room availability"""
    if request.user.role == 'manager':
        return redirect('/manager/rooms/')
    
    # Get all room types with their rooms
    room_types = RoomType.objects.prefetch_related('rooms').all()
    
    context = {
        'user': request.user,
        'role': 'Staff',
        'room_types': room_types
    }
    return render(request, 'kilistaff/staffrooms.html', context)

@login_required
def staff_reservations_view(request):
    """Staff reservations view - view and process reservations"""
    if request.user.role == 'manager':
        return redirect('/manager/reservations/')
    
    # Get pending and waiting check-in reservations
    reservations = Reservation.objects.filter(
        status__in=['pending', 'waiting_checkin']
    ).select_related('customer', 'room_type', 'room').order_by('-created_at')
    
    # Get completed (checked-out) reservations that went through the reservation process
    # These are reservations that were confirmed (have confirmed_at timestamp)
    completed_reservations = Reservation.objects.filter(
        status='checked_out',
        confirmed_at__isnull=False  # Only reservations that went through the confirmation process
    ).select_related('customer', 'room_type', 'room').order_by('-check_out_date')
    
    context = {
        'user': request.user,
        'role': 'Staff',
        'reservations': reservations,
        'completed_reservations': completed_reservations
    }
    return render(request, 'kilistaff/staffreservations.html', context)

# Staff API Views for Reservations
@login_required
@require_http_methods(["GET"])
def staff_reservation_details(request, reservation_id):
    """Get reservation details for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(id=reservation_id)
        
        # Calculate duration
        duration_days = (reservation.check_out_date - reservation.check_in_date).days
        
        data = {
            'status': 'success',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'status': reservation.status,
                'status_display': reservation.get_status_display(),
                'check_in_date': reservation.check_in_date.strftime('%B %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
                'number_of_guests': reservation.number_of_guests,
                'duration_days': duration_days,
                'total_amount': float(reservation.total_amount),
                'special_requests': reservation.special_requests or 'None',
                'purpose_of_visit': reservation.purpose_of_visit or 'Not specified',
                'created_at': reservation.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'customer': {
                    'full_name': reservation.customer.full_name,
                    'email': reservation.customer.email,
                    'phone_number': reservation.customer.phone_number,
                    'nationality': reservation.customer.nationality,
                    'id_type': reservation.customer.id_type,
                    'id_passport_number': reservation.customer.id_passport_number,
                    'id_passport_photo': reservation.customer.id_passport_photo.url if reservation.customer.id_passport_photo else None,
                    'guest_origin': reservation.customer.guest_origin,
                    'is_regular_guest': reservation.customer.is_regular_guest,
                    'total_reservations': reservation.customer.reservations.count()
                },
                'room_type': {
                    'name': reservation.room_type.name,
                    'price_per_day': float(reservation.room_type.price_per_day),
                    'total_rooms': reservation.room_type.total_rooms,
                    'available_rooms': reservation.room_type.available_rooms,
                    'description': reservation.room_type.description
                },
                'room': {
                    'room_name': reservation.room.room_name
                } if reservation.room else None
            }
        }
        return JsonResponse(data)
    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reservation not found'}, status=404)

@login_required
@require_http_methods(["GET"])
def staff_get_available_rooms(request, reservation_id):
    """Get available rooms for a reservation for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related('room_type').get(id=reservation_id)
        
        # Get all active rooms of this type
        all_rooms = Room.objects.filter(
            room_type=reservation.room_type,
            is_active=True
        )
        
        # Filter to only show truly available rooms
        available_rooms = []
        for room in all_rooms:
            # Check if room is available for the specific reservation dates
            if room.is_available_for_dates(reservation.check_in_date, reservation.check_out_date):
                available_rooms.append(room)
        
        rooms_data = []
        for room in available_rooms:
            rooms_data.append({
                'id': room.id,
                'display_name': f"{room.room_name} - {room.room_type.name}"
            })
        
        data = {
            'status': 'success',
            'room_type': reservation.room_type.name,
            'total_rooms': reservation.room_type.total_rooms,
            'available_rooms': rooms_data
        }
        return JsonResponse(data)
    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reservation not found'}, status=404)

@login_required
@require_http_methods(["POST"])
def staff_confirm_reservation(request, reservation_id):
    """Confirm reservation and assign room for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        
        if not room_id:
            return JsonResponse({'status': 'error', 'message': 'Room ID is required'}, status=400)
        
        reservation = Reservation.objects.select_related('room_type', 'room').get(id=reservation_id)
        room = Room.objects.get(id=room_id)
        
        # Check if room is still available by checking for existing reservations
        from django.utils import timezone
        today = timezone.now().date()
        
        # Check if room has any active reservations (current)
        active_reservations = Reservation.objects.filter(
            room=room,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status__in=['waiting_checkin', 'checked_in']
        ).exists()
        
        # Check if room has any future reservations
        future_reservations = Reservation.objects.filter(
            room=room,
            check_in_date__gt=today,
            status__in=['waiting_checkin', 'confirmed']
        ).exists()
        
        if active_reservations or future_reservations:
            return JsonResponse({'status': 'error', 'message': 'Selected room is no longer available'}, status=400)
        
        # Update reservation
        reservation.room = room
        reservation.status = 'waiting_checkin'
        reservation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Reservation confirmed! Room {room.room_name} has been assigned.'
        })
    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reservation not found'}, status=404)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def staff_cancel_reservation(request, reservation_id):
    """Cancel reservation and delete customer data for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related('customer', 'room').get(id=reservation_id)
        customer = reservation.customer
        room = reservation.room
        
        # Delete the reservation and customer
        # The room will automatically become available when the reservation is deleted
        reservation.delete()
        customer.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Reservation and customer data have been deleted successfully.'
        })
    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reservation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def staff_checkin_view(request):
    """Staff check-in page for adding customers and creating reservations"""
    if request.user.role == 'manager':
        return redirect('/manager/checkin/')
    
    # Get available room types and rooms
    room_types = RoomType.objects.filter(is_active=True).prefetch_related('rooms')
    
    # Get all checked-in reservations from all time
    checked_in_reservations = Reservation.objects.filter(
        status='checked_in'
    ).select_related('customer', 'room_type', 'room').order_by('-created_at')
    
    # Get all checked-out reservations from all time
    checked_out_reservations = Reservation.objects.filter(
        status='checked_out'
    ).select_related('customer', 'room_type', 'room').order_by('-check_out_date')
    
    context = {
        'user': request.user,
        'role': 'Staff',
        'room_types': room_types,
        'checked_in_reservations': checked_in_reservations,
        'checked_out_reservations': checked_out_reservations
    }
    return render(request, 'kilistaff/staffcheckin.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def staff_process_checkin(request):
    """Process check-in form submission for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Extract customer data
        customer_data = {
            'email': data.get('email'),
            'full_name': data.get('full_name'),
            'phone_number': data.get('phone_number'),
            'nationality': data.get('nationality'),
            'id_type': data.get('id_type'),
            'other_id_name': data.get('other_id_name', ''),
            'id_passport_number': data.get('id_passport_number'),
            'guest_origin': data.get('guest_origin', ''),
        }
        
        # Extract reservation data
        reservation_data = {
            'room_id': data.get('room_id'),
            'check_in_date': data.get('check_in_date'),
            'check_out_date': data.get('check_out_date'),
            'number_of_guests': data.get('number_of_guests'),
            'purpose_of_visit': data.get('purpose_of_visit', 'leisure'),
            'special_requests': data.get('special_requests', ''),
            'payment_status': data.get('payment_status', 'not_paid'),
            'signature_consent': data.get('signature_consent', ''),
        }
        
        # Validate required fields
        required_fields = ['email', 'full_name', 'phone_number', 'nationality', 
                          'id_type', 'id_passport_number', 'room_id', 
                          'check_in_date', 'check_out_date', 'number_of_guests']
        
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field.replace("_", " ").title()} is required'
                }, status=400)
        
        # Handle ID photo upload if provided
        id_photo = None
        if data.get('id_passport_photo'):
            try:
                # Decode base64 image
                image_data = data['id_passport_photo']
                if image_data.startswith('data:image'):
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_data = base64.b64decode(imgstr)
                    id_photo = ContentFile(image_data, name=f'id_photo_{customer_data["id_passport_number"]}.{ext}')
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error processing ID photo: {str(e)}'
                }, status=400)
        
        # Check if customer already exists
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        
        if not created:
            # Update existing customer
            for key, value in customer_data.items():
                setattr(customer, key, value)
            if id_photo:
                customer.id_passport_photo = id_photo
            customer.save()
        
        # Get the room
        try:
            room = Room.objects.get(id=reservation_data['room_id'])
        except Room.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Selected room not found'
            }, status=400)
        
        # Check if room is available for this customer
        if room.room_status == 'checked_in':
            return JsonResponse({
                'status': 'error',
                'message': f'{room.room_name} is currently checked in and cannot be used'
            }, status=400)
        elif room.room_status == 'reserved':
            # Check if this room is reserved for the same customer
            today = timezone.now().date()
            existing_reservation = Reservation.objects.filter(
                room=room,
                check_in_date__lte=today,
                check_out_date__gte=today,
                status='waiting_checkin'
            ).first()
            
            if existing_reservation and existing_reservation.customer != customer:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{room.room_name} is reserved for another guest'
                }, status=400)
        
        # Create reservation
        reservation = Reservation.objects.create(
            customer=customer,
            room_type=room.room_type,
            room=room,
            check_in_date=datetime.strptime(reservation_data['check_in_date'], '%Y-%m-%d').date(),
            check_out_date=datetime.strptime(reservation_data['check_out_date'], '%Y-%m-%d').date(),
            number_of_guests=int(reservation_data['number_of_guests']),
            purpose_of_visit=reservation_data['purpose_of_visit'],
            special_requests=reservation_data.get('special_requests', ''),
            payment_status=reservation_data['payment_status'],
            status='checked_in'  # Direct to checked_in since this is manual check-in
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Check-in successful! Booking ID: {reservation.booking_id}',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'customer_name': customer.full_name,
                'room_type_name': room.room_type.name,
                'room_name': room.room_name,
                'check_in_date': reservation.check_in_date.strftime('%B %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
                'total_amount': str(reservation.total_amount),
                'payment_status': reservation.get_payment_status_display()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing check-in: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def staff_reservation_details_by_booking_id(request, booking_id):
    """Get detailed reservation information by booking ID for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(booking_id=booking_id)
        
        return JsonResponse({
            'status': 'success',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'status': reservation.status,
                'status_display': reservation.get_status_display(),
                'check_in_date': reservation.check_in_date.strftime('%B %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
                'number_of_guests': reservation.number_of_guests,
                'duration_days': reservation.duration_days,
                'total_amount': str(reservation.total_amount),
                'payment_status': reservation.payment_status,
                'payment_status_display': reservation.get_payment_status_display(),
                'purpose_of_visit': reservation.purpose_of_visit,
                'special_requests': reservation.special_requests,
                'created_at': reservation.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'customer': {
                    'full_name': reservation.customer.full_name,
                    'email': reservation.customer.email,
                    'phone_number': reservation.customer.phone_number,
                    'nationality': reservation.customer.nationality,
                    'id_type': reservation.customer.get_id_type_display(),
                    'id_passport_number': reservation.customer.id_passport_number,
                    'id_passport_photo': reservation.customer.id_passport_photo.url if reservation.customer.id_passport_photo else None,
                    'is_regular_guest': reservation.customer.is_regular_guest,
                    'total_reservations': reservation.customer.reservations.count()
                },
                'room_type': {
                    'name': reservation.room_type.name,
                    'price_per_day': str(reservation.room_type.price_per_day),
                    'total_rooms': reservation.room_type.total_rooms,
                    'available_rooms': reservation.room_type.available_rooms,
                    'description': reservation.room_type.description
                },
                'room': {
                    'room_name': reservation.room.room_name if reservation.room else None
                } if reservation.room else None
            }
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Reservation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching reservation: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def staff_checkout_reservation_by_booking_id(request, booking_id):
    """Check-out a reservation by booking ID for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(booking_id=booking_id)
        
        if reservation.status != 'checked_in':
            return JsonResponse({
                'status': 'error',
                'message': f'Reservation is not checked in. Current status: {reservation.get_status_display()}'
            }, status=400)
        
        # Update reservation status to checked_out
        reservation.status = 'checked_out'
        reservation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Guest {reservation.customer.full_name} has been checked out successfully.',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'customer_name': reservation.customer.full_name,
                'room_name': reservation.room.room_name if reservation.room else 'Not Assigned',
                'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
                'total_amount': str(reservation.total_amount)
            }
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Reservation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing check-out: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def staff_checkin_existing_reservation(request, reservation_id):
    """Check-in an existing reservation (from waiting_checkin to checked_in) for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        # Get the existing reservation
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(id=reservation_id)
        
        if reservation.status != 'waiting_checkin':
            return JsonResponse({
                'status': 'error',
                'message': f'Reservation is not waiting for check-in. Current status: {reservation.get_status_display()}'
            }, status=400)
        
        # Parse the request data
        data = json.loads(request.body)
        
        # Update customer information if provided
        customer = reservation.customer
        if 'email' in data:
            customer.email = data['email']
        if 'full_name' in data:
            customer.full_name = data['full_name']
        if 'phone_number' in data:
            customer.phone_number = data['phone_number']
        if 'nationality' in data:
            customer.nationality = data['nationality']
        if 'id_type' in data:
            customer.id_type = data['id_type']
        if 'id_passport_number' in data:
            customer.id_passport_number = data['id_passport_number']
        if 'other_id_name' in data:
            customer.other_id_name = data['other_id_name']
        
        # Handle ID photo upload if provided
        if 'id_passport_photo' in data and data['id_passport_photo']:
            try:
                # Decode base64 image
                format, imgstr = data['id_passport_photo'].split(';base64,')
                ext = format.split('/')[-1]
                file_data = ContentFile(base64.b64decode(imgstr), name=f'id_photo_{customer.id}.{ext}')
                customer.id_passport_photo = file_data
            except Exception as e:
                print(f"Error processing ID photo: {e}")
        
        customer.save()
        
        # Update reservation information if provided
        if 'check_in_date' in data:
            reservation.check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
        if 'check_out_date' in data:
            reservation.check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
        if 'number_of_guests' in data:
            reservation.number_of_guests = int(data['number_of_guests'])
        if 'purpose_of_visit' in data:
            reservation.purpose_of_visit = data['purpose_of_visit']
        if 'special_requests' in data:
            reservation.special_requests = data['special_requests']
        if 'payment_status' in data:
            reservation.payment_status = data['payment_status']
        
        # Update room assignment if provided
        if 'room_id' in data and data['room_id']:
            try:
                new_room = Room.objects.get(id=data['room_id'])
                # Check if the new room is available for this customer
                if new_room.room_status == 'checked_in':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Selected room "{new_room.room_name}" is currently checked in'
                    }, status=400)
                elif new_room.room_status == 'reserved':
                    # Check if this room is reserved for the same customer
                    today = timezone.now().date()
                    existing_reservation = Reservation.objects.filter(
                        room=new_room,
                        check_in_date__lte=today,
                        check_out_date__gte=today,
                        status='waiting_checkin'
                    ).first()
                    
                    if existing_reservation and existing_reservation.customer != reservation.customer:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Selected room "{new_room.room_name}" is reserved for another guest'
                        }, status=400)
                
                reservation.room = new_room
            except Room.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Selected room does not exist'
                }, status=400)
        
        # Update status to checked_in
        reservation.status = 'checked_in'
        reservation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Check-in successful! Booking ID: {reservation.booking_id}',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'customer_name': customer.full_name,
                'room_type_name': reservation.room_type.name,
                'room_name': reservation.room.room_name if reservation.room else 'Not Assigned',
                'check_in_date': reservation.check_in_date.strftime('%B %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
                'total_amount': str(reservation.total_amount),
                'payment_status': reservation.get_payment_status_display()
            }
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Reservation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing check-in: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def staff_get_rooms_for_type(request, room_type_id):
    """Get available rooms for a specific room type (for check-in) for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        room_type = RoomType.objects.get(id=room_type_id)
        rooms = room_type.rooms.filter(is_active=True)
        
        rooms_data = []
        for room in rooms:
            # Only include available rooms (not reserved or checked in)
            if room.room_status == 'available':
                rooms_data.append({
                    'id': room.id,
                    'room_name': room.room_name,
                    'status': room.room_status
                })
        
        return JsonResponse({
            'status': 'success',
            'room_type': room_type.name,
            'rooms': rooms_data
        })
        
    except RoomType.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Room type not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching rooms: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def staff_get_all_rooms_for_type(request, room_type_id):
    """Get all rooms for a specific room type (for reservations - includes all statuses) for staff"""
    if request.user.role == 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        room_type = RoomType.objects.get(id=room_type_id)
        rooms = room_type.rooms.filter(is_active=True)
        
        rooms_data = []
        for room in rooms:
            rooms_data.append({
                'id': room.id,
                'room_name': room.room_name,
                'status': room.room_status
            })
        
        return JsonResponse({
            'status': 'success',
            'room_type': room_type.name,
            'rooms': rooms_data
        })
        
    except RoomType.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Room type not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching rooms: {str(e)}'
        }, status=500)



@login_required
def reservations_view(request):
    """Reservations management view - shows only pending and waiting check-in reservations"""
    if request.user.role != 'manager':
        return redirect('/staff/dashboard/')
    
    from .models import Reservation, Customer, RoomType
    
    # Only show pending and waiting_checkin reservations
    reservations = Reservation.objects.filter(
        status__in=['pending', 'waiting_checkin']
    ).select_related('customer', 'room_type', 'room').order_by('-created_at')
    
    context = {
        'user': request.user,
        'role': 'Manager',
        'reservations': reservations
    }
    return render(request, 'kilimanager/reservations.html', context)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def reservation_details(request, reservation_id):
    """Get detailed reservation information"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        from .models import Reservation
        reservation = Reservation.objects.select_related('customer', 'room_type', 'room').get(id=reservation_id)
        
        # Calculate duration
        duration_days = (reservation.check_out_date - reservation.check_in_date).days
        
        reservation_data = {
            'id': reservation.id,
            'booking_id': reservation.booking_id,
            'status': reservation.status,
            'status_display': reservation.get_status_display(),
            'check_in_date': reservation.check_in_date.strftime('%B %d, %Y'),
            'check_out_date': reservation.check_out_date.strftime('%B %d, %Y'),
            'number_of_guests': reservation.number_of_guests,
            'total_amount': str(reservation.total_amount),
            'duration_days': duration_days,
            'purpose_of_visit': reservation.get_purpose_of_visit_display(),
            'special_requests': reservation.special_requests or 'None',
            'created_at': reservation.created_at.strftime('%B %d, %Y'),
            'customer': {
                'full_name': reservation.customer.full_name,
                'email': reservation.customer.email,
                'phone_number': reservation.customer.phone_number,
                'nationality': reservation.customer.nationality,
                'id_type': reservation.customer.get_id_type_display(),
                'id_passport_number': reservation.customer.id_passport_number,
                'id_passport_photo': reservation.customer.id_passport_photo.url if reservation.customer.id_passport_photo else None,
                'guest_origin': reservation.customer.guest_origin,
                'is_regular_guest': reservation.customer.is_regular_guest,
                'total_reservations': reservation.customer.total_reservations
            },
                'room_type': {
                    'name': reservation.room_type.name,
                    'price_per_day': str(reservation.room_type.price_per_day),
                    'description': reservation.room_type.description,
                    'total_rooms': reservation.room_type.total_rooms,
                    'available_rooms': reservation.room_type.available_rooms
                },
                'room': {
                    'id': reservation.room.id if reservation.room else None,
                    'room_name': reservation.room.room_name if reservation.room else None
                } if reservation.room else None
        }
        
        return JsonResponse({
            'status': 'success',
            'reservation': reservation_data
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error fetching reservation details: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_available_rooms(request, reservation_id):
    """Get available rooms for a reservation"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related('room_type').get(id=reservation_id)
        
        # Get available rooms for the reservation dates
        available_rooms = reservation.room_type.get_available_rooms_for_dates(
            reservation.check_in_date, 
            reservation.check_out_date
        )
        
        rooms_data = []
        for room in available_rooms:
            rooms_data.append({
                'id': room.id,
                'room_name': room.room_name,
                'display_name': room.room_name
            })
        
        return JsonResponse({
            'status': 'success',
            'room_type': reservation.room_type.name,
            'total_rooms': reservation.room_type.total_rooms,
            'available_rooms': rooms_data
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error fetching available rooms: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def confirm_reservation(request, reservation_id):
    """Confirm reservation with room assignment"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related('room_type').get(id=reservation_id)
        data = json.loads(request.body)
        
        room_id = data.get('room_id')
        
        if not room_id:
            return JsonResponse({
                'message': 'Room selection is required',
                'status': 'error'
            }, status=400)
        
        # Get the room
        try:
            room = Room.objects.get(id=room_id, room_type=reservation.room_type)
        except Room.DoesNotExist:
            return JsonResponse({
                'message': 'Selected room not found',
                'status': 'error'
            }, status=400)
        
        # Check if room is available for the dates
        available_rooms = reservation.room_type.get_available_rooms_for_dates(
            reservation.check_in_date, 
            reservation.check_out_date
        )
        
        if not available_rooms.filter(id=room_id).exists():
            return JsonResponse({
                'message': f'{room.room_name} is not available for the selected dates',
                'status': 'error'
            }, status=400)
        
        # Update reservation
        reservation.room = room
        reservation.status = 'waiting_checkin'
        reservation.confirmed_at = timezone.now()
        reservation.save()
        
        return JsonResponse({
            'message': f'Reservation confirmed successfully! {room.room_name} has been assigned.',
            'status': 'success',
            'reservation': {
                'id': reservation.id,
                'booking_id': reservation.booking_id,
                'room_name': room.room_name,
                'status': reservation.status
            }
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error confirming reservation: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def cancel_reservation(request, reservation_id):
    """Cancel reservation and delete all user data"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related('customer').get(id=reservation_id)
        customer = reservation.customer
        booking_id = reservation.booking_id
        
        # Delete the reservation first
        reservation.delete()
        
        # Delete all customer data
        customer.delete()
        
        return JsonResponse({
            'message': f'Reservation {booking_id} and all customer data have been deleted successfully.',
            'status': 'success'
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
            return JsonResponse({
                'message': f'Error cancelling reservation: {str(e)}',
                'status': 'error'
            }, status=500)

# Room Type CRUD Operations
@login_required
@require_http_methods(["POST"])
def add_room_type(request):
    """Add a new room type"""
    try:
        name = request.POST.get('name')
        price_per_day = request.POST.get('price_per_day')
        description = request.POST.get('description', '')
        total_rooms = request.POST.get('total_rooms')
        is_active = request.POST.get('is_active') == 'on'
        
        if not all([name, price_per_day, total_rooms]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be filled'
            })
        
        room_type = RoomType.objects.create(
            name=name,
            price_per_day=float(price_per_day),
            description=description,
            total_rooms=int(total_rooms),
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Room type added successfully',
            'room_type_id': room_type.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding room type: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def edit_room_type(request):
    """Edit an existing room type"""
    try:
        room_type_id = request.POST.get('room_type_id')
        name = request.POST.get('name')
        price_per_day = request.POST.get('price_per_day')
        description = request.POST.get('description', '')
        total_rooms = request.POST.get('total_rooms')
        is_active = request.POST.get('is_active') == 'on'
        
        if not all([room_type_id, name, price_per_day, total_rooms]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be filled'
            })
        
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Room type not found'
            })
        
        room_type.name = name
        room_type.price_per_day = float(price_per_day)
        room_type.description = description
        room_type.total_rooms = int(total_rooms)
        room_type.is_active = is_active
        room_type.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Room type updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating room type: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def delete_room_type(request, room_type_id):
    """Delete a room type and all its rooms"""
    try:
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Room type not found'
            })
        
        # Check if there are any active reservations for this room type
        active_reservations = Reservation.objects.filter(
            room_type=room_type,
            status__in=['pending', 'confirmed', 'checked_in']
        ).exists()
        
        if active_reservations:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete room type with active reservations'
            })
        
        room_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Room type deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting room type: {str(e)}'
        })

# Room CRUD Operations
@login_required
@require_http_methods(["POST"])
def add_room(request):
    """Add a new room to a room type"""
    try:
        room_type_id = request.POST.get('room_type_id')
        room_name = request.POST.get('room_name')
        # Default to True if not provided (checkbox not checked means True for new rooms)
        is_active = request.POST.get('is_active') != 'false'
        
        if not all([room_type_id, room_name]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be filled'
            })
        
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Room type not found'
            })
        
        room = Room.objects.create(
            room_type=room_type,
            room_name=room_name,
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Room added successfully',
            'room_id': room.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding room: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def edit_room(request):
    """Edit an existing room"""
    try:
        room_id = request.POST.get('room_id')
        room_name = request.POST.get('room_name')
        # Handle checkbox: if not provided, it means unchecked (False), if provided, it means checked (True)
        is_active = request.POST.get('is_active') == 'on'
        
        if not all([room_id, room_name]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be filled'
            })
        
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            })
        
        room.room_name = room_name
        room.is_active = is_active
        room.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Room updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating room: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def delete_room(request, room_id):
    """Delete a room"""
    try:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Room not found'
            })
        
        # Check if room is currently in use
        if room.room_status in ['reserved', 'checked_in']:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete room that is currently in use'
            })
        
        room.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Room deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting room: {str(e)}'
        })
