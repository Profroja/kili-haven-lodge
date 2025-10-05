from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Sum, Count, Avg
from .models import RoomType, Room, Customer, Reservation, CheckIn, CheckOut
import json
import base64
from datetime import datetime, timedelta
from calendar import monthrange

User = get_user_model()

@login_required
def manager_dashboard(request):
    """Manager dashboard view"""
    # Check if user is a manager
    if request.user.role != 'manager':
        return redirect('/staff/dashboard/')
    
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%B %Y')
    
    # Get dashboard statistics
    from .models import RoomType, Customer, Reservation, CheckIn, CheckOut
    
    total_users = User.objects.count()
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
        'role': 'Manager',
        'current_year': current_year,
        'current_month': current_month,
        'total_users': total_users,
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
    return render(request, 'kilimanager/dashbaord.html', context)

@login_required
def manager_sales_view(request):
    """Manager sales analytics view with month/year filtering"""
    if request.user.role != 'manager':
        return redirect('/staff/sales/')
    
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
        'role': 'Manager',
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
    return render(request, 'kilimanager/sales.html', context)

@login_required
def rooms_view(request):
    """Rooms management view"""
    if request.user.role != 'manager':
        return redirect('/staff/dashboard/')
    
    room_types = RoomType.objects.all().order_by('name')
    
    context = {
        'user': request.user,
        'role': 'Manager',
        'room_types': room_types
    }
    return render(request, 'kilimanager/rooms.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_room(request):
    """Add new room type"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Create new room type
        room_type = RoomType.objects.create(
            name=data.get('name'),
            price_per_day=data.get('price_per_day'),
            total_rooms=data.get('total_rooms'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'message': 'Room type added successfully!',
            'status': 'success',
            'room_type': {
                'id': room_type.id,
                'name': room_type.name,
                'price_per_day': str(room_type.price_per_day),
                'total_rooms': room_type.total_rooms,
                'available_rooms': room_type.available_rooms,
                'is_active': room_type.is_active
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'message': f'Error adding room type: {str(e)}',
            'status': 'error'
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def edit_room(request, room_id):
    """Edit existing room type"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        room_type = RoomType.objects.get(id=room_id)
        data = json.loads(request.body)
        
        # Update room type
        room_type.name = data.get('name', room_type.name)
        room_type.price_per_day = data.get('price_per_day', room_type.price_per_day)
        room_type.total_rooms = data.get('total_rooms', room_type.total_rooms)
        room_type.description = data.get('description', room_type.description)
        room_type.is_active = data.get('is_active', room_type.is_active)
        room_type.save()
        
        return JsonResponse({
            'message': 'Room type updated successfully!',
            'status': 'success',
            'room_type': {
                'id': room_type.id,
                'name': room_type.name,
                'price_per_day': str(room_type.price_per_day),
                'total_rooms': room_type.total_rooms,
                'available_rooms': room_type.available_rooms,
                'is_active': room_type.is_active
            }
        })
        
    except RoomType.DoesNotExist:
        return JsonResponse({
            'message': 'Room type not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error updating room type: {str(e)}',
            'status': 'error'
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_room(request, room_id):
    """Delete room type"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        room_type = RoomType.objects.get(id=room_id)
        room_name = room_type.name
        room_type.delete()
        
        return JsonResponse({
            'message': f'Room type "{room_name}" deleted successfully!',
            'status': 'success'
        })
        
    except RoomType.DoesNotExist:
        return JsonResponse({
            'message': 'Room type not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error deleting room type: {str(e)}',
            'status': 'error'
        }, status=400)

@login_required
def users_view(request):
    """Users management view"""
    if request.user.role != 'manager':
        return redirect('/staff/dashboard/')
    
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'user': request.user,
        'role': 'Manager',
        'users': users
    }
    return render(request, 'kilimanager/users.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_user(request):
    """Add new user"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'role', 'password', 'confirm_password']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'message': f'{field.replace("_", " ").title()} is required',
                    'status': 'error'
                }, status=400)
        
        # Validate password confirmation
        if data.get('password') != data.get('confirm_password'):
            return JsonResponse({
                'message': 'Passwords do not match',
                'status': 'error'
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=data.get('email')).exists():
            return JsonResponse({
                'message': 'Email already exists',
                'status': 'error'
            }, status=400)
        
        # Check if username already exists (using email as username)
        if User.objects.filter(username=data.get('email')).exists():
            return JsonResponse({
                'message': 'Username already exists',
                'status': 'error'
            }, status=400)
        
        # Create new user
        user = User.objects.create(
            username=data.get('email'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            mobile_number=data.get('mobile_number'),
            role=data.get('role'),
            password=make_password(data.get('password')),
            is_active=True
        )
        
        return JsonResponse({
            'message': 'User created successfully!',
            'status': 'success',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile_number': user.mobile_number,
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'message': f'Error creating user: {str(e)}',
            'status': 'error'
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def edit_user(request, user_id):
    """Edit existing user"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'role']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'message': f'{field.replace("_", " ").title()} is required',
                    'status': 'error'
                }, status=400)
        
        # Check if email already exists (excluding current user)
        if User.objects.filter(email=data.get('email')).exclude(id=user_id).exists():
            return JsonResponse({
                'message': 'Email already exists',
                'status': 'error'
            }, status=400)
        
        # Check if username already exists (excluding current user)
        if User.objects.filter(username=data.get('email')).exclude(id=user_id).exists():
            return JsonResponse({
                'message': 'Username already exists',
                'status': 'error'
            }, status=400)
        
        # Update user
        user.username = data.get('email')
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.mobile_number = data.get('mobile_number')
        user.role = data.get('role')
        
        # Update password if provided
        if data.get('password'):
            if data.get('password') != data.get('confirm_password'):
                return JsonResponse({
                    'message': 'Passwords do not match',
                    'status': 'error'
                }, status=400)
            user.password = make_password(data.get('password'))
        
        user.save()
        
        return JsonResponse({
            'message': 'User updated successfully!',
            'status': 'success',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile_number': user.mobile_number,
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'message': 'User not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error updating user: {str(e)}',
            'status': 'error'
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def deactivate_user(request, user_id):
    """Deactivate/Activate user"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deactivating self
        if user.id == request.user.id:
            return JsonResponse({
                'message': 'You cannot deactivate your own account',
                'status': 'error'
            }, status=400)
        
        # Toggle active status
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'activated' if user.is_active else 'deactivated'
        
        return JsonResponse({
            'message': f'User "{user.get_full_name()}" has been {status_text} successfully!',
            'status': 'success',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile_number': user.mobile_number,
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'message': 'User not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error updating user status: {str(e)}',
            'status': 'error'
        }, status=400)

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
    
    # Get completed (checked-out) reservations that went through the reservation process
    # These are reservations that were confirmed (have confirmed_at timestamp)
    completed_reservations = Reservation.objects.filter(
        status='checked_out',
        confirmed_at__isnull=False  # Only reservations that went through the confirmation process
    ).select_related('customer', 'room_type', 'room').order_by('-check_out_date')
    
    context = {
        'user': request.user,
        'role': 'Manager',
        'reservations': reservations,
        'completed_reservations': completed_reservations
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
def rooms_management_view(request):
    """Rooms management view - shows individual rooms"""
    if request.user.role != 'manager':
        return redirect('/staff/dashboard/')
    
    room_types = RoomType.objects.filter(is_active=True).prefetch_related('rooms')
    
    context = {
        'user': request.user,
        'role': 'Manager',
        'room_types': room_types
    }
    return render(request, 'kilimanager/rooms_management.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_room(request):
    """Add new room to a room type"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        data = json.loads(request.body)
        room_type_id = data.get('room_type_id')
        room_name = data.get('room_name')
        
        if not all([room_type_id, room_name]):
            return JsonResponse({
                'message': 'All fields are required',
                'status': 'error'
            }, status=400)
        
        # Get room type
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return JsonResponse({
                'message': 'Room type not found',
                'status': 'error'
            }, status=400)
        
        # Check if room name already exists for this room type
        if Room.objects.filter(room_type=room_type, room_name=room_name).exists():
            return JsonResponse({
                'message': f'Room "{room_name}" already exists for {room_type.name}',
                'status': 'error'
            }, status=400)
        
        # Create room
        room = Room.objects.create(
            room_type=room_type,
            room_name=room_name
        )
        
        return JsonResponse({
            'message': f'Room "{room_name}" added successfully!',
            'status': 'success',
            'room': {
                'id': room.id,
                'room_name': room.room_name,
                'room_type': room.room_type.name
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'message': f'Error adding room: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def edit_individual_room(request, room_id):
    """Edit individual room"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        room = Room.objects.get(id=room_id)
        data = json.loads(request.body)
        
        room_name = data.get('room_name')
        is_active = data.get('is_active', True)
        
        if not room_name:
            return JsonResponse({
                'message': 'Room name is required',
                'status': 'error'
            }, status=400)
        
        # Check if room name already exists for this room type (excluding current room)
        if Room.objects.filter(room_type=room.room_type, room_name=room_name).exclude(id=room_id).exists():
            return JsonResponse({
                'message': f'Room "{room_name}" already exists for {room.room_type.name}',
                'status': 'error'
            }, status=400)
        
        # Update room
        room.room_name = room_name
        room.is_active = is_active
        room.save()
        
        return JsonResponse({
            'message': f'Room "{room_name}" updated successfully!',
            'status': 'success',
            'room': {
                'id': room.id,
                'room_name': room.room_name,
                'is_active': room.is_active
            }
        })
        
    except Room.DoesNotExist:
        return JsonResponse({
            'message': 'Room not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error updating room: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_individual_room(request, room_id):
    """Delete individual room"""
    if request.user.role != 'manager':
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        room = Room.objects.get(id=room_id)
        room_name = room.room_name
        
        # Check if room has any active reservations
        active_reservations = Reservation.objects.filter(
            room=room,
            status__in=['confirmed', 'checked_in']
        ).exists()
        
        if active_reservations:
            return JsonResponse({
                'message': f'Cannot delete room "{room_name}" as it has active reservations',
                'status': 'error'
            }, status=400)
        
        # Delete room
        room.delete()
        
        return JsonResponse({
            'message': f'Room "{room_name}" deleted successfully!',
            'status': 'success'
        })
        
    except Room.DoesNotExist:
        return JsonResponse({
            'message': 'Room not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error deleting room: {str(e)}',
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

@login_required
def checkin_view(request):
    """Check-in page for staff to add customers and create reservations"""
    if request.user.role not in ['manager', 'staff']:
        return redirect('/staff/dashboard/')
    
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
        'role': 'Manager' if request.user.role == 'manager' else 'Staff',
        'room_types': room_types,
        'checked_in_reservations': checked_in_reservations,
        'checked_out_reservations': checked_out_reservations
    }
    return render(request, 'kilimanager/checkin.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def process_checkin(request):
    """Process check-in form submission"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
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
                    'message': f'{field.replace("_", " ").title()} is required',
                    'status': 'error'
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
                    'message': f'Error processing ID photo: {str(e)}',
                    'status': 'error'
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
                'message': 'Selected room not found',
                'status': 'error'
            }, status=400)
        
        # Check if room is available for this customer
        if room.room_status == 'checked_in':
            return JsonResponse({
                'message': f'{room.room_name} is currently checked in and cannot be used',
                'status': 'error'
            }, status=400)
        elif room.room_status == 'reserved':
            # Check if this room is reserved for the same customer
            from django.utils import timezone
            today = timezone.now().date()
            existing_reservation = Reservation.objects.filter(
                room=room,
                check_in_date__lte=today,
                check_out_date__gte=today,
                status='waiting_checkin'
            ).first()
            
            if existing_reservation and existing_reservation.customer != customer:
                return JsonResponse({
                    'message': f'{room.room_name} is reserved for another guest',
                    'status': 'error'
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
            'message': f'Check-in successful! Booking ID: {reservation.booking_id}',
            'status': 'success',
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
                'message': f'Error processing check-in: {str(e)}',
                'status': 'error'
            }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def reservation_details_by_booking_id(request, booking_id):
    """Get detailed reservation information by booking ID"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
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
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error fetching reservation: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def checkout_reservation_by_booking_id(request, booking_id):
    """Check-out a reservation by booking ID"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(booking_id=booking_id)
        
        if reservation.status != 'checked_in':
            return JsonResponse({
                'message': f'Reservation is not checked in. Current status: {reservation.get_status_display()}',
                'status': 'error'
            }, status=400)
        
        # Update reservation status to checked_out
        reservation.status = 'checked_out'
        reservation.save()
        
        return JsonResponse({
            'message': f'Guest {reservation.customer.full_name} has been checked out successfully.',
            'status': 'success',
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
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
            return JsonResponse({
                'message': f'Error processing check-out: {str(e)}',
                'status': 'error'
            }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def checkin_existing_reservation(request, reservation_id):
    """Check-in an existing reservation (from waiting_checkin to checked_in)"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
    try:
        # Get the existing reservation
        reservation = Reservation.objects.select_related(
            'customer', 'room_type', 'room'
        ).get(id=reservation_id)
        
        if reservation.status != 'waiting_checkin':
            return JsonResponse({
                'message': f'Reservation is not waiting for check-in. Current status: {reservation.get_status_display()}',
                'status': 'error'
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
                import base64
                from django.core.files.base import ContentFile
                
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
                        'message': f'Selected room "{new_room.room_name}" is currently checked in',
                        'status': 'error'
                    }, status=400)
                elif new_room.room_status == 'reserved':
                    # Check if this room is reserved for the same customer
                    from django.utils import timezone
                    today = timezone.now().date()
                    existing_reservation = Reservation.objects.filter(
                        room=new_room,
                        check_in_date__lte=today,
                        check_out_date__gte=today,
                        status='waiting_checkin'
                    ).first()
                    
                    if existing_reservation and existing_reservation.customer != reservation.customer:
                        return JsonResponse({
                            'message': f'Selected room "{new_room.room_name}" is reserved for another guest',
                            'status': 'error'
                        }, status=400)
                
                # Free up the old room if different
                if reservation.room and reservation.room.id != new_room.id:
                    # The old room will be freed when we update the reservation
                    pass
                
                reservation.room = new_room
            except Room.DoesNotExist:
                return JsonResponse({
                    'message': 'Selected room does not exist',
                    'status': 'error'
                }, status=400)
        
        # Update status to checked_in
        reservation.status = 'checked_in'
        reservation.save()
        
        return JsonResponse({
            'message': f'Check-in successful! Booking ID: {reservation.booking_id}',
            'status': 'success',
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
            'message': 'Reservation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error processing check-in: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_rooms_for_type(request, room_type_id):
    """Get available rooms for a specific room type (for check-in)"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
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
            'message': 'Room type not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error fetching rooms: {str(e)}',
            'status': 'error'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_all_rooms_for_type(request, room_type_id):
    """Get all rooms for a specific room type (for reservations - includes all statuses)"""
    if request.user.role not in ['manager', 'staff']:
        return JsonResponse({'message': 'Unauthorized', 'status': 'error'}, status=403)
    
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
            'message': 'Room type not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': f'Error fetching rooms: {str(e)}',
            'status': 'error'
        }, status=500)
