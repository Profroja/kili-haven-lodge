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
                
                {/* Twitter */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white hover:bg-gray-50 border-gray-300"
                  asChild
                >
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="#1DA1F2" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                    </svg>
                  </a>
                </Button>
                
                {/* Facebook */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white hover:bg-gray-50 border-gray-300"
                  asChild
                >
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </a>
                </Button>
                
                {/* Instagram */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white hover:bg-gray-50 border-gray-300"
                  asChild
                >
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <defs>
                        <linearGradient id="instagram-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#833AB4"/>
                          <stop offset="50%" stopColor="#E1306C"/>
                          <stop offset="100%" stopColor="#F77737"/>
                        </linearGradient>
                      </defs>
                      <path fill="url(#instagram-gradient)" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </a>
                </Button>
                
                {/* Email */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-white hover:bg-gray-50 border-gray-300"
                  asChild
                >
                  <a href="mailto:kilihavenlodge@gmail.com">
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="#EA4335" d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-.904.732-1.636 1.636-1.636h3.819l6.545 4.91 6.545-4.91h3.819c.904 0 1.636.732 1.636 1.636z"/>
                    </svg>
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