from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from .models import RoomType, Room, Customer, Reservation, CheckIn, CheckOut
from datetime import datetime, timedelta
from calendar import monthrange
import weasyprint
from django.template.loader import render_to_string
from django.conf import settings


# Report Views
@login_required
def generate_checkin_report(request):
    """Generate check-in/check-out report data"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        
        # Get month name
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        # Get date range for the month
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, monthrange(year, month)[1]).date()
        
        # Get check-ins for the month
        checkins = Reservation.objects.filter(
            check_in_date__year=year,
            check_in_date__month=month,
            status__in=['checked_in', 'checked_out']
        ).select_related('customer', 'room', 'room_type')
        
        # Get check-outs for the month
        checkouts = Reservation.objects.filter(
            check_out_date__year=year,
            check_out_date__month=month,
            status='checked_out'
        ).select_related('customer', 'room', 'room_type')
        
        # Calculate summary statistics
        total_checkins = checkins.count()
        total_checkouts = checkouts.count()
        current_checked_in = Reservation.objects.filter(
            status='checked_in',
            check_in_date__lte=timezone.now().date(),
            check_out_date__gte=timezone.now().date()
        ).count()
        
        total_revenue = checkins.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Format check-in data
        checkins_data = []
        for checkin in checkins:
            checkins_data.append({
                'customer_name': checkin.customer.full_name,
                'room_name': checkin.room.room_name if checkin.room else 'Not Assigned',
                'room_type': checkin.room_type.name,
                'check_in_date': checkin.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': checkin.check_out_date.strftime('%Y-%m-%d'),
                'status': checkin.get_status_display(),
                'total_amount': float(checkin.total_amount)
            })
        
        # Format check-out data
        checkouts_data = []
        for checkout in checkouts:
            duration = (checkout.check_out_date - checkout.check_in_date).days
            checkouts_data.append({
                'customer_name': checkout.customer.full_name,
                'room_name': checkout.room.room_name if checkout.room else 'Not Assigned',
                'room_type': checkout.room_type.name,
                'check_in_date': checkout.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': checkout.check_out_date.strftime('%Y-%m-%d'),
                'duration': duration,
                'total_amount': float(checkout.total_amount)
            })
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'month_name': month_name,
                'year': year,
                'generated_date': datetime.now().strftime('%Y-%m-%d'),
                'total_checkins': total_checkins,
                'total_checkouts': total_checkouts,
                'current_checked_in': current_checked_in,
                'total_revenue': f"{float(total_revenue):,.0f}",
                'checkins': checkins_data,
                'checkouts': checkouts_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating check-in report: {str(e)}'
        }, status=500)


@login_required
def generate_sales_report(request):
    """Generate sales report data"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        
        # Get month name
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        # Calculate monthly sales
        monthly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate yearly sales
        yearly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate total bookings
        total_bookings = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).count()
        
        # Room type profits
        room_type_profits = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            monthly_reservations = Reservation.objects.filter(
                room_type=room_type,
                status__in=['checked_in', 'checked_out'],
                created_at__year=year,
                created_at__month=month
            )
            
            total_revenue = monthly_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            booking_count = monthly_reservations.count()
            
            room_type_profits.append({
                'room_type_name': room_type.name,
                'room_type_description': room_type.description,
                'price_per_day': f"{float(room_type.price_per_day):,.0f}",
                'total_revenue': f"{float(total_revenue):,.0f}",
                'booking_count': booking_count
            })
        
        # Sort by total revenue
        room_type_profits.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        # Daily sales breakdown
        daily_sales = []
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, monthrange(year, month)[1]).date()
        
        current_date = start_date
        while current_date <= end_date:
            day_reservations = Reservation.objects.filter(
                created_at__date=current_date,
                status__in=['checked_in', 'checked_out']
            )
            
            day_revenue = day_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            day_bookings = day_reservations.count()
            avg_per_booking = day_revenue / day_bookings if day_bookings > 0 else 0
            
            daily_sales.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'bookings': day_bookings,
                'revenue': f"{float(day_revenue):,.0f}",
                'avg_per_booking': float(avg_per_booking)
            })
            
            current_date += timedelta(days=1)
        
        # Top performing rooms
        top_rooms = []
        rooms = Room.objects.filter(is_active=True).select_related('room_type')
        
        for room in rooms:
            room_reservations = Reservation.objects.filter(
                room=room,
                status__in=['checked_in', 'checked_out'],
                created_at__year=year,
                created_at__month=month
            )
            
            room_revenue = room_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            room_bookings = room_reservations.count()
            
            # Calculate occupancy rate (simplified)
            days_in_month = monthrange(year, month)[1]
            occupied_days = 0
            for reservation in room_reservations:
                check_in = max(reservation.check_in_date, start_date)
                check_out = min(reservation.check_out_date, end_date)
                if check_in <= end_date and check_out >= start_date:
                    occupied_days += (check_out - check_in).days + 1
            
            occupancy_rate = (occupied_days / days_in_month) * 100 if days_in_month > 0 else 0
            
            if room_bookings > 0:  # Only include rooms with bookings
                top_rooms.append({
                    'room_name': room.room_name,
                    'room_type': room.room_type.name,
                    'bookings': room_bookings,
                    'revenue': float(room_revenue),
                    'occupancy_rate': round(occupancy_rate, 1)
                })
        
        # Sort by revenue
        top_rooms.sort(key=lambda x: x['revenue'], reverse=True)
        top_rooms = top_rooms[:10]  # Top 10 rooms
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'month_name': month_name,
                'year': year,
                'generated_date': datetime.now().strftime('%Y-%m-%d'),
                'monthly_sales': f"{float(monthly_sales):,.0f}",
                'yearly_sales': f"{float(yearly_sales):,.0f}",
                'total_bookings': total_bookings,
                'room_types_count': room_types.count(),
                'room_type_profits': room_type_profits,
                'daily_sales': daily_sales,
                'top_rooms': top_rooms
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating sales report: {str(e)}'
        }, status=500)


@login_required
def generate_reservations_report(request):
    """Generate reservations report data"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        
        # Get month name
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        # Get all reservations for the month
        reservations = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).select_related('customer', 'room', 'room_type')
        
        # Calculate summary statistics
        total_reservations = reservations.count()
        pending_count = reservations.filter(status='pending').count()
        confirmed_count = reservations.filter(status='confirmed').count()
        cancelled_count = reservations.filter(status='cancelled').count()
        
        # Format reservations data
        reservations_data = []
        for reservation in reservations:
            duration = (reservation.check_out_date - reservation.check_in_date).days
            reservations_data.append({
                'booking_id': reservation.booking_id,
                'customer_name': reservation.customer.full_name,
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'created_date': reservation.created_at.strftime('%b %d, %Y'),
                'duration': duration,
                'status': reservation.get_status_display(),
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        # Reservations by status
        status_counts = reservations.values('status').annotate(
            count=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('status')
        
        reservations_by_status = []
        for status_data in status_counts:
            count = status_data['count']
            total_revenue = status_data['total_revenue'] or 0
            avg_amount = total_revenue / count if count > 0 else 0
            percentage = (count / total_reservations) * 100 if total_reservations > 0 else 0
            
            reservations_by_status.append({
                'status': status_data['status'].replace('_', ' ').title(),
                'count': count,
                'total_revenue': f"{float(total_revenue):,.0f}",
                'avg_amount': float(avg_amount),
                'percentage': round(percentage, 1)
            })
        
        # Room type performance
        room_type_performance = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            type_reservations = reservations.filter(room_type=room_type)
            reservation_count = type_reservations.count()
            total_revenue = type_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            avg_amount = total_revenue / reservation_count if reservation_count > 0 else 0
            popularity = (reservation_count / total_reservations) * 100 if total_reservations > 0 else 0
            
            room_type_performance.append({
                'room_type_name': room_type.name,
                'reservation_count': reservation_count,
                'total_revenue': f"{float(total_revenue):,.0f}",
                'avg_amount': float(avg_amount),
                'popularity': round(popularity, 1)
            })
        
        # Sort by reservation count
        room_type_performance.sort(key=lambda x: x['reservation_count'], reverse=True)
        
        # Monthly trends (weekly breakdown)
        monthly_trends = []
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, monthrange(year, month)[1]).date()
        
        # Calculate weeks in the month
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            week_reservations = Reservation.objects.filter(
                created_at__date__range=[current_date, week_end]
            )
            
            week_checkins = Reservation.objects.filter(
                check_in_date__range=[current_date, week_end],
                status__in=['checked_in', 'checked_out']
            )
            
            week_checkouts = Reservation.objects.filter(
                check_out_date__range=[current_date, week_end],
                status='checked_out'
            )
            
            week_revenue = week_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            
            monthly_trends.append({
                'week_label': f'Week {week_num} ({current_date.strftime("%m/%d")} - {week_end.strftime("%m/%d")})',
                'new_reservations': week_reservations.count(),
                'check_ins': week_checkins.count(),
                'check_outs': week_checkouts.count(),
                'weekly_revenue': float(week_revenue)
            })
            
            current_date = week_end + timedelta(days=1)
            week_num += 1
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'month_name': month_name,
                'year': year,
                'generated_date': datetime.now().strftime('%Y-%m-%d'),
                'total_reservations': total_reservations,
                'pending_count': pending_count,
                'confirmed_count': confirmed_count,
                'cancelled_count': cancelled_count,
                'reservations': reservations_data,
                'reservations_by_status': reservations_by_status,
                'room_type_performance': room_type_performance,
                'monthly_trends': monthly_trends
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating reservations report: {str(e)}'
        }, status=500)


@login_required
def checkin_report_template(request):
    """Render checkin report template for PDF generation"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the API endpoint
        month = int(month)
        year = int(year)
        
        # Get check-in/check-out data for the specified month and year
        # Check-ins: reservations that have check-in dates in this month
        checkins = Reservation.objects.filter(
            check_in_date__year=year,
            check_in_date__month=month,
            status__in=['checked_in', 'checked_out']
        ).select_related('customer', 'room', 'room_type')
        
        # Check-outs: reservations that have check-out dates in this month
        checkouts = Reservation.objects.filter(
            check_out_date__year=year,
            check_out_date__month=month,
            status='checked_out'
        ).select_related('customer', 'room', 'room_type')
        
        # Calculate summary statistics
        total_checkins = checkins.count()
        total_checkouts = checkouts.count()
        current_checked_in = Reservation.objects.filter(
            status='checked_in',
            check_in_date__lte=timezone.now().date(),
            check_out_date__gte=timezone.now().date()
        ).count()
        
        total_revenue = checkins.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Prepare data for template
        checkins_data = []
        for reservation in checkins:
            checkins_data.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_name': reservation.room.room_name if reservation.room else 'N/A',
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'status': reservation.get_status_display(),
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        # Prepare checkouts data
        checkouts_data = []
        for reservation in checkouts:
            checkouts_data.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_name': reservation.room.room_name if reservation.room else 'N/A',
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'duration': (reservation.check_out_date - reservation.check_in_date).days,
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'total_checkins': total_checkins,
            'total_checkouts': total_checkouts,
            'current_checked_in': current_checked_in,
            'total_revenue': float(total_revenue),
            'checkins': checkins_data,
            'checkouts': checkouts_data
        }
        
        return render(request, 'kilimanager/checkin_checkout_report.html', context)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error rendering checkin report template: {str(e)}'
        }, status=500)


@login_required
def sales_report_template(request):
    """Render sales report template for PDF generation"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the API endpoint
        month = int(month)
        year = int(year)
        
        # Calculate monthly sales for selected period
        monthly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate yearly sales for selected year
        yearly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate total bookings for selected month
        total_bookings = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).count()
        
        # Room type profit breakdown for selected period
        room_type_profits = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            # Get reservations for this room type in selected period
            monthly_reservations = Reservation.objects.filter(
                room_type=room_type,
                status__in=['checked_in', 'checked_out'],
                created_at__year=year,
                created_at__month=month
            )
            
            # Calculate total revenue for this room type
            total_revenue = monthly_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Count number of bookings
            booking_count = monthly_reservations.count()
            
            # Include all room types (even with 0 sales) for complete overview
            room_type_profits.append({
                'room_type_name': room_type.name,
                'room_type_description': room_type.description,
                'price_per_day': f"{float(room_type.price_per_day):,.0f}",
                'total_revenue': f"{float(total_revenue):,.0f}",
                'booking_count': booking_count,
                'average_revenue': f"{float(total_revenue) / booking_count:,.0f}" if booking_count > 0 else "0"
            })
        
        # Sort by total revenue (highest first)
        room_type_profits.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        # Customer payments for the selected period
        customer_payments = []
        reservations_with_payments = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month,
            status__in=['checked_in', 'checked_out']
        ).select_related('customer', 'room_type').order_by('-created_at')
        
        for reservation in reservations_with_payments:
            # Calculate duration in days
            duration = (reservation.check_out_date - reservation.check_in_date).days
            
            customer_payments.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'room_type': reservation.room_type.name,
                'payment_date': reservation.created_at.strftime('%b %d, %Y'),
                'duration': duration,
                'amount_paid': f"{float(reservation.total_amount):,.0f}",
                'payment_status': reservation.get_payment_status_display()
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'monthly_sales': f"{float(monthly_sales):,.0f}",
            'yearly_sales': f"{float(yearly_sales):,.0f}",
            'total_bookings': total_bookings,
            'room_type_profits': room_type_profits,
            'room_types_count': len(room_type_profits),
            'customer_payments': customer_payments
        }
        
        return render(request, 'kilimanager/sales_report.html', context)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error rendering sales report template: {str(e)}'
        }, status=500)


@login_required
def reservations_report_template(request):
    """Render reservations report template for PDF generation"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the API endpoint
        month = int(month)
        year = int(year)
        
        # Get reservations for the specified month and year
        reservations = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).select_related('customer', 'room_type', 'room')
        
        # Calculate summary statistics
        total_reservations = reservations.count()
        pending_count = reservations.filter(status='pending').count()
        confirmed_count = reservations.filter(status='confirmed').count()
        cancelled_count = reservations.filter(status='cancelled').count()
        
        # Prepare data for template
        reservations_data = []
        for reservation in reservations:
            duration = (reservation.check_out_date - reservation.check_in_date).days
            reservations_data.append({
                'booking_id': reservation.booking_id,
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'created_date': reservation.created_at.strftime('%b %d, %Y'),
                'duration': duration,
                'status': reservation.get_status_display(),
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        # Group reservations by status
        reservations_by_status = {}
        for status_choice in Reservation.STATUS_CHOICES:
            status_code = status_choice[0]
            status_display = status_choice[1]
            count = reservations.filter(status=status_code).count()
            reservations_by_status[status_display] = count
        
        # Room type performance
        room_type_performance = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            room_reservations = reservations.filter(room_type=room_type)
            total_revenue = room_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            booking_count = room_reservations.count()
            
            room_type_performance.append({
                'room_type_name': room_type.name,
                'booking_count': booking_count,
                'total_revenue': f"{float(total_revenue):,.0f}",
                'average_revenue': f"{float(total_revenue) / booking_count:,.0f}" if booking_count > 0 else "0"
            })
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            trend_month = month - i
            trend_year = year
            if trend_month <= 0:
                trend_month += 12
                trend_year -= 1
            
            trend_reservations = Reservation.objects.filter(
                created_at__year=trend_year,
                created_at__month=trend_month
            )
            trend_count = trend_reservations.count()
            trend_revenue = trend_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            monthly_trends.append({
                'month': month_names[trend_month],
                'year': trend_year,
                'count': trend_count,
                'revenue': float(trend_revenue)
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'total_reservations': total_reservations,
            'pending_count': pending_count,
            'confirmed_count': confirmed_count,
            'cancelled_count': cancelled_count,
            'reservations': reservations_data,
            'reservations_by_status': reservations_by_status,
            'room_type_performance': room_type_performance,
            'monthly_trends': monthly_trends
        }
        
        return render(request, 'kilimanager/reservations_report.html', context)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error rendering reservations report template: {str(e)}'
        }, status=500)


@login_required
def download_checkin_report_pdf(request):
    """Download check-in/check-out report as PDF"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the template function
        month = int(month)
        year = int(year)
        
        # Get check-in/check-out data for the specified month and year
        checkins = Reservation.objects.filter(
            check_in_date__year=year,
            check_in_date__month=month,
            status__in=['checked_in', 'checked_out']
        ).select_related('customer', 'room', 'room_type')
        
        checkouts = Reservation.objects.filter(
            check_out_date__year=year,
            check_out_date__month=month,
            status='checked_out'
        ).select_related('customer', 'room', 'room_type')
        
        # Calculate summary statistics
        total_checkins = checkins.count()
        total_checkouts = checkouts.count()
        current_checked_in = Reservation.objects.filter(
            status='checked_in',
            check_in_date__lte=timezone.now().date(),
            check_out_date__gte=timezone.now().date()
        ).count()
        
        total_revenue = checkins.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Prepare data for template
        checkins_data = []
        for reservation in checkins:
            checkins_data.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_name': reservation.room.room_name if reservation.room else 'N/A',
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'status': reservation.get_status_display(),
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        # Prepare checkouts data
        checkouts_data = []
        for reservation in checkouts:
            checkouts_data.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_name': reservation.room.room_name if reservation.room else 'N/A',
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'duration': (reservation.check_out_date - reservation.check_in_date).days,
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'total_checkins': total_checkins,
            'total_checkouts': total_checkouts,
            'current_checked_in': current_checked_in,
            'total_revenue': float(total_revenue),
            'checkins': checkins_data,
            'checkouts': checkouts_data
        }
        
        # Render HTML template
        html_string = render_to_string('kilimanager/checkin_checkout_report.html', context)
        
        # Create PDF with landscape orientation
        pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[weasyprint.CSS(string='''
                @page {
                    size: A4 landscape;
                    margin: 0.5in;
                }
                body {
                    font-size: 12px;
                }
                .report-container {
                    max-width: none;
                    width: 100%;
                }
                .data-table {
                    font-size: 11px;
                }
                .data-table th,
                .data-table td {
                    padding: 6px 4px;
                }
                .summary-cards {
                    grid-template-columns: repeat(4, 1fr);
                    gap: 10px;
                }
                .summary-card {
                    padding: 10px;
                }
                .summary-card h4 {
                    font-size: 10px;
                }
                .summary-card .value {
                    font-size: 16px;
                }
            ''')]
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="checkin_report_{month_name}_{year}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating PDF: {str(e)}'
        }, status=500)


@login_required
def download_reservations_report_pdf(request):
    """Download reservations report as PDF"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the template function
        month = int(month)
        year = int(year)
        
        # Get reservations for the specified month and year
        reservations = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).select_related('customer', 'room_type', 'room')
        
        # Calculate summary statistics
        total_reservations = reservations.count()
        pending_count = reservations.filter(status='pending').count()
        confirmed_count = reservations.filter(status='confirmed').count()
        cancelled_count = reservations.filter(status='cancelled').count()
        
        # Prepare data for template
        reservations_data = []
        for reservation in reservations:
            duration = (reservation.check_out_date - reservation.check_in_date).days
            reservations_data.append({
                'booking_id': reservation.booking_id,
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'guest_origin': reservation.customer.guest_origin,
                'room_type': reservation.room_type.name,
                'check_in_date': reservation.check_in_date.strftime('%b %d, %Y'),
                'check_out_date': reservation.check_out_date.strftime('%b %d, %Y'),
                'created_date': reservation.created_at.strftime('%b %d, %Y'),
                'duration': duration,
                'status': reservation.get_status_display(),
                'total_amount': f"{float(reservation.total_amount):,.0f}"
            })
        
        # Group reservations by status
        reservations_by_status = {}
        for status_choice in Reservation.STATUS_CHOICES:
            status_code = status_choice[0]
            status_display = status_choice[1]
            count = reservations.filter(status=status_code).count()
            reservations_by_status[status_display] = count
        
        # Room type performance
        room_type_performance = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            room_reservations = reservations.filter(room_type=room_type)
            total_revenue = room_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            booking_count = room_reservations.count()
            
            room_type_performance.append({
                'room_type_name': room_type.name,
                'booking_count': booking_count,
                'total_revenue': f"{float(total_revenue):,.0f}",
                'average_revenue': f"{float(total_revenue) / booking_count:,.0f}" if booking_count > 0 else "0"
            })
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            trend_month = month - i
            trend_year = year
            if trend_month <= 0:
                trend_month += 12
                trend_year -= 1
            
            trend_reservations = Reservation.objects.filter(
                created_at__year=trend_year,
                created_at__month=trend_month
            )
            trend_count = trend_reservations.count()
            trend_revenue = trend_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            monthly_trends.append({
                'month': month_names[trend_month],
                'year': trend_year,
                'count': trend_count,
                'revenue': float(trend_revenue)
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'total_reservations': total_reservations,
            'pending_count': pending_count,
            'confirmed_count': confirmed_count,
            'cancelled_count': cancelled_count,
            'reservations': reservations_data,
            'reservations_by_status': reservations_by_status,
            'room_type_performance': room_type_performance,
            'monthly_trends': monthly_trends
        }
        
        # Render HTML template
        html_string = render_to_string('kilimanager/reservations_report.html', context)
        
        # Create PDF with landscape orientation
        pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[weasyprint.CSS(string='''
                @page {
                    size: A4 landscape;
                    margin: 0.5in;
                }
                body {
                    font-size: 12px;
                }
                .report-container {
                    max-width: none;
                    width: 100%;
                }
                .data-table {
                    font-size: 11px;
                }
                .data-table th,
                .data-table td {
                    padding: 6px 4px;
                }
                .summary-cards {
                    grid-template-columns: repeat(4, 1fr);
                    gap: 10px;
                }
                .summary-card {
                    padding: 10px;
                }
                .summary-card h4 {
                    font-size: 10px;
                }
                .summary-card .value {
                    font-size: 16px;
                }
            ''')]
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reservations_report_{month_name}_{year}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating PDF: {str(e)}'
        }, status=500)


@login_required
def download_sales_report_pdf(request):
    """Download sales report as PDF"""
    if request.user.role != 'manager':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'status': 'error', 'message': 'Month and year are required'}, status=400)
    
    try:
        # Get the same data as the template function
        month = int(month)
        year = int(year)
        
        # Calculate monthly sales for selected period
        monthly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate yearly sales for selected year
        yearly_sales = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate total bookings for selected month
        total_bookings = Reservation.objects.filter(
            status__in=['checked_in', 'checked_out'],
            created_at__year=year,
            created_at__month=month
        ).count()
        
        # Room type profit breakdown for selected period
        room_type_profits = []
        room_types = RoomType.objects.all()
        
        for room_type in room_types:
            # Get reservations for this room type in selected period
            monthly_reservations = Reservation.objects.filter(
                room_type=room_type,
                status__in=['checked_in', 'checked_out'],
                created_at__year=year,
                created_at__month=month
            )
            
            # Calculate total revenue for this room type
            total_revenue = monthly_reservations.aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Count number of bookings
            booking_count = monthly_reservations.count()
            
            # Include all room types (even with 0 sales) for complete overview
            room_type_profits.append({
                'room_type_name': room_type.name,
                'room_type_description': room_type.description,
                'price_per_day': f"{float(room_type.price_per_day):,.0f}",
                'total_revenue': f"{float(total_revenue):,.0f}",
                'booking_count': booking_count,
                'average_revenue': f"{float(total_revenue) / booking_count:,.0f}" if booking_count > 0 else "0"
            })
        
        # Sort by total revenue (highest first)
        room_type_profits.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        # Customer payments for the selected period
        customer_payments = []
        reservations_with_payments = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month,
            status__in=['checked_in', 'checked_out']
        ).select_related('customer', 'room_type').order_by('-created_at')
        
        for reservation in reservations_with_payments:
            # Calculate duration in days
            duration = (reservation.check_out_date - reservation.check_in_date).days
            
            customer_payments.append({
                'customer_name': reservation.customer.full_name,
                'phone_number': reservation.customer.phone_number,
                'room_type': reservation.room_type.name,
                'payment_date': reservation.created_at.strftime('%b %d, %Y'),
                'duration': duration,
                'amount_paid': f"{float(reservation.total_amount):,.0f}",
                'payment_status': reservation.get_payment_status_display()
            })
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            'month_name': month_name,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'monthly_sales': f"{float(monthly_sales):,.0f}",
            'yearly_sales': f"{float(yearly_sales):,.0f}",
            'total_bookings': total_bookings,
            'room_type_profits': room_type_profits,
            'room_types_count': len(room_type_profits),
            'customer_payments': customer_payments
        }
        
        # Render HTML template
        html_string = render_to_string('kilimanager/sales_report.html', context)
        
        # Create PDF with landscape orientation
        pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[weasyprint.CSS(string='''
                @page {
                    size: A4 landscape;
                    margin: 0.5in;
                }
                body {
                    font-size: 12px;
                }
                .report-container {
                    max-width: none;
                    width: 100%;
                }
                .data-table {
                    font-size: 11px;
                }
                .data-table th,
                .data-table td {
                    padding: 6px 4px;
                }
                .summary-cards {
                    grid-template-columns: repeat(4, 1fr);
                    gap: 10px;
                }
                .summary-card {
                    padding: 10px;
                }
                .summary-card h4 {
                    font-size: 10px;
                }
                .summary-card .value {
                    font-size: 16px;
                }
            ''')]
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{month_name}_{year}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating PDF: {str(e)}'
        }, status=500)
