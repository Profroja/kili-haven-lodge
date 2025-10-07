import { Button } from "@/components/ui/button";
import logoKili from "@/assets/logo-kili.png";

const Footer = () => {
  return (
    <footer className="py-16" style={{backgroundColor: 'rgb(30, 56, 42)', color: '#ffd700'}}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Lodge Info */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <img 
                src={logoKili} 
                alt="Kili Haven Lodge Logo" 
                className="h-10 w-auto"
              />
              <h3 className="text-2xl font-bold">Kili Haven Lodge</h3>
            </div>
            <p className="mb-6 leading-relaxed" style={{color: 'rgba(255, 215, 0, 0.8)'}}>
              Your cozy escape in Moshi, Kilimanjaro. Experience comfort and tranquility at the foot of Mount Kilimanjaro 
              with authentic Tanzanian hospitality.
            </p>
            <div className="space-y-2" style={{color: 'rgba(255, 215, 0, 0.8)'}}>
              <p>📍 Kariwa Chini Street, Moshi - Kilimanjaro</p>
              <p>📞 +255-676-626-193</p>
              <p>✉️ kilihavenlodge@gmail.com</p>
              <p>📱 IG: @kilihaven</p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li><a href="#about" style={{color: 'rgba(255, 215, 0, 0.8)'}} className="hover:text-yellow-300 transition-colors">About Us</a></li>
              <li><a href="#rooms" style={{color: 'rgba(255, 215, 0, 0.8)'}} className="hover:text-yellow-300 transition-colors">Our Rooms</a></li>
              <li><a href="#booking" style={{color: 'rgba(255, 215, 0, 0.8)'}} className="hover:text-yellow-300 transition-colors">Reservations</a></li>
              <li><a href="#location" style={{color: 'rgba(255, 215, 0, 0.8)'}} className="hover:text-yellow-300 transition-colors">Location</a></li>
              <li><a href="/gallery" style={{color: 'rgba(255, 215, 0, 0.8)'}} className="hover:text-yellow-300 transition-colors">Gallery</a></li>
            </ul>
          </div>

          {/* Contact & Social */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Connect With Us</h4>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-3">
                {/* TripAdvisor - Text Button */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white hover:bg-gray-50 border-gray-300 text-green-600 hover:text-green-700 font-medium"
                  asChild
                >
                  <a href="https://www.tripadvisor.com/Hotel_Review-g317084-d33419730-Reviews-Kili_Haven_Lodge-Moshi_Kilimanjaro_Region.html" target="_blank" rel="noopener noreferrer">
                    TripAdvisor
                  </a>
                </Button>

  
              </div>
              <p className="text-sm" style={{color: 'rgba(255, 215, 0, 0.6)'}}>
                Follow us for updates and Kilimanjaro inspiration
              </p>
            </div>
          </div>
        </div>

        <div className="border-t mt-12 pt-8 text-center" style={{borderColor: 'rgba(255, 215, 0, 0.2)', color: 'rgba(255, 215, 0, 0.6)'}}>
          <p>&copy; 2024 Kili Haven Lodge. All rights reserved. | Privacy Policy | Terms of Service</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;