import { useState } from "react";
import Navigation from "@/components/Navigation";
import FloatingButtons from "@/components/FloatingButtons";
import FloatingSocialButtons from "@/components/FloatingSocialButtons";
import ReserveButton from "@/components/ReserveButton";
import Footer from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Wifi, Car, Coffee, Utensils, Tv, Wind } from "lucide-react";

import r1 from "@/assets/r1.jpg";
import r2 from "@/assets/r2.jpg";
import r3 from "@/assets/r3.jpg";
import r4 from "@/assets/r4.jpg";
import r5 from "@/assets/r5.jpg";
import r6 from "@/assets/r6.jpg";
import r7 from "@/assets/r7.jpg";
import v1 from "@/assets/v1.jpg";
import v2 from "@/assets/v2.jpg";
import v3 from "@/assets/v3.jpg";

const rooms = [
  {
    id: 1,
    name: "Twin Haven Room",
    images: [r1, r4, v1],
    price: "TZS 50,000",
    description: "Comfortable twin beds with modern amenities. Perfect for business travelers or friends sharing.",
    amenities: ["Twin Beds", "Free Wi-Fi", "Work Desk", "Basic Toiletries & Daily Cleaning", "Hot Showers"],
    size: "Standard",
    icons: [Wifi, Wind, Coffee, Tv]
  },
  {
    id: 2,
    name: "Cozy Double Room",
    images: [r2, r5, v2],
    price: "TZS 50,000", 
    description: "A cozy double room with all essential amenities for a comfortable stay at the foot of Mount Kilimanjaro.",
    amenities: ["Cozy Bed with Fresh Linens", "Breakfast Included for 2 Guests", "Complimentary Bottled Water", "Complementary Welcome Drink", "Full Toiletries", "Free Wi-Fi and Work Desk", "Hot Showers"],
    size: "Standard",
    icons: [Wifi, Utensils, Car, Wind]
  },
  {
    id: 3,
    name: "Budget Haven Room",
    images: [r3, r6, v3],
    price: "TZS 30,000",
    description: "Affordable accommodation with basic amenities for budget-conscious travelers exploring Kilimanjaro.",
    amenities: ["Free Wi-Fi", "Work Desk", "Basic Toiletries & Daily Cleaning", "Hot Showers"],
    size: "Compact",
    icons: [Wifi, Utensils, Wind, Tv]
  }
];

const RoomCarousel = ({ images, roomName }: { images: string[], roomName: string }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % images.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="relative w-full h-64 overflow-hidden rounded-lg">
      <div 
        className="flex transition-transform duration-500 ease-in-out h-full"
        style={{ transform: `translateX(-${currentSlide * 100}%)` }}
      >
        {images.map((image, index) => (
          <img
            key={index}
            src={image}
            alt={`${roomName} - Image ${index + 1}`}
            className="w-full h-full object-cover flex-shrink-0"
          />
        ))}
      </div>
      
      <button
        onClick={prevSlide}
        className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>
      
      <button
        onClick={nextSlide}
        className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
      >
        <ChevronRight className="w-4 h-4" />
      </button>

      <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {images.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-2 h-2 rounded-full transition-colors ${
              currentSlide === index ? 'bg-white' : 'bg-white/50'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

const RoomsPage = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <main className="pt-16">
        <section className="py-20 px-4 bg-background">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h1 className="text-4xl md:text-5xl font-bold text-primary mb-6">
                Our Rooms
              </h1>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                Choose from our comfortable accommodations at the foot of Mount Kilimanjaro, designed for both business and leisure travelers. 
                All rates include breakfast and taxes.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
              {rooms.map((room) => (
                <Card key={room.id} className="overflow-hidden shadow-elegant hover:shadow-forest transition-all duration-500">
                  <CardContent className="p-0">
                    <RoomCarousel images={room.images} roomName={room.name} />
                    
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <CardTitle className="text-xl font-bold text-primary mb-2">{room.name}</CardTitle>
                          <p className="text-sm text-muted-foreground">{room.size}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-accent">{room.price}</p>
                          <p className="text-sm text-muted-foreground">per night</p>
                        </div>
                      </div>
                      
                      <p className="text-muted-foreground mb-4">{room.description}</p>
                      
                      <div className="grid grid-cols-2 gap-2 mb-6">
                        {room.amenities.map((amenity, index) => {
                          const Icon = room.icons[index] || Wifi;
                          return (
                            <div key={amenity} className="flex items-center space-x-2">
                              <Icon className="w-4 h-4 text-accent" />
                              <span className="text-sm text-muted-foreground">{amenity}</span>
                            </div>
                          );
                        })}
                      </div>
                      
                      <Button className="w-full bg-accent hover:bg-accent-light text-accent-foreground">
                        Reserve This Room
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>
      </main>
      
      <FloatingButtons />
      <FloatingSocialButtons />
      <ReserveButton />
      <Footer />
    </div>
  );
};

export default RoomsPage;