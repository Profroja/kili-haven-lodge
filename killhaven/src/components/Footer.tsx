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
              <div className="flex space-x-3">
                <Button variant="outline" size="sm" style={{borderColor: 'rgba(255, 215, 0, 0.3)', color: '#ffd700'}} className="hover:bg-yellow-500 hover:text-white">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                  </svg>
                </Button>
                <Button variant="outline" size="sm" style={{borderColor: 'rgba(255, 215, 0, 0.3)', color: '#ffd700'}} className="hover:bg-yellow-500 hover:text-white">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                </Button>
                <Button variant="outline" size="sm" style={{borderColor: 'rgba(255, 215, 0, 0.3)', color: '#ffd700'}} className="hover:bg-yellow-500 hover:text-white">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.097.118.112.221.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.746-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001 12.017.001z"/>
                  </svg>
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