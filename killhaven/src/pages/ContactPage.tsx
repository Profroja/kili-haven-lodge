import Navigation from "@/components/Navigation";
import FloatingButtons from "@/components/FloatingButtons";
import FloatingSocialButtons from "@/components/FloatingSocialButtons";
import ReserveButton from "@/components/ReserveButton";
import Footer from "@/components/Footer";
import { Card, CardContent } from "@/components/ui/card";
import { Phone, Mail, MapPin, Clock } from "lucide-react";

const ContactPage = () => {

  return (
    <div className="min-h-screen">
      <Navigation />
      
      <main className="pt-16">
        {/* Contact Information Section */}
        <section className="py-20 px-4 bg-background">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h1 className="text-4xl md:text-5xl font-bold text-primary mb-6">
                Contact Us
              </h1>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                Get in touch with us for reservations, inquiries, or any assistance you need for your stay at Kili Haven Lodge.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
              <Card className="text-center p-6 shadow-elegant hover:shadow-forest transition-shadow duration-300">
                <CardContent className="p-0">
                  <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
                    <Phone className="w-8 h-8 text-accent-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2">Phone</h3>
                  <p className="text-muted-foreground">+255-676-626-193</p>
                </CardContent>
              </Card>

              <Card className="text-center p-6 shadow-elegant hover:shadow-forest transition-shadow duration-300">
                <CardContent className="p-0">
                  <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
                    <Mail className="w-8 h-8 text-accent-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2">Email</h3>
                  <p className="text-muted-foreground">kilihavenlodge@gmail.com</p>
                </CardContent>
              </Card>

              <Card className="text-center p-6 shadow-elegant hover:shadow-forest transition-shadow duration-300">
                <CardContent className="p-0">
                  <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
                    <MapPin className="w-8 h-8 text-accent-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2">Address</h3>
                  <p className="text-muted-foreground">Kariwa Chini Street, Moshi - Kilimanjaro</p>
                </CardContent>
              </Card>

              <Card className="text-center p-6 shadow-elegant hover:shadow-forest transition-shadow duration-300">
                <CardContent className="p-0">
                  <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
                    <Clock className="w-8 h-8 text-accent-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-primary mb-2">Hours</h3>
                  <p className="text-muted-foreground">24/7 Reception</p>
                </CardContent>
              </Card>
            </div>

            {/* Map Section */}
            <div className="max-w-4xl mx-auto">
                <Card className="shadow-elegant">
                  <CardContent className="p-0">
                    <div className="rounded-lg overflow-hidden">
                      <iframe 
                        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2707.2625147263584!2d37.3395602!3d-3.3257442000000004!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1839d95231c5cf5d%3A0x7634fd612f4befe6!2sKili%20Haven%20Lodge!5e1!3m2!1ssw!2stz!4v1757308865139!5m2!1ssw!2stz" 
                        width="100%" 
                        height="400" 
                        style={{border: 0}} 
                        allowFullScreen 
                        loading="lazy" 
                        referrerPolicy="no-referrer-when-downgrade"
                        title="Kili Haven Lodge Location"
                      />
                    </div>
                  </CardContent>
                </Card>

              <Card className="shadow-elegant mt-6">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-primary mb-4">Quick Contact</h3>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <Phone className="w-5 h-5 text-accent mr-3" />
                      <span className="text-muted-foreground">+255-676-626-193</span>
                    </div>
                    <div className="flex items-center">
                      <Mail className="w-5 h-5 text-accent mr-3" />
                      <span className="text-muted-foreground">kilihavenlodge@gmail.com</span>
                    </div>
                    <div className="flex items-center">
                      <MapPin className="w-5 h-5 text-accent mr-3" />
                      <span className="text-muted-foreground">Kariwa Chini Street, Moshi - Kilimanjaro</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
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

export default ContactPage;
