from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.

class RoomType(models.Model):
    """Model for different room types in the lodge"""
    name = models.CharField(max_length=100, unique=True, help_text="Room type name (e.g., Standard, Deluxe, Suite)")
    price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Price per day in TZS"
    )
    total_rooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Total number of rooms of this type"
    )
    description = models.TextField(blank=True, help_text="Room description and amenities")
    is_active = models.BooleanField(default=True, help_text="Whether this room type is available for booking")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"

    def __str__(self):
        return f"{self.name} - TZS {self.price_per_day}/day"

    @property
    def available_rooms(self):
        """Calculate available rooms of this type"""
        today = timezone.now().date()
        
        # Count rooms with active reservations (current)
        active_reserved_rooms = Reservation.objects.filter(
            room_type=self,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status__in=['waiting_checkin', 'checked_in']
        ).count()
        
        # Count rooms with future reservations
        future_reserved_rooms = Reservation.objects.filter(
            room_type=self,
            check_in_date__gt=today,
            status__in=['waiting_checkin', 'confirmed']
        ).count()
        
        total_reserved = active_reserved_rooms + future_reserved_rooms
        return max(0, self.total_rooms - total_reserved)

    def get_available_rooms_for_dates(self, check_in_date, check_out_date):
        """Get available rooms for a specific date range"""
        # Get all rooms of this type
        all_rooms = self.rooms.filter(is_active=True)
        
        # Get rooms that are reserved during the date range
        reserved_rooms = Reservation.objects.filter(
            room__room_type=self,
            room__isnull=False,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            status__in=['waiting_checkin', 'checked_in', 'confirmed']
        ).values_list('room_id', flat=True)
        
        # Return available rooms
        available_rooms = all_rooms.exclude(id__in=reserved_rooms)
        return available_rooms


class Room(models.Model):
    """Model for individual rooms within a room type"""
    room_type = models.ForeignKey(
        RoomType, 
        on_delete=models.CASCADE, 
        related_name='rooms',
        help_text="Room type this room belongs to"
    )
    room_name = models.CharField(
        max_length=100, 
        help_text="Name of the room (e.g., Room 1, Mountain View, etc.)"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this room is available for booking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room_type', 'room_name']
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        unique_together = ['room_type', 'room_name']  # Ensure unique room names per room type

    def __str__(self):
        return f"{self.room_type.name} - {self.room_name}"

    @property
    def is_available(self):
        """Check if room is currently available"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if not self.is_active:
            return False
        
        # Check if there are any active reservations for this room (current or future)
        active_reservations = Reservation.objects.filter(
            room=self,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status__in=['waiting_checkin', 'checked_in']
        ).exists()
        
        # Check for future reservations
        future_reservations = Reservation.objects.filter(
            room=self,
            check_in_date__gt=today,
            status__in=['waiting_checkin', 'confirmed']
        ).exists()
        
        return not (active_reservations or future_reservations)

    @property
    def room_status(self):
        """Get the current status of the room"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if not self.is_active:
            return 'inactive'
        
        # Check for checked-in reservations (currently active)
        checked_in_reservation = Reservation.objects.filter(
            room=self,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='checked_in'
        ).first()
        
        if checked_in_reservation:
            return 'checked_in'
        
        # Check for waiting check-in reservations (currently active)
        waiting_checkin_reservation = Reservation.objects.filter(
            room=self,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='waiting_checkin'
        ).first()
        
        if waiting_checkin_reservation:
            return 'reserved'
        
        # Check for any future reservations (confirmed but not yet active)
        future_reservation = Reservation.objects.filter(
            room=self,
            check_in_date__gt=today,
            status__in=['waiting_checkin', 'confirmed']
        ).first()
        
        if future_reservation:
            return 'reserved'
        
        return 'available'

    def is_available_for_dates(self, check_in_date, check_out_date):
        """Check if room is available for specific date range"""
        if not self.is_active:
            return False
        
        # Check if there are any reservations that overlap with the date range
        overlapping_reservations = Reservation.objects.filter(
            room=self,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            status__in=['waiting_checkin', 'checked_in', 'confirmed']
        ).exists()
        
        return not overlapping_reservations


class Customer(models.Model):
    """Model for customers/guests"""
    
    ID_TYPE_CHOICES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('other', 'Other ID'),
    ]
    
    email = models.EmailField(unique=True, help_text="Customer email address")
    full_name = models.CharField(max_length=200, help_text="Customer full name")
    phone_number = models.CharField(max_length=20, help_text="Customer phone number")
    nationality = models.CharField(max_length=100, help_text="Customer nationality")
    id_type = models.CharField(
        max_length=20,
        choices=ID_TYPE_CHOICES,
        help_text="Type of identification document"
    )
    other_id_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Name of other ID type (if 'other' is selected)"
    )
    id_passport_number = models.CharField(max_length=50, unique=True, help_text="ID or Passport number")
    id_passport_photo = models.ImageField(
        upload_to='customers/id_photos/', 
        blank=True,
        null=True,
        help_text="ID or Passport photo"
    )
    guest_origin = models.CharField(
        max_length=200, 
        help_text="Where the customer is coming from (city, country)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def total_reservations(self):
        """Get total number of reservations for this customer"""
        return self.reservations.count()

    @property
    def is_regular_guest(self):
        """Check if customer is a regular guest (more than 1 reservation)"""
        return self.total_reservations > 1


class Reservation(models.Model):
    """Model for reservations"""
    
    PURPOSE_CHOICES = [
        ('leisure', 'Leisure'),
        ('business', 'Business'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('waiting_checkin', 'Waiting Check-in'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]

    # Booking ID - unique 6-character identifier
    booking_id = models.CharField(
        max_length=6, 
        unique=True, 
        help_text="Unique 6-character booking identifier"
    )
    
    # Customer and Room Information
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        help_text="Customer making the reservation"
    )
    room_type = models.ForeignKey(
        RoomType, 
        on_delete=models.CASCADE, 
        help_text="Selected room type"
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Assigned specific room (set when reservation is confirmed)"
    )
    
    # Reservation Details
    check_in_date = models.DateField(help_text="Check-in date")
    check_out_date = models.DateField(help_text="Check-out date")
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Number of guests"
    )
    purpose_of_visit = models.CharField(
        max_length=20, 
        choices=PURPOSE_CHOICES, 
        default='leisure',
        help_text="Purpose of visit"
    )
    special_requests = models.TextField(blank=True, help_text="Special requests or accommodations")
    
    # Reservation Management
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Reservation status"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Total amount for the stay"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Paid'),
            ('not_paid', 'Not Paid'),
            ('partial', 'Partial Payment'),
        ],
        default='not_paid',
        help_text="Payment status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        return f"{self.customer.full_name} - {self.room_type.name} - {self.check_in_date} to {self.check_out_date}"

    def generate_booking_id(self):
        """Generate a unique 6-character booking ID"""
        import random
        import string
        
        while True:
            # Generate 6-character ID with letters and numbers
            booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Reservation.objects.filter(booking_id=booking_id).exists():
                return booking_id

    def save(self, *args, **kwargs):
        """Generate booking ID and calculate total amount before saving"""
        # Generate booking ID if not set
        if not self.booking_id:
            self.booking_id = self.generate_booking_id()
        
        # Calculate total amount based ONLY on room price per day and duration (NOT guests)
        if self.room_type and self.check_in_date and self.check_out_date:
            days = (self.check_out_date - self.check_in_date).days
            if days > 0:  # Ensure positive days
                # Amount = room price per day × number of days (guests don't affect price)
                self.total_amount = self.room_type.price_per_day * days
            else:
                # Minimum 1 day charge
                self.total_amount = self.room_type.price_per_day
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Calculate number of days"""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    @property
    def is_active(self):
        """Check if reservation is currently active"""
        today = timezone.now().date()
        return (self.status == 'confirmed' and 
                self.check_in_date <= today <= self.check_out_date)


class CheckIn(models.Model):
    """Model for check-in records"""
    reservation = models.OneToOneField(
        Reservation, 
        on_delete=models.CASCADE, 
        related_name='checkin',
        help_text="Associated reservation"
    )
    check_in_time = models.DateTimeField(auto_now_add=True, help_text="Actual check-in time")
    room_key_given = models.BooleanField(default=False, help_text="Whether room key was given")
    welcome_pack_given = models.BooleanField(default=False, help_text="Whether welcome pack was given")
    additional_notes = models.TextField(blank=True, help_text="Additional check-in notes")
    checked_in_by = models.CharField(max_length=100, help_text="Staff member who checked in the guest")

    class Meta:
        ordering = ['-check_in_time']
        verbose_name = "Check In"
        verbose_name_plural = "Check Ins"

    def __str__(self):
        return f"Check-in: {self.reservation.customer.full_name} - {self.check_in_time}"

    @property
    def is_checked_in(self):
        """Check if guest is currently checked in"""
        return self.reservation.status == 'confirmed' and self.reservation.check_in_date <= timezone.now().date()


class CheckOut(models.Model):
    """Model for check-out records"""
    reservation = models.OneToOneField(
        Reservation, 
        on_delete=models.CASCADE, 
        related_name='checkout',
        help_text="Associated reservation"
    )
    check_out_time = models.DateTimeField(auto_now_add=True, help_text="Actual check-out time")
    room_key_returned = models.BooleanField(default=False, help_text="Whether room key was returned")
    room_condition = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('damaged', 'Damaged'),
        ],
        default='good',
        help_text="Condition of room after check-out"
    )
    additional_charges = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Additional charges (damages, extra services, etc.)"
    )
    final_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Final amount including additional charges"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('mobile_money', 'Mobile Money'),
        ],
        help_text="Payment method used"
    )
    additional_notes = models.TextField(blank=True, help_text="Additional check-out notes")
    checked_out_by = models.CharField(max_length=100, help_text="Staff member who checked out the guest")

    class Meta:
        ordering = ['-check_out_time']
        verbose_name = "Check Out"
        verbose_name_plural = "Check Outs"

    def __str__(self):
        return f"Check-out: {self.reservation.customer.full_name} - {self.check_out_time}"

    def save(self, *args, **kwargs):
        """Calculate final amount before saving"""
        self.final_amount = self.reservation.total_amount + self.additional_charges
        super().save(*args, **kwargs)
