// Booking API service for check-in/check-out functionality
// This file contains the API functions that will connect to your Django backend

export interface BookingDetails {
  id: string;
  booking_id: string;
  guest_name: string;
  email: string;
  phone: string;
  check_in_date: string;
  check_out_date: string;
  room_type: string;
  status: 'pending' | 'confirmed' | 'checked_in' | 'checked_out' | 'cancelled';
  special_requests?: string;
  created_at: string;
}


export interface CheckOutResponse {
  success: boolean;
  message: string;
  booking_id: string;
  check_out_time: string;
}

export interface CancelResponse {
  success: boolean;
  message: string;
  booking_id: string;
}

// Base API URL - update this to match your Django backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://kilihavenlodge.co.tz/api';

/**
 * Fetch booking details by booking ID
 * @param bookingId - The booking ID to look up
 * @returns Promise<BookingDetails>
 */
export const fetchBookingDetails = async (bookingId: string): Promise<BookingDetails> => {
  const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Booking not found');
    }
    throw new Error('Failed to fetch booking details');
  }

  const data = await response.json();
  return data;
};


/**
 * Check out a guest
 * @param bookingId - The booking ID to check out
 * @returns Promise<CheckOutResponse>
 */
export const checkOutBooking = async (bookingId: string): Promise<CheckOutResponse> => {
  const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/checkout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to check out');
  }

  return response.json();
};

/**
 * Cancel a reservation
 * @param bookingId - The booking ID to cancel
 * @returns Promise<CancelResponse>
 */
export const cancelBooking = async (bookingId: string): Promise<CancelResponse> => {
  const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/cancel/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to cancel booking');
  }

  return response.json();
};

/**
 * Get booking status
 * @param bookingId - The booking ID to check status for
 * @returns Promise<{status: string, message: string}>
 */
export const getBookingStatus = async (bookingId: string): Promise<{status: string, message: string}> => {
  const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/status/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Booking not found');
    }
    throw new Error('Failed to fetch booking status');
  }

  return response.json();
};
