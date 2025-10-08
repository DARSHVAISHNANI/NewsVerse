import { motion } from 'framer-motion';
import { ArrowRight } from 'phosphor-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth'; // Import the auth hook

const HeroSection = () => {
  const { isAuthenticated } = useAuth(); // Get the user's login status

  return (
    <section id="home" className="relative h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none translate-y-40 ">
        <iframe 
          src='https://my.spline.design/worldplanet-MHxva3kCAuvHHDNWdCIgBFKB/' 
          frameBorder='0' 
          width='100%' 
          height='100%'
          className="w-full h-full"
        ></iframe>
      </div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center -mt-32">
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl md:text-7xl font-light tracking-tighter mb-6"
        >
          Read Smarter with{' '}
          <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            AI-Powered
          </span>{' '}
          News Insights
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl text-muted-foreground font-light max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          NewsVerse combines artificial intelligence with cutting-edge analysis strategies to help you stay informed with precision and ease.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex justify-center items-center gap-4"
        >
          {/* THIS IS THE NEW LOGIC */}
          {isAuthenticated ? (
            // Buttons to show when the user IS logged in
            <>
              <Link to="/get-started">
                <button className="neuro-button px-8 py-4 rounded-2xl text-foreground font-light flex items-center space-x-2 group">
                  <span>Get Started</span>
                  <ArrowRight 
                    size={20} 
                    weight="light" 
                    className="group-hover:translate-x-1 transition-transform duration-300" 
                  />
                </button>
              </Link>
              <Link to="/news">
                <button className="neuro-button px-8 py-4 rounded-2xl text-foreground font-light flex items-center space-x-2 group">
                  <span>Personalized Recommendations</span>
                  <ArrowRight 
                    size={20} 
                    weight="light" 
                    className="group-hover:translate-x-1 transition-transform duration-300" 
                />
                </button>
              </Link>
            </>
          ) : (
            // Button to show when the user IS NOT logged in
            <Link to="/login">
              <button className="neuro-button px-8 py-4 rounded-2xl text-foreground font-light flex items-center space-x-2 group">
                <span>Get Started</span>
                <ArrowRight 
                  size={20} 
                  weight="light" 
                  className="group-hover:translate-x-1 transition-transform duration-300" 
                />
              </button>
            </Link>
          )}
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;