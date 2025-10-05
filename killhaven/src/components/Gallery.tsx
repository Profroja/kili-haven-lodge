import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import kiliHavenVideo from "@/assets/kili-haven-video.mp4";
import n1 from "@/assets/n1.jpg";
import n2 from "@/assets/n2.jpg";
import pic1 from "@/assets/pic1.jpg";
import pic2 from "@/assets/pic2.jpg";
import r1 from "@/assets/r1.jpg";
import r2 from "@/assets/r2.jpg";
import r3 from "@/assets/r3.jpg";
import r4 from "@/assets/r4.jpg";
import r5 from "@/assets/r5.jpg";
import r6 from "@/assets/r6.jpg";
import r7 from "@/assets/r7.jpg";
import v1 from "@/assets/v1.jpg";
import v2 from "@/assets/v2.jpg";
import v3 from "@/assets/v3.jpg";
import v4 from "@/assets/v4.jpg";
import v5 from "@/assets/v5.jpg";
import v6 from "@/assets/v6.jpg";
import v7 from "@/assets/v7.jpg";
import v8 from "@/assets/v8.jpg";

const galleryItems = [
  {
    type: "video",
    src: kiliHavenVideo,
    title: "Kili Haven Lodge Video"
  },
  {
    type: "image",
    src: n1,
    title: "Lodge View 1"
  },
  {
    type: "image",
    src: n2,
    title: "Lodge View 2"
  },
  {
    type: "image",
    src: pic1,
    title: "Lodge Picture 1"
  },
  {
    type: "image",
    src: pic2,
    title: "Lodge Picture 2"
  },
  {
    type: "image",
    src: r1,
    title: "Room 1"
  },
  {
    type: "image",
    src: r2,
    title: "Room 2"
  },
  {
    type: "image",
    src: r3,
    title: "Room 3"
  },
  {
    type: "image",
    src: r4,
    title: "Room 4"
  },
  {
    type: "image",
    src: r5,
    title: "Room 5"
  },
  {
    type: "image",
    src: r6,
    title: "Room 6"
  },
  {
    type: "image",
    src: r7,
    title: "Room 7"
  },
  {
    type: "image",
    src: v1,
    title: "View 1"
  },
  {
    type: "image",
    src: v2,
    title: "View 2"
  },
  {
    type: "image",
    src: v3,
    title: "View 3"
  },
  {
    type: "image",
    src: v4,
    title: "View 4"
  },
  {
    type: "image",
    src: v5,
    title: "View 5"
  },
  {
    type: "image",
    src: v6,
    title: "View 6"
  },
  {
    type: "image",
    src: v7,
    title: "View 7"
  },
  {
    type: "image",
    src: v8,
    title: "View 8"
  }
];

const Gallery = () => {
  const [selectedItem, setSelectedItem] = useState<{type: string, src: string} | null>(null);

  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6 slide-up">
            Gallery
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto slide-up">
            Discover the beauty and comfort of Kili Haven Lodge through our gallery showcasing our rooms, facilities, and surroundings.
          </p>
        </div>

        {/* Gallery Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {galleryItems.map((item, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-lg shadow-elegant hover:shadow-forest transition-all duration-500 cursor-pointer slide-up"
              onClick={() => setSelectedItem({type: item.type, src: item.src})}
            >
              {item.type === "image" ? (
                <img
                  src={item.src}
                  alt={item.title}
                  className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                />
              ) : (
                <video
                  src={item.src}
                  className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500"
                  muted
                  loop
                  playsInline
                />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute bottom-4 left-4">
                  <h3 className="text-white font-semibold text-lg">{item.title}</h3>
                  <p className="text-white/80 text-sm">{item.type === "video" ? "Video" : "Image"}</p>
                </div>
              </div>
              <div className="absolute top-4 right-4 bg-accent text-accent-foreground px-2 py-1 rounded-full text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                {item.type === "video" ? "Play" : "View"}
              </div>
            </div>
          ))}
        </div>

        {/* Media Modal */}
        <Dialog open={!!selectedItem} onOpenChange={() => setSelectedItem(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] p-0">
            <DialogHeader className="sr-only">
              <DialogTitle>Gallery Media</DialogTitle>
            </DialogHeader>
            {selectedItem && (
              selectedItem.type === "image" ? (
                <img
                  src={selectedItem.src}
                  alt="Gallery view"
                  className="w-full h-full object-contain rounded-lg"
                />
              ) : (
                <video
                  src={selectedItem.src}
                  className="w-full h-full object-contain rounded-lg"
                  controls
                  autoPlay
                  loop
                  playsInline
                />
              )
            )}
          </DialogContent>
        </Dialog>
      </div>
    </section>
  );
};

export default Gallery;