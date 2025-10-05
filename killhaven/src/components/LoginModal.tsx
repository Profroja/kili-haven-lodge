import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from '../hooks/useLogin';
import { LoginData } from '../services/api';
import { useToast } from "@/hooks/use-toast";
import { 
  sanitizeInput, 
  validateLoginForm, 
  rateLimiter, 
  generateCSRFToken,
  createHoneypotField,
  isHoneypotFilled
} from '../utils/security';
import { AlertCircle, Shield, Clock } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal = ({ isOpen, onClose }: LoginModalProps) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState<LoginData>({
    email: '',
    password: ''
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [csrfToken, setCsrfToken] = useState<string>('');
  const [honeypot, setHoneypot] = useState<{ name: string; value: string }>({ name: '', value: '' });
  const [isRateLimited, setIsRateLimited] = useState(false);
  const [remainingAttempts, setRemainingAttempts] = useState(5);
  const [lockoutTime, setLockoutTime] = useState<number | null>(null);
  
  const { handleLogin, isLoading, error, clearError } = useLogin();

  // Initialize security features when modal opens
  useEffect(() => {
    if (isOpen) {
      clearError();
      setValidationErrors({});
      setCsrfToken(generateCSRFToken());
      setHoneypot(createHoneypotField());
      setIsRateLimited(false);
      setRemainingAttempts(5);
      setLockoutTime(null);
    }
  }, [isOpen, clearError]);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});
    
    // Check honeypot (bot detection)
    if (isHoneypotFilled(honeypot.value)) {
      toast({
        title: "Security Alert",
        description: "Suspicious activity detected. Please try again.",
        variant: "destructive",
      });
      return;
    }

    // Rate limiting check
    const clientKey = `login_${formData.email}_${window.location.hostname}`;
    if (!rateLimiter.isAllowed(clientKey, 'login')) {
      setIsRateLimited(true);
      const lockoutTime = rateLimiter.getLockoutTime(clientKey, 'login');
      setLockoutTime(lockoutTime);
      
      toast({
        title: "Too Many Attempts",
        description: "Too many login attempts. Please try again later.",
        variant: "destructive",
      });
      return;
    }

    // Input validation
    const validation = validateLoginForm(formData);
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return;
    }

    // Sanitize inputs
    const sanitizedData = {
      email: sanitizeInput(formData.email),
      password: formData.password, // Don't sanitize password as it might contain special chars
    };

    // Update remaining attempts
    const attempts = rateLimiter.getRemainingAttempts(clientKey, 'login');
    setRemainingAttempts(attempts);

    // Clear form function to pass to handleLogin
    const clearForm = () => {
      setFormData({ email: '', password: '' });
      setValidationErrors({});
      rateLimiter.reset(clientKey);
    };

    await handleLogin(sanitizedData, clearForm);
  };

  const handleClose = () => {
    setFormData({ email: '', password: '' });
    clearError();
    onClose();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Clear validation errors when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const formatLockoutTime = (ms: number): string => {
    const minutes = Math.ceil(ms / (1000 * 60));
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-center">Login</DialogTitle>
            <DialogDescription className="text-center">
              Enter your credentials to access the staff dashboard
            </DialogDescription>
          </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          

          {/* Rate Limiting Warning */}
          {isRateLimited && lockoutTime && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <Clock className="h-4 w-4 text-red-600 mr-2" />
                <span className="text-sm text-red-800">
                  Account temporarily locked. Try again in {formatLockoutTime(lockoutTime)}.
                </span>
              </div>
            </div>
          )}

          {/* Validation Errors */}
          {Object.keys(validationErrors).length > 0 && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-4 w-4 text-red-600 mr-2 mt-0.5" />
                <div className="text-sm text-red-800">
                  {Object.values(validationErrors).map((error, index) => (
                    <div key={index}>{error}</div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
              name="email"
                type="email"
              value={formData.email}
              onChange={handleInputChange}
                required
              disabled={isLoading || isRateLimited}
              placeholder="Enter your email"
              className={validationErrors.email ? "border-red-500" : ""}
              />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
              <Input
                id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading || isRateLimited}
                placeholder="Enter your password"
                className={validationErrors.password ? "border-red-500" : ""}
            />
          </div>

          {/* Honeypot field (hidden) */}
          <input
            type="text"
            name={honeypot.name}
            value={honeypot.value}
            onChange={(e) => setHoneypot(prev => ({ ...prev, value: e.target.value }))}
            style={{ display: 'none' }}
            tabIndex={-1}
            autoComplete="off"
          />

          {/* CSRF Token (hidden) */}
          <input type="hidden" name="csrf_token" value={csrfToken} />
          

          
          <Button
            type="submit"
            disabled={isLoading || !formData.email || !formData.password || isRateLimited}
            className="w-full"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Signing In...
              </div>
            ) : isRateLimited ? (
              'Account Locked'
            ) : (
              'Sign In'
            )}
          </Button>
        </form>

       
      </DialogContent>
    </Dialog>
  );
};

export default LoginModal;