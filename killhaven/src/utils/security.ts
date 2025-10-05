// Security utilities for form validation and protection

// Rate limiting configuration
const RATE_LIMIT_CONFIG = {
  login: {
    maxAttempts: 5,
    windowMs: 15 * 60 * 1000, // 15 minutes
    lockoutMs: 30 * 60 * 1000, // 30 minutes
  },
  booking: {
    maxAttempts: 10,
    windowMs: 60 * 60 * 1000, // 1 hour
    lockoutMs: 2 * 60 * 60 * 1000, // 2 hours
  }
};

// Input sanitization
export const sanitizeInput = (input: string): string => {
  if (typeof input !== 'string') return '';
  
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .substring(0, 1000); // Limit length
};

// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email) && email.length <= 254;
};

// Phone validation (international format)
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
  return phoneRegex.test(cleanPhone) && cleanPhone.length >= 10 && cleanPhone.length <= 16;
};

// Password strength validation
export const validatePasswordStrength = (password: string): {
  isValid: boolean;
  score: number;
  feedback: string[];
} => {
  const feedback: string[] = [];
  let score = 0;

  if (password.length < 8) {
    feedback.push('Password must be at least 8 characters long');
  } else {
    score += 1;
  }

  if (!/[a-z]/.test(password)) {
    feedback.push('Password must contain at least one lowercase letter');
  } else {
    score += 1;
  }

  if (!/[A-Z]/.test(password)) {
    feedback.push('Password must contain at least one uppercase letter');
  } else {
    score += 1;
  }

  if (!/\d/.test(password)) {
    feedback.push('Password must contain at least one number');
  } else {
    score += 1;
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    feedback.push('Password must contain at least one special character');
  } else {
    score += 1;
  }

  return {
    isValid: score >= 4,
    score,
    feedback
  };
};

// Name validation
export const isValidName = (name: string): boolean => {
  const nameRegex = /^[a-zA-Z\s\-'\.]{2,50}$/;
  return nameRegex.test(name) && name.trim().length >= 2;
};

// Date validation
export const isValidDate = (dateString: string): boolean => {
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  return date instanceof Date && !isNaN(date.getTime()) && date >= today;
};

export const isValidDateRange = (checkIn: string, checkOut: string): boolean => {
  const checkInDate = new Date(checkIn);
  const checkOutDate = new Date(checkOut);
  
  return checkOutDate > checkInDate;
};

// Rate limiting
class RateLimiter {
  private attempts: Map<string, { count: number; firstAttempt: number; lockedUntil?: number }> = new Map();

  isAllowed(key: string, type: 'login' | 'booking'): boolean {
    const config = RATE_LIMIT_CONFIG[type];
    const now = Date.now();
    const record = this.attempts.get(key);

    // Check if currently locked out
    if (record?.lockedUntil && now < record.lockedUntil) {
      return false;
    }

    // Reset if lockout period has passed
    if (record?.lockedUntil && now >= record.lockedUntil) {
      this.attempts.delete(key);
      return true;
    }

    // Check if within rate limit window
    if (record && (now - record.firstAttempt) < config.windowMs) {
      if (record.count >= config.maxAttempts) {
        // Lock out
        record.lockedUntil = now + config.lockoutMs;
        return false;
      }
      record.count += 1;
    } else {
      // First attempt or window expired
      this.attempts.set(key, { count: 1, firstAttempt: now });
    }

    return true;
  }

  getRemainingAttempts(key: string, type: 'login' | 'booking'): number {
    const config = RATE_LIMIT_CONFIG[type];
    const record = this.attempts.get(key);
    
    if (!record) return config.maxAttempts;
    
    const now = Date.now();
    if (record.lockedUntil && now < record.lockedUntil) {
      return 0;
    }
    
    if ((now - record.firstAttempt) >= config.windowMs) {
      return config.maxAttempts;
    }
    
    return Math.max(0, config.maxAttempts - record.count);
  }

  getLockoutTime(key: string, type: 'login' | 'booking'): number | null {
    const record = this.attempts.get(key);
    if (!record?.lockedUntil) return null;
    
    const now = Date.now();
    return record.lockedUntil > now ? record.lockedUntil - now : null;
  }

  reset(key: string): void {
    this.attempts.delete(key);
  }
}

export const rateLimiter = new RateLimiter();

// CSRF token generation
export const generateCSRFToken = (): string => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

// Input validation for booking form
export const validateBookingForm = (formData: any): {
  isValid: boolean;
  errors: Record<string, string>;
} => {
  const errors: Record<string, string> = {};

  // Name validation
  if (!formData.name || !isValidName(formData.name)) {
    errors.name = 'Please enter a valid name (2-50 characters, letters only)';
  }

  // Email validation
  if (!formData.email || !isValidEmail(formData.email)) {
    errors.email = 'Please enter a valid email address';
  }

  // Phone validation
  if (!formData.phone || !isValidPhone(formData.phone)) {
    errors.phone = 'Please enter a valid phone number';
  }

  // Date validation
  if (!formData.checkIn || !isValidDate(formData.checkIn)) {
    errors.checkIn = 'Please select a valid check-in date (today or later)';
  }

  if (!formData.checkOut || !isValidDate(formData.checkOut)) {
    errors.checkOut = 'Please select a valid check-out date (today or later)';
  }

  // Date range validation
  if (formData.checkIn && formData.checkOut && !isValidDateRange(formData.checkIn, formData.checkOut)) {
    errors.checkOut = 'Check-out date must be after check-in date';
  }

  // Room type validation
  if (!formData.roomType) {
    errors.roomType = 'Please select a room type';
  }

  // Guests validation
  const guests = parseInt(formData.guests);
  if (!formData.guests || isNaN(guests) || guests < 1 || guests > 10) {
    errors.guests = 'Please enter a valid number of guests (1-10)';
  }

  // Origin validation
  if (!formData.origin || formData.origin.trim().length < 2) {
    errors.origin = 'Please enter your origin (city, country)';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Input validation for login form
export const validateLoginForm = (formData: any): {
  isValid: boolean;
  errors: Record<string, string>;
} => {
  const errors: Record<string, string> = {};

  // Email validation
  if (!formData.email || !isValidEmail(formData.email)) {
    errors.email = 'Please enter a valid email address';
  }

  // Password validation
  if (!formData.password || formData.password.length < 1) {
    errors.password = 'Please enter your password';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Honeypot field for bot detection
export const createHoneypotField = (): { name: string; value: string } => {
  return {
    name: `website_${Math.random().toString(36).substring(7)}`,
    value: ''
  };
};

// Check if honeypot was filled (indicates bot)
export const isHoneypotFilled = (honeypotValue: string): boolean => {
  return honeypotValue.trim().length > 0;
};
