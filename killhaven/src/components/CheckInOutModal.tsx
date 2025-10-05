import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { CheckCircle, XCircle, Clock, User, Calendar, MapPin, Phone, Mail } from "lucide-react";
import { 
  fetchBookingDetails, 
  checkOutBooking, 
  cancelBooking,
  BookingDetails 
} from "@/services/bookingApi";


interface CheckInOutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CheckInOutModal = ({ isOpen, onClose }: CheckInOutModalProps) => {
  const { toast } = useToast();
  const [bookingId, setBookingId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [bookingDetails, setBookingDetails] = useState<BookingDetails | null>(null);
  const [actionType, setActionType] = useState<'checkout' | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const handleBookingLookup = async () => {
    if (!bookingId.trim()) {
      setErrorMessage("Please enter a booking ID");
      return;
    }

    setIsLoading(true);
    setErrorMessage(""); // Clear any previous error
    try {
      // Fetch booking details from Django backend
      const booking = await fetchBookingDetails(bookingId);
      setBookingDetails(booking);
      
      // Determine action type based on status
      if (booking.status === 'checked_in') {
        setActionType('checkout');
      }

    } catch (error) {
      console.error('Error fetching booking details:', error);
      const errorMsg = error instanceof Error ? error.message : "Booking not found. Please check your booking ID and try again.";
      setErrorMessage(errorMsg);
      setBookingDetails(null);
    } finally {
      setIsLoading(false);
    }
  };


  const handleCheckOut = async () => {
    if (!bookingDetails) return;

    setIsLoading(true);
    try {
      // Call Django backend to check out the guest
      await checkOutBooking(bookingDetails.booking_id);
      
      toast({
        title: "Check-out Successful!",
        description: `Thank you for staying with us, ${bookingDetails.guest_name}! We hope you enjoyed your stay.`,
      });

      // Update booking status
      setBookingDetails(prev => prev ? { ...prev, status: 'checked_out' } : null);
      setActionType(null);

    } catch (error) {
      console.error('Check-out error:', error);
      toast({
        title: "Error",
        description: "Failed to process check-out. Please try again or contact reception.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelReservation = async () => {
    if (!bookingDetails) return;

    setIsLoading(true);
    try {
      // Call Django backend to cancel the booking
      await cancelBooking(bookingDetails.booking_id);
      
      toast({
        title: "Reservation Cancelled",
        description: "Your reservation has been successfully cancelled.",
      });

      // Update booking status
      setBookingDetails(prev => prev ? { ...prev, status: 'cancelled' } : null);
      setActionType(null);

    } catch (error) {
      console.error('Cancellation error:', error);
      toast({
        title: "Error",
        description: "Failed to cancel reservation. Please contact us directly.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetModal = () => {
    setBookingId("");
    setBookingDetails(null);
    setActionType(null);
    setErrorMessage("");
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'checked_in':
        return <Clock className="h-5 w-5 text-blue-500" />;
      case 'checked_out':
        return <CheckCircle className="h-5 w-5 text-gray-500" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending Confirmation';
      case 'confirmed':
        return 'Confirmed';
      case 'checked_in':
        return 'Checked In';
      case 'checked_out':
        return 'Checked Out';
      case 'cancelled':
        return 'Cancelled';
      default:
        return 'Unknown';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-primary text-center">
            Check Out / Manage Reservation
          </DialogTitle>
        </DialogHeader>
        
        <Card className="border-0 shadow-none">
          <CardContent className="p-0">
            {!bookingDetails ? (
              // Booking ID Input Form
              <div className="space-y-6">
                <div className="text-center">
                  <p className="text-gray-600 mb-4">
                    Enter your booking ID to check out or view your reservation status.
                  </p>
                </div>

                {/* Error Message Display */}
                {errorMessage && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center">
                      <XCircle className="h-5 w-5 text-red-500 mr-2" />
                      <p className="text-red-700 font-medium">{errorMessage}</p>
                    </div>
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="booking-id" className="text-primary font-medium">
                    Booking ID
                  </Label>
                  <Input
                    id="booking-id"
                    value={bookingId}
                    onChange={(e) => {
                      setBookingId(e.target.value);
                      if (errorMessage) setErrorMessage(""); // Clear error when user starts typing
                    }}
                    placeholder="Enter your booking ID (e.g., KH-2024-001)"
                    className="border-forest focus:border-accent"
                    onKeyPress={(e) => e.key === 'Enter' && handleBookingLookup()}
                  />
                </div>

                <Button 
                  onClick={handleBookingLookup}
                  disabled={isLoading || !bookingId.trim()}
                  className="w-full bg-accent text-accent-foreground hover:bg-accent/90 transition-colors duration-300 py-3 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Looking up booking...
                    </div>
                  ) : (
                    'Look Up Booking'
                  )}
                </Button>
              </div>
            ) : (
              // Booking Details and Actions
              <div className="space-y-6">
                {/* Booking Status Header */}
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(bookingDetails.status)}
                    <span className="font-semibold text-gray-700">
                      {getStatusText(bookingDetails.status)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Booking ID: {bookingDetails.booking_id}
                  </div>
                </div>

                {/* Guest Information */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <h3 className="font-semibold text-primary flex items-center">
                      <User className="h-4 w-4 mr-2" />
                      Guest Information
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <Mail className="h-4 w-4 mr-2 text-gray-400" />
                        {bookingDetails.email}
                      </div>
                      <div className="flex items-center">
                        <Phone className="h-4 w-4 mr-2 text-gray-400" />
                        {bookingDetails.phone}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h3 className="font-semibold text-primary flex items-center">
                      <Calendar className="h-4 w-4 mr-2" />
                      Stay Details
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                        {bookingDetails.room_type}
                      </div>
                      <div>
                        <strong>Check-in:</strong> {formatDate(bookingDetails.check_in_date)}
                      </div>
                      <div>
                        <strong>Check-out:</strong> {formatDate(bookingDetails.check_out_date)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Special Requests */}
                {bookingDetails.special_requests && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-1">Special Requests</h4>
                    <p className="text-sm text-blue-700">{bookingDetails.special_requests}</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  {actionType === 'checkout' && (
                    <Button 
                      onClick={handleCheckOut}
                      disabled={isLoading}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      {isLoading ? 'Processing...' : 'Check Out'}
                    </Button>
                  )}

                  {bookingDetails.status === 'confirmed' && (
                    <Button 
                      onClick={handleCancelReservation}
                      disabled={isLoading}
                      variant="destructive"
                      className="flex-1"
                    >
                      {isLoading ? 'Cancelling...' : 'Cancel Reservation'}
                    </Button>
                  )}

                  <Button 
                    onClick={resetModal}
                    variant="outline"
                    className="flex-1"
                  >
                    Look Up Another Booking
                  </Button>
                </div>

                {/* Help Text */}
                <div className="text-center text-sm text-gray-500 space-y-2">
                  <p>Need help? Contact our reception at +255 123 456 789</p>
                  {bookingDetails?.status === 'confirmed' && (
                    <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <p className="text-yellow-800 font-medium">
                        ℹ️ Check-in is handled at our front desk upon arrival
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
};

export default CheckInOutModal;
