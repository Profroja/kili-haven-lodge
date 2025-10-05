import Navigation from "@/components/Navigation";
import HeroSection from "@/components/HeroSection";
import AboutSection from "@/components/AboutSection";
import RoomsSection from "@/components/RoomsSection";
import ReserveButton from "@/components/ReserveButton";
import FloatingButtons from "@/components/FloatingButtons";
import FloatingSocialButtons from "@/components/FloatingSocialButtons";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <main>
        <div id="hero">
          <HeroSection />
        </div>
        
        <div id="about">
          <AboutSection />
        </div>
        
        <div id="rooms">
          <RoomsSection />
        </div>
        
        <div id="location">
          <section className="py-20 px-4 bg-background">
            <div className="max-w-7xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6 slide-up">
                  Our Location
                </h2>
                <p className="text-xl text-muted-foreground max-w-3xl mx-auto slide-up">
                  Find us in Moshi, Kilimanjaro region. We're conveniently located at the foot of Mount Kilimanjaro for both business and leisure travelers.
                </p>
              </div>
              
              <div className="rounded-lg overflow-hidden shadow-elegant">
                <iframe 
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2707.2625147263584!2d37.3395602!3d-3.3257442000000004!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1839d95231c5cf5d%3A0x7634fd612f4befe6!2sKili%20Haven%20Lodge!5e1!3m2!1ssw!2stz!4v1757308865139!5m2!1ssw!2stz" 
                  width="100%" 
                  height="450" 
                  style={{border: 0}} 
                  allowFullScreen 
                  loading="lazy" 
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Kili Haven Lodge Location"
                />
              </div>
            </div>
          </section>
        </div>
      </main>
      
      <ReserveButton />
      <FloatingButtons />
      <FloatingSocialButtons />
      <Footer />
    </div>
  );
};

export default Index;
