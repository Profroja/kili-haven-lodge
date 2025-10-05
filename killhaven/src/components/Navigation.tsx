import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Link, useLocation } from "react-router-dom";
import LoginModal from "@/components/LoginModal";
import BookingModal from "@/components/BookingModal";
import logoKili from "@/assets/logo-kili.png";

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const location = useLocation();

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-sm border-b" style={{backgroundColor: 'rgb(30, 56, 42)'}}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center space-x-3">
            <img 
              src={logoKili} 
              alt="Kili Haven Lodge Logo" 
              className="h-8 w-auto"
            />
            <h1 className="text-xl font-bold" style={{color: '#ffd700'}}>Kili Haven Lodge</h1>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              {location.pathname === '/' ? (
                <>
                  <button 
                    onClick={() => scrollToSection('hero')}
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
                  >
                    Home
                  </button>
                  <button 
                    onClick={() => scrollToSection('about')}
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
                  >
                    About
                  </button>
                </>
              ) : (
                <>
                  <Link 
                    to="/"
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
                  >
                    Home
                  </Link>
                  <Link 
                    to="/#about"
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
                  >
                    About
                  </Link>
                </>
              )}
              <Link 
                to="/rooms"
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
              >
                Our Rooms
              </Link>
              <Link 
                to="/gallery"
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
              >
                Gallery
              </Link>
              <Link 
                to="/contact"
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
              >
                Contact Us
              </Link>
              <button
                onClick={() => setLoginOpen(true)}
                    style={{color: '#ffd700'}} className="hover:text-yellow-300 transition-colors duration-200"
              >
                Login
              </button>
            </div>
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Button 
              onClick={() => setBookingOpen(true)}
              style={{backgroundColor: '#ffd700', color: '#1a4d1a'}} className="hover:bg-yellow-300 transition-colors duration-300"
            >
              Reserve Now
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              style={{color: '#ffd700'}} className="hover:text-yellow-300 p-2"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1" style={{backgroundColor: 'rgb(30, 56, 42)'}}>
              {location.pathname === '/' ? (
                <>
                  <button 
                    onClick={() => scrollToSection('hero')}
                    style={{color: '#ffd700'}} className="block w-full text-left px-3 py-2 hover:text-yellow-300 transition-colors duration-200"
                  >
                    Home
                  </button>
                  <button 
                    onClick={() => scrollToSection('about')}
                    style={{color: '#ffd700'}} className="block w-full text-left px-3 py-2 hover:text-yellow-300 transition-colors duration-200"
                  >
                    About
                  </button>
                </>
              ) : (
                <>
                  <Link 
                    to="/"
                    style={{color: '#ffd700'}} className="block w-full text-left px-3 py-2 hover:text-yellow-300 transition-colors duration-200"
                    onClick={() => setIsOpen(false)}
                  >
                    Home
                  </Link>
                  <Link 
                    to="/#about"
                    style={{color: '#ffd700'}} className="block w-full text-left px-3 py-2 hover:text-yellow-300 transition-colors duration-200"
                    onClick={() => setIsOpen(false)}
                  >
                    About
                  </Link>
                </>
              )}
              <Link 
                to="/rooms"
                className="block w-full text-left px-3 py-2 text-white hover:text-yellow-400 transition-colors duration-200"
                onClick={() => setIsOpen(false)}
              >
                Our Rooms
              </Link>
              <Link 
                to="/gallery"
                className="block w-full text-left px-3 py-2 text-white hover:text-yellow-400 transition-colors duration-200"
                onClick={() => setIsOpen(false)}
              >
                Gallery
              </Link>
              <Link 
                to="/contact"
                className="block w-full text-left px-3 py-2 text-white hover:text-yellow-400 transition-colors duration-200"
                onClick={() => setIsOpen(false)}
              >
                Contact Us
              </Link>
              <button
                onClick={() => {
                  setLoginOpen(true);
                  setIsOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-white hover:text-yellow-400 transition-colors duration-200"
              >
                Login
              </button>
            </div>
          </div>
        )}
      </div>
      
      <LoginModal isOpen={loginOpen} onClose={() => setLoginOpen(false)} />
      <BookingModal isOpen={bookingOpen} onClose={() => setBookingOpen(false)} />
    </nav>
  );
};

export default Navigation;