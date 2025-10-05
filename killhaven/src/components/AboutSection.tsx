import lodgeExterior from "@/assets/pic1.jpg";
import forestPath from "@/assets/forest-path.jpg";

const AboutSection = () => {
  return (
    <section className="py-20 px-4 bg-gradient-warm">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
          <div className="slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6">
              Welcome to Kili Haven Lodge
            </h2>
            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
              Located in Moshi, Kilimanjaro region, Kili Haven Lodge offers a comfortable 
              and welcoming stay for both business and leisure travelers. Our lodge provides a peaceful 
              retreat at the foot of Mount Kilimanjaro while maintaining easy access to Moshi's attractions and Kilimanjaro National Park.
            </p>
            <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
              Experience the warmth of Tanzanian hospitality in our clean, comfortable accommodations. 
              Whether you're visiting for Kilimanjaro climbing, exploring Moshi's cultural sites, or simply 
              passing through, we ensure a pleasant and memorable stay.
            </p>
            <div className="grid grid-cols-2 gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-2">Many</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wide">Available & Comfortable Rooms</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-2">24/7</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wide">Reception Service</div>
              </div>
            </div>
          </div>
          <div className="relative">
            <img 
              src={lodgeExterior} 
              alt="Kill Haven Lodge exterior at golden hour"
              className="rounded-lg shadow-elegant w-full"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-8 bg-card rounded-lg shadow-warm slide-up">
            <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-secondary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-2">Mountain Exploration</h3>
            <p className="text-muted-foreground">Easy access to Mount Kilimanjaro, Kilimanjaro National Park, and Moshi's cultural sites and attractions.</p>
          </div>

          <div className="text-center p-8 bg-card rounded-lg shadow-warm slide-up">
            <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-secondary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-2">Comfortable Amenities</h3>
            <p className="text-muted-foreground">Clean rooms, reliable WiFi, and essential amenities for a comfortable stay in Moshi.</p>
          </div>

          <div className="text-center p-8 bg-card rounded-lg shadow-warm slide-up">
            <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-secondary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-2">Tanzanian Hospitality</h3>
            <p className="text-muted-foreground">Experience warm, friendly service and authentic Tanzanian hospitality during your stay.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;