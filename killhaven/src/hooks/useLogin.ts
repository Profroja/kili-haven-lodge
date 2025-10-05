import { useState } from 'react';
import { submitLogin, LoginData, LoginResponse } from '../services/api';
import Swal from 'sweetalert2';

export const useLogin = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (loginData: LoginData, onError?: () => void) => {
    setIsLoading(true);
    setError(null);

    try {
      const response: LoginResponse = await submitLogin(loginData);
      console.log('Response received in useLogin:', response);
      console.log('Response status:', response.status);
      
      if (response.status === 'success') {
        console.log('Login successful, showing SweetAlert');
        
        // Show SweetAlert success message
        Swal.fire({
          title: 'Login Successful!',
          text: `Welcome ${response.role_display || response.user?.role_display || 'User'}! Redirecting...`,
          icon: 'success',
          confirmButtonText: 'Continue',
          showConfirmButton: false,
          timer: 2000,
          timerProgressBar: true,
          allowOutsideClick: false,
          allowEscapeKey: false,
          didOpen: () => {
            // Redirect based on role after showing the alert
            const role = response.role || response.user?.role;
            setTimeout(() => {
              if (role === 'manager') {
                window.location.href = 'https://kilihavenlodge.co.tz/manager/dashboard/';
              } else {
                window.location.href = 'https://kilihavenlodge.co.tz/staff/dashboard/';
              }
            }, 2000);
          }
        });
      } else {
        // Handle error response from API
        let errorMessage = 'Invalid credentials. Please try again.';
        
        // Map specific server errors to user-friendly messages
        if (response.message) {
          if (response.message.toLowerCase().includes('user not found') || 
              response.message.toLowerCase().includes('invalid credentials') ||
              response.message.toLowerCase().includes('incorrect') ||
              response.message.toLowerCase().includes('wrong password')) {
            errorMessage = 'Invalid credentials. Please try again.';
          } else {
            errorMessage = response.message;
          }
        }
        
        // Show SweetAlert for error
        Swal.fire({
          title: 'Login Failed',
          text: errorMessage,
          icon: 'error',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true,
          allowOutsideClick: false,
          allowEscapeKey: true
        }).then(() => {
          // Clear form after alert closes
          if (onError) {
            onError();
          }
        });
        
        console.error('Login failed with response:', response);
      }
    } catch (error) {
      console.error('Login failed:', error);
      
      // Show SweetAlert for network error
      Swal.fire({
        title: 'Connection Error',
        text: 'Network error. Please check your connection and try again.',
        icon: 'error',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        allowOutsideClick: false,
        allowEscapeKey: true
      }).then(() => {
        // Clear form after alert closes
        if (onError) {
          onError();
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  return {
    handleLogin,
    isLoading,
    error,
    clearError: () => setError(null)
  };
};
