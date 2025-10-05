import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import r1 from "@/assets/r1.jpg";
import r2 from "@/assets/r2.jpg";
import r3 from "@/assets/r3.jpg";

const rooms = [
  {
    id: 1,
    name: "Twin Haven Room",
    image: r1,
    price: "TZS 50,000",
    description: "Comfortable twin beds with modern amenities. Perfect for business travelers or friends sharing.",
    amenities: ["Twin Beds", "Free Wi-Fi", "Work Desk", "Basic Toiletries & Daily Cleaning", "Hot Showers"],
    size: "Standard"
  },
  {
    id: 2,
    name: "Cozy Double Room", 
    image: r2,
    price: "TZS 50,000",
    description: "A cozy double room with all essential amenities for a comfortable stay at the foot of Mount Kilimanjaro.",
    amenities: ["Cozy Bed with Fresh Linens", "Breakfast Included for 2 Guests", "Complimentary Bottled Water", "Complementary Welcome Drink", "Full Toiletries", "Free Wi-Fi and Work Desk", "Hot Showers"],
    size: "Standard"
  },
  {
    id: 3,
    name: "Budget Haven Room",
    image: r3,
    price: "TZS 30,000", 
    description: "Affordable accommodation with basic amenities for budget-conscious travelers exploring Kilimanjaro.",
    amenities: ["Free Wi-Fi", "Work Desk", "Basic Toiletries & Daily Cleaning", "Hot Showers"],
    size: "Compact"
  }
];

const RoomsSection = () => {
  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6 slide-up">
            Our Rooms
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto slide-up">
            Choose from our comfortable accommodations at the foot of Mount Kilimanjaro, designed for both business and leisure travelers. 
            All rates include breakfast and taxes.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {rooms.map((room, index) => (
            <Card key={room.id} className="overflow-hidden shadow-elegant hover:shadow-forest transition-shadow duration-300 slide-up">
              <div className="relative overflow-hidden">
                <img 
                  src={room.image} 
                  alt={room.name}
                  className="w-full h-64 object-cover transition-transform duration-300 hover:scale-105"
                />
                <div className="absolute top-4 right-4 bg-accent text-accent-foreground px-3 py-1 rounded-full font-semibold">
                  {room.price}/night
                </div>
              </div>
              
              <CardContent className="p-6">
                <h3 className="text-2xl font-semibold text-primary mb-2">{room.name}</h3>
                <p className="text-muted-foreground mb-4 text-sm">{room.size}</p>
                <p className="text-foreground mb-6 leading-relaxed">{room.description}</p>
                
                <div className="mb-6">
                  <h4 className="font-semibold text-primary mb-3">Amenities</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {room.amenities.map((amenity, idx) => (
                      <div key={idx} className="flex items-center text-sm text-muted-foreground">
                        <div className="w-2 h-2 bg-accent rounded-full mr-2"></div>
                        {amenity}
                      </div>
                    ))}
                  </div>
                </div>

                <Button className="w-full bg-secondary text-secondary-foreground hover:bg-secondary-light transition-colors duration-300">
                  Reserve This Room
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default RoomsSection;