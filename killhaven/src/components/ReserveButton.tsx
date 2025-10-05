import { useState } from "react";
import { Button } from "@/components/ui/button";
import BookingModal from "./BookingModal";

const ReserveButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div className="fixed bottom-8 right-8 z-50">
        <Button
          onClick={() => setIsModalOpen(true)}
          className="bg-accent text-accent-foreground hover:bg-accent/90 shadow-elegant hover:shadow-forest transition-all duration-300 px-8 py-4 text-lg font-semibold rounded-full animate-pulse hover:animate-none"
        >
          Reserve Now
        </Button>
      </div>
      
      <BookingModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </>
  );
};

export default ReserveButton;