import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { submitHome, HomeData, fetchRoomTypes, RoomType } from "../services/api";
import { 
  sanitizeInput, 
  validateBookingForm, 
  rateLimiter, 
  generateCSRFToken,
  createHoneypotField,
  isHoneypotFilled
} from '../utils/security';
import { AlertCircle, Shield, Clock } from 'lucide-react';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const BookingModal = ({ isOpen, onClose }: BookingModalProps) => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loadingRoomTypes, setLoadingRoomTypes] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [csrfToken, setCsrfToken] = useState<string>('');
  const [honeypot, setHoneypot] = useState<{ name: string; value: string }>({ name: '', value: '' });
  const [isRateLimited, setIsRateLimited] = useState(false);
  const [remainingAttempts, setRemainingAttempts] = useState(10);
  const [lockoutTime, setLockoutTime] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    checkIn: "",
    checkOut: "",
    roomType: "",
    guests: "",
    idDocument: "",
    idDocumentOther: "",
    origin: "",
    purpose: "",
    specialRequests: ""
  });

  // Initialize security features when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchRoomTypesData();
      setValidationErrors({});
      setCsrfToken(generateCSRFToken());
      setHoneypot(createHoneypotField());
      setIsRateLimited(false);
      setRemainingAttempts(10);
      setLockoutTime(null);
    }
  }, [isOpen]);

  const fetchRoomTypesData = async () => {
    setLoadingRoomTypes(true);
    try {
      const data = await fetchRoomTypes();
      setRoomTypes(data);
    } catch (error) {
      console.error('Error fetching room types:', error);
      toast({
        title: "Error",
        description: "Failed to load room types. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoadingRoomTypes(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    const clientKey = `booking_${formData.email}_${window.location.hostname}`;
    if (!rateLimiter.isAllowed(clientKey, 'booking')) {
      setIsRateLimited(true);
      const lockoutTime = rateLimiter.getLockoutTime(clientKey, 'booking');
      setLockoutTime(lockoutTime);
      
      toast({
        title: "Too Many Attempts",
        description: "Too many booking attempts. Please try again later.",
        variant: "destructive",
      });
      return;
    }

    // Input validation
    const validation = validateBookingForm(formData);
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return;
    }

    setIsLoading(true);
    
    try {
      // Sanitize inputs
      const sanitizedData = {
        name: sanitizeInput(formData.name),
        email: sanitizeInput(formData.email),
        phone: sanitizeInput(formData.phone),
        checkIn: formData.checkIn,
        checkOut: formData.checkOut,
        roomType: formData.roomType,
        guests: formData.guests,
        idDocument: sanitizeInput(formData.idDocument),
        idDocumentOther: sanitizeInput(formData.idDocumentOther),
        origin: sanitizeInput(formData.origin),
        purpose: sanitizeInput(formData.purpose),
        specialRequests: sanitizeInput(formData.specialRequests)
      };

      // Find selected room type details
      const selectedRoomType = roomTypes.find(rt => rt.id.toString() === sanitizedData.roomType);
      const roomTypeName = selectedRoomType ? selectedRoomType.name : sanitizedData.roomType;
      const roomTypePrice = selectedRoomType ? `TZS ${selectedRoomType.price_per_day}/day` : '';

      // Prepare data for Django
      const bookingData: HomeData = {
        name: sanitizedData.name,
        email: sanitizedData.email,
        phone: sanitizedData.phone,
        message: `Booking Request Details:
        Check-in: ${sanitizedData.checkIn}
        Check-out: ${sanitizedData.checkOut}
        Room Type: ${roomTypeName} ${roomTypePrice}
        Number of Guests: ${sanitizedData.guests}
        Purpose of Stay: ${sanitizedData.purpose}
        ID Document: ${sanitizedData.idDocument}${sanitizedData.idDocumentOther ? ` (${sanitizedData.idDocumentOther})` : ''}
        Origin: ${sanitizedData.origin}
        Special Requests: ${sanitizedData.specialRequests || 'None'}`,
        type: 'booking'
      };

      // Update remaining attempts
      const attempts = rateLimiter.getRemainingAttempts(clientKey, 'booking');
      setRemainingAttempts(attempts);

      // Send to Django backend
      const response = await submitHome(bookingData);
      
      // Show success message with booking ID and OK button
      const successMessage = document.createElement('div');
      successMessage.innerHTML = `
        <div style="
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          font-family: system-ui, -apple-system, sans-serif;
        ">
          <div style="
            background: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            width: 90%;
          ">
            <div style="
              width: 60px;
              height: 60px;
              background: #10b981;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              margin: 0 auto 20px;
              font-size: 24px;
              color: white;
            ">✓</div>
            <h2 style="
              color: #1f2937;
              font-size: 24px;
              font-weight: 600;
              margin: 0 0 10px;
            ">Booking Submitted!</h2>
            <div style="
              background: #f3f4f6;
              padding: 15px;
              border-radius: 8px;
              margin: 15px 0;
              border-left: 4px solid #10b981;
            ">
              <p style="
                color: #374151;
                font-size: 14px;
                margin: 0 0 5px;
                font-weight: 500;
              ">Your Booking ID:</p>
              <p style="
                color: #1f2937;
                font-size: 20px;
                font-weight: 700;
                margin: 0;
                letter-spacing: 2px;
                font-family: 'Courier New', monospace;
                cursor: pointer;
                user-select: all;
              " title="Click to select all">${response.booking_id || 'N/A'}</p>
            </div>
            <p style="
              color: #6b7280;
              font-size: 16px;
              margin: 0 0 20px;
              line-height: 1.5;
            ">We'll contact you within 24 hours to confirm your reservation.</p>
            <button onclick="this.parentElement.parentElement.remove(); window.location.reload();" style="
              background: #10b981;
              color: white;
              border: none;
              padding: 12px 24px;
              border-radius: 8px;
              font-size: 16px;
              font-weight: 600;
              cursor: pointer;
              transition: background-color 0.3s ease;
            " onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">
              OK
            </button>
          </div>
        </div>
      `;
      
      document.body.appendChild(successMessage);

      // Reset form
      setFormData({
        name: "",
        email: "",
        phone: "",
        checkIn: "",
        checkOut: "",
        roomType: "",
        guests: "",
        idDocument: "",
        idDocumentOther: "",
        origin: "",
        purpose: "",
        specialRequests: ""
      });

      onClose();

    } catch (error) {
      console.error('Booking submission error:', error);
      toast({
        title: "Error",
        description: "Failed to submit booking request. Please try again or contact us directly.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    // Clear validation errors when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
    
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const formatPrice = (price: string) => {
    const numPrice = parseFloat(price);
    return new Intl.NumberFormat('en-TZ', {
      style: 'currency',
      currency: 'TZS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numPrice);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-primary text-center">
            Reserve Your Stay
          </DialogTitle>
        </DialogHeader>
        
        <Card className="border-0 shadow-none">
          <CardContent className="p-0">
            <form onSubmit={handleSubmit} className="space-y-6">
            

              {/* Rate Limiting Warning */}
              {isRateLimited && lockoutTime && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 text-red-600 mr-2" />
                    <span className="text-sm text-red-800">
                      Too many attempts. Try again in {Math.ceil(lockoutTime / (1000 * 60))} minutes.
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
                      {Object.entries(validationErrors).map(([field, error]) => (
                        <div key={field}>{error}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-primary font-medium">Full Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="Your full name"
                    className={`border-forest focus:border-accent ${validationErrors.name ? "border-red-500" : ""}`}
                    required
                    disabled={isRateLimited}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-primary font-medium">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    placeholder="your.email@example.com"
                    className="border-forest focus:border-accent"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone" className="text-primary font-medium">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange("phone", e.target.value)}
                  placeholder="0766123456"
                  className="border-forest focus:border-accent"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="checkin" className="text-primary font-medium">Check-in Date</Label>
                  <Input
                    id="checkin"
                    type="date"
                    value={formData.checkIn}
                    onChange={(e) => handleInputChange("checkIn", e.target.value)}
                    className="border-forest focus:border-accent"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="checkout" className="text-primary font-medium">Check-out Date</Label>
                  <Input
                    id="checkout"
                    type="date"
                    value={formData.checkOut}
                    onChange={(e) => handleInputChange("checkOut", e.target.value)}
                    className="border-forest focus:border-accent"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-primary font-medium">Room Type</Label>
                  <Select 
                    value={formData.roomType} 
                    onValueChange={(value) => handleInputChange("roomType", value)}
                    disabled={loadingRoomTypes}
                  >
                    <SelectTrigger className="border-forest focus:border-accent">
                      <SelectValue placeholder={loadingRoomTypes ? "Loading room types..." : "Select room type"} />
                    </SelectTrigger>
                    <SelectContent>
                      {roomTypes.map((roomType) => (
                        <SelectItem key={roomType.id} value={roomType.id.toString()}>
                          {roomType.name} - {formatPrice(roomType.price_per_day)}/day
                          {roomType.available_rooms > 0 && (
                            <span className="text-green-600 ml-2">({roomType.available_rooms} available)</span>
                          )}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {roomTypes.length === 0 && !loadingRoomTypes && (
                    <p className="text-sm text-red-500">No room types available</p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label className="text-primary font-medium">Number of Guests</Label>
                  <Select 
                    value={formData.guests} 
                    onValueChange={(value) => handleInputChange("guests", value)}
                  >
                    <SelectTrigger className="border-forest focus:border-accent">
                      <SelectValue placeholder="Select number of guests" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 Guest</SelectItem>
                      <SelectItem value="2">2 Guests</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-primary font-medium">ID Document Type</Label>
                  <Select value={formData.idDocument} onValueChange={(value) => handleInputChange("idDocument", value)}>
                    <SelectTrigger className="border-forest focus:border-accent">
                      <SelectValue placeholder="Select ID document" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="national_id">National ID</SelectItem>
                      <SelectItem value="passport">Passport</SelectItem>
                      <SelectItem value="other">Other (Please specify)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="origin" className="text-primary font-medium">Where are you coming from?</Label>
                  <Input
                    id="origin"
                    value={formData.origin}
                    onChange={(e) => handleInputChange("origin", e.target.value)}
                    placeholder="City, Country"
                    className="border-forest focus:border-accent"
                    required
                  />
                </div>
              </div>

              {formData.idDocument === "other" && (
                <div className="space-y-2">
                  <Label htmlFor="id-document-other" className="text-primary font-medium">Please specify ID document type</Label>
                  <Input
                    id="id-document-other"
                    value={formData.idDocumentOther}
                    onChange={(e) => handleInputChange("idDocumentOther", e.target.value)}
                    placeholder="e.g., Driver's License, Student ID, etc."
                    className="border-forest focus:border-accent"
                    required
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label className="text-primary font-medium">Purpose of Stay</Label>
                <Select value={formData.purpose} onValueChange={(value) => handleInputChange("purpose", value)}>
                  <SelectTrigger className="border-forest focus:border-accent">
                    <SelectValue placeholder="Select purpose of stay" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="business">Business</SelectItem>
                    <SelectItem value="leisure">Leisure</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="special-requests" className="text-primary font-medium">Special Requests</Label>
                <Textarea
                  id="special-requests"
                  value={formData.specialRequests}
                  onChange={(e) => handleInputChange("specialRequests", e.target.value)}
                  placeholder="Any special accommodations or requests..."
                  className="border-forest focus:border-accent min-h-[100px]"
                  disabled={isRateLimited}
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
                disabled={isLoading || loadingRoomTypes || isRateLimited}
                className="w-full bg-accent text-accent-foreground hover:bg-accent/90 transition-colors duration-300 py-3 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting Request...
                  </div>
                ) : isRateLimited ? (
                  'Booking Temporarily Disabled'
                ) : (
                  'Submit Reservation Request'
                )}
              </Button>
            </form>

          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
};

export default BookingModal;
