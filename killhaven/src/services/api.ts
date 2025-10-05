const API_BASE_URL = 'https://kilihavenlodge.co.tz/api'; // Your Django server URL

export interface HomeData {
  name: string;
  email: string;
  phone?: string;
  message?: string;
  type: 'booking' | 'contact' | 'inquiry';
}

export interface LoginData {
  email: string;    // Django expects 'email'
  password: string; // Django expects 'password'
  username?: string; // Alternative field name some Django setups use
}

export interface LoginResponse {
  message: string;
  status: string;
  redirect_url?: string;
  role?: string;
  role_display?: string;
  user?: {
    id: number;
    username: string;
    email: string;
    role: string;
    role_display?: string;
  };
}

export interface RoomType {
  id: number;
  name: string;
  price_per_day: string;
  description: string;
  total_rooms: number;
  available_rooms: number;
}

export const submitHome = async (data: HomeData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/home/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to submit form');
    }

    return await response.json();
  } catch (error) {
    console.error('Form submission error:', error);
    throw error;
  }
};

export const submitLogin = async (data: LoginData): Promise<LoginResponse> => {
  try {
    console.log('Sending login request:', data);
    console.log('API URL:', `${API_BASE_URL}/login/`);
    
    const response = await fetch(`${API_BASE_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'include', // Include cookies for Django sessions
      body: JSON.stringify(data),
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    let responseData;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      responseData = await response.json();
    } else {
      const textData = await response.text();
      console.log('Non-JSON response:', textData);
      responseData = { message: textData || 'Server error' };
    }
    
    console.log('Response data:', responseData);

    if (!response.ok) {
      // Return the error response from the server
      let errorMessage = responseData.message || responseData.error || responseData.detail || 'Login failed';
      
      // Normalize common error messages
      if (errorMessage.toLowerCase().includes('user not found')) {
        errorMessage = 'User not found';
      }
      
      return {
        status: 'error',
        message: errorMessage
      };
    }

    return responseData;
  } catch (error) {
    console.error('Login error:', error);
    return {
      status: 'error',
      message: 'Network error. Please check your connection.'
    };
  }
};

export const fetchRoomTypes = async (): Promise<RoomType[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/room-types/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch room types');
    }

    const data = await response.json();
    return data.room_types || [];
  } catch (error) {
    console.error('Room types fetch error:', error);
    throw error;
  }
};
