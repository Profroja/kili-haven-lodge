import { Button } from "@/components/ui/button";

const FloatingButtons = () => {
  return (
    <div className="fixed top-20 left-6 z-50">
      {/* Free WiFi Button */}
      <div className="relative">
        <Button 
          size="sm" 
          className="bg-green-600 text-white hover:bg-green-700 transition-all duration-300 shadow-lg hover:shadow-xl px-4 py-2 rounded-full border-2 border-green-400"
        >
          <svg className="w-4 h-4 mr-2 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
            <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.07 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
          </svg>
          Free WiFi
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full"></div>
        </Button>
      </div>
    </div>
  );
};

export default FloatingButtons;
