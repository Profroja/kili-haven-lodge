import Navigation from "@/components/Navigation";
import Gallery from "@/components/Gallery";
import FloatingButtons from "@/components/FloatingButtons";
import FloatingSocialButtons from "@/components/FloatingSocialButtons";
import ReserveButton from "@/components/ReserveButton";
import Footer from "@/components/Footer";

const GalleryPage = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <main className="pt-16">
        <Gallery />
      </main>
      
      <FloatingButtons />
      <FloatingSocialButtons />
      <ReserveButton />
      <Footer />
    </div>
  );
};

export default GalleryPage;