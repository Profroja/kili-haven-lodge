from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from kilimanager.models import RoomType, Reservation, Customer, CheckOut
from django.utils import timezone
import json

# Get the custom User model
User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def home(request):
    """Handle all homepage form submissions"""
    try:
        data = json.loads(request.body)
        
        
        # Only process booking requests
        if data.get('type') == 'booking':
            # Parse the booking message to extract details
            message = data.get('message', '')
            lines = message.split('\n')
            
            # Extract booking details from message
            booking_details = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_').replace('-', '_')
                    value = value.strip()
                    booking_details[key] = value
            
            # Extract customer information
            customer_name = data.get('name', '')
            customer_email = data.get('email', '')
            customer_phone = data.get('phone', '')
            
            # Extract booking details
            check_in = booking_details.get('check_in', '')
            check_out = booking_details.get('check_out', '')
            room_type_name = booking_details.get('room_type', '')
            guests = booking_details.get('number_of_guests', '1')
            id_document = booking_details.get('id_document', 'national_id')
            origin = booking_details.get('origin', '')
            purpose_of_stay = booking_details.get('purpose_of_stay', 'leisure')
            special_requests = booking_details.get('special_requests', 'None')
            
            # Parse room type name (remove price info)
            if 'TZS' in room_type_name:
                room_type_name = room_type_name.split('TZS')[0].strip()
            
            # Get or create customer
            from kilimanager.models import Customer, RoomType, Reservation
            from datetime import datetime
            
            customer, created = Customer.objects.get_or_create(
                email=customer_email,
                defaults={
                    'full_name': customer_name,
                    'phone_number': customer_phone,
                    'nationality': 'Tanzania',  # Default, could be extracted from origin
                    'id_type': id_document,
                    'id_passport_number': f"TEMP_{customer_email}",  # Temporary ID
                    'guest_origin': origin,
                }
            )
            
            # Update customer if exists
            if not created:
                customer.full_name = customer_name
                customer.phone_number = customer_phone
                customer.guest_origin = origin
                customer.save()
            
            # Find room type
            try:
                room_type = RoomType.objects.get(name__icontains=room_type_name)
            except RoomType.DoesNotExist:
                # If room type not found, use the first available one
                room_type = RoomType.objects.filter(is_active=True).first()
                if not room_type:
                    return JsonResponse({
                        'message': 'No room types available',
                        'status': 'error'
                    }, status=400)
            
            # Parse dates
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'message': 'Invalid date format',
                    'status': 'error'
                }, status=400)
            
            # Create reservation
            reservation = Reservation.objects.create(
                customer=customer,
                room_type=room_type,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                number_of_guests=int(guests) if guests.isdigit() else 1,
                purpose_of_visit=purpose_of_stay,
                special_requests=special_requests if special_requests != 'None' else '',
                status='pending'
            )
            
            # Send SMS notification to admin
            try:
                from kilimanager.sms_service import send_reservation_notification
                
                # Format dates for SMS
                check_in_formatted = check_in_date.strftime('%d/%m/%Y')
                check_out_formatted = check_out_date.strftime('%d/%m/%Y')
                
                # Send SMS notification
                sms_result = send_reservation_notification(
                    booking_id=reservation.booking_id,
                    customer_name=customer.full_name,
                    customer_phone=customer.phone_number,
                    room_type=room_type.name,
                    check_in_date=check_in_formatted,
                    check_out_date=check_out_formatted
                )
                
                # Log SMS result (optional - you can remove this if not needed)
                if not sms_result['success']:
                    print(f"SMS notification failed: {sms_result['message']}")
                    
            except Exception as sms_error:
                # Don't fail the reservation if SMS fails
                print(f"SMS notification error: {str(sms_error)}")
            
            return JsonResponse({
                'message': f'Booking request submitted successfully! Your booking ID is: {reservation.booking_id}. We will contact you within 24 hours to confirm your reservation.',
                'status': 'success',
                'reservation_id': reservation.id,
                'booking_id': reservation.booking_id,
                'total_amount': str(reservation.total_amount),
                'customer_name': customer.full_name
            })
        
        # For non-booking requests, just return success
        return JsonResponse({
            'message': 'Form submitted successfully!',
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'message': f'Error processing booking: {str(e)}',
            'status': 'error'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """Handle login form submissions from React frontend"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        
        # Find user by email (since your frontend sends email)
        try:
            user = User.objects.get(email=email)
            # Authenticate using username and password
            authenticated_user = authenticate(request, username=user.username, password=password)
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                
                # Determine redirect URL based on role
                if authenticated_user.role == 'manager':
                    redirect_url = '/manager/dashboard/'
                    role_display = 'Manager'
                else:  # lodge_attendant or any other role
                    redirect_url = '/staff/dashboard/'
                    role_display = 'Staff'
                
                return JsonResponse({
                    'message': 'Login successful!',
                    'status': 'success',
                    'redirect_url': redirect_url,
                    'role': authenticated_user.role,
                    'role_display': role_display,
                    'user': {
                        'id': authenticated_user.id,
                        'username': authenticated_user.username,
                        'email': authenticated_user.email,
                        'role': authenticated_user.role
                    }
                })
            else:
                return JsonResponse({
                    'message': 'Invalid password',
                    'status': 'error'
                }, status=400)
                
        except User.DoesNotExist:
            return JsonResponse({
                'message': 'User not found',
                'status': 'error'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'message': 'Login failed',
            'status': 'error'
        }, status=400)

@require_http_methods(["GET"])
def room_types(request):
    """Get all active room types for booking form"""
    try:
        room_types = RoomType.objects.filter(is_active=True).order_by('name')
        
        room_types_data = []
        for room_type in room_types:
            room_types_data.append({
                'id': room_type.id,
                'name': room_type.name,
                'price_per_day': str(room_type.price_per_day),
                'description': room_type.description,
                'total_rooms': room_type.total_rooms,
                'available_rooms': room_type.available_rooms
            })
        
        return JsonResponse({
            'status': 'success',
            'room_types': room_types_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching room types: {str(e)}'
        }, status=500)


# ===== BOOKING MANAGEMENT API ENDPOINTS =====

@require_http_methods(["GET"])
def get_booking_details(request, booking_id):
    """Get booking details by booking ID"""
    try:
        reservation = Reservation.objects.select_related('customer', 'room_type').get(booking_id=booking_id)
        
        booking_data = {
            'id': reservation.id,
            'booking_id': reservation.booking_id,
            'guest_name': reservation.customer.full_name,
            'email': reservation.customer.email,
            'phone': reservation.customer.phone_number,
            'check_in_date': reservation.check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': reservation.check_out_date.strftime('%Y-%m-%d'),
            'room_type': reservation.room_type.name,
            'status': reservation.status,
            'special_requests': reservation.special_requests,
            'created_at': reservation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_amount': str(reservation.total_amount),
            'number_of_guests': reservation.number_of_guests,
            'purpose_of_visit': reservation.purpose_of_visit,
            'payment_status': reservation.payment_status
        }
        
        return JsonResponse(booking_data)
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'error': 'Booking not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to fetch booking details: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def checkout_booking(request, booking_id):
    """Check out a guest"""
    try:
        reservation = Reservation.objects.get(booking_id=booking_id)
        
        # Validate that guest can check out
        if reservation.status != 'checked_in':
            return JsonResponse({
                'success': False,
                'message': f'Cannot check out. Current status: {reservation.get_status_display()}'
            }, status=400)
        
        # Check if already checked out
        if hasattr(reservation, 'checkout'):
            return JsonResponse({
                'success': False,
                'message': 'Guest has already checked out'
            }, status=400)
        
        # Create checkout record
        checkout = CheckOut.objects.create(
            reservation=reservation,
            room_key_returned=True,  # Default to True for remote checkout
            room_condition='good',   # Default condition
            additional_charges=0,
            payment_method='cash',   # Default payment method
            checked_out_by='Guest (Remote)'
        )
        
        # Update reservation status
        reservation.status = 'checked_out'
        reservation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully checked out',
            'booking_id': reservation.booking_id,
            'check_out_time': checkout.check_out_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Failed to check out: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """Cancel a reservation"""
    try:
        reservation = Reservation.objects.get(booking_id=booking_id)
        
        # Validate that reservation can be cancelled
        if reservation.status in ['checked_in', 'cancelled']:
            return JsonResponse({
                'success': False,
                'message': f'Cannot cancel reservation. Current status: {reservation.get_status_display()}'
            }, status=400)
        
        # Check if check-in date has passed
        today = timezone.now().date()
        if reservation.check_in_date <= today:
            return JsonResponse({
                'success': False,
                'message': 'Cannot cancel reservation. Check-in date has passed'
            }, status=400)
        
        # Update reservation status
        reservation.status = 'cancelled'
        reservation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Reservation cancelled successfully',
            'booking_id': reservation.booking_id
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Failed to cancel booking: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_booking_status(request, booking_id):
    """Get booking status"""
    try:
        reservation = Reservation.objects.get(booking_id=booking_id)
        
        # Determine status message based on current status
        status_messages = {
            'pending': 'Your reservation is pending confirmation. We will contact you within 24 hours.',
            'confirmed': 'Your reservation is confirmed. Please check in at the front desk on your arrival date.',
            'waiting_checkin': 'Your reservation is confirmed. Please check in at the front desk.',
            'checked_in': 'You are currently checked in. You can check out remotely using this system.',
            'checked_out': 'You have successfully checked out. Thank you for staying with us!',
            'cancelled': 'This reservation has been cancelled.'
        }
        
        return JsonResponse({
            'status': reservation.status,
            'status_display': reservation.get_status_display(),
            'message': status_messages.get(reservation.status, 'Unknown status'),
            'booking_id': reservation.booking_id,
            'check_in_date': reservation.check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': reservation.check_out_date.strftime('%Y-%m-%d')
        })
        
    except Reservation.DoesNotExist:
        return JsonResponse({
            'error': 'Booking not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to fetch booking status: {str(e)}'
        }, status=500)