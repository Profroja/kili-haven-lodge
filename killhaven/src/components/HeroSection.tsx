import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import BookingModal from "./BookingModal";
import lodgeExterior from "@/assets/pic1.jpg";
import r5 from "@/assets/r5.jpg";
import r3 from "@/assets/r3.jpg";
import logoKili from "@/assets/logo-kili-min.png";

const slides = [
  {
    type: "image",
    src: lodgeExterior,
    alt: "Kill Haven Lodge exterior at golden hour"
  },
  {
    type: "image", 
    src: r5,
    alt: "Kili Haven Lodge room interior"
  },
  {
    type: "image",
    src: r3,
    alt: "Kili Haven Lodge room interior"
  }
];

const HeroSection = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000); // All slides show for 5 seconds

    return () => clearInterval(timer);
  }, [currentSlide]);

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  return (
    <section className="relative h-screen overflow-hidden">
      {/* Slides */}
      {slides.map((slide, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-opacity duration-1000 ${
            index === currentSlide ? "opacity-100" : "opacity-0"
          }`}
        >
          <img
            src={slide.src}
            alt={slide.alt}
            className="w-full h-full object-cover object-top sm:object-center"
          />
        </div>
      ))}

      {/* Overlay */}
      <div className="video-overlay" />


      {/* Content */}
      <div className="relative z-10 flex items-center justify-center h-full px-4">
        <div className="text-center text-white max-w-4xl">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 fade-in">
            Kili Haven Lodge
          </h1>
          <div className="flex justify-center mb-6">
            <img 
              src={logoKili} 
              alt="Kili Haven Lodge Logo" 
              className="h-24 md:h-32 lg:h-40 w-auto"
            />
          </div>
          <p className="text-xl md:text-2xl mb-8 font-light slide-up">
            Your Cozy Escape in Moshi
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center slide-up">
            <Button 
              onClick={() => setIsBookingModalOpen(true)}
              variant="secondary" 
              size="lg" 
              className="bg-accent text-accent-foreground hover:bg-accent-light transition-all duration-300"
            >
              Reserve Your Stay
            </Button>
            <Link to="/rooms">
              <Button variant="outline" size="lg" className="border-2 border-white text-white hover:bg-white hover:text-gray-800 transition-all duration-300 bg-transparent">
                Explore Rooms
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Slide Indicators */}
      <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 flex space-x-3 z-20">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => goToSlide(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentSlide 
                ? "bg-accent scale-125" 
                : "bg-white/50 hover:bg-white/75"
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>

      {/* Navigation Arrows */}
      <button
        onClick={() => goToSlide((currentSlide - 1 + slides.length) % slides.length)}
        className="absolute left-6 top-1/2 transform -translate-y-1/2 z-20 text-white hover:text-accent transition-colors duration-300"
        aria-label="Previous slide"
      >
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      
      <button
        onClick={() => goToSlide((currentSlide + 1) % slides.length)}
        className="absolute right-6 top-1/2 transform -translate-y-1/2 z-20 text-white hover:text-accent transition-colors duration-300"
        aria-label="Next slide"
      >
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <BookingModal 
        isOpen={isBookingModalOpen} 
        onClose={() => setIsBookingModalOpen(false)} 
      />
    </section>
  );
};

export default HeroSection;