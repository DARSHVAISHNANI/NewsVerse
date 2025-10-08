import { motion } from 'framer-motion';
import HeroSection from '../components/HeroSection';
import FeaturedSection from '../components/FeaturedSection';
import TestimonialsSection from '../components/TestimonialsSection';
import FeaturesSection from '../components/FeaturesSection';
import MissionSection from '../components/MissionSection';
import FAQSection from '../components/FAQSection';

const Homepage = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <HeroSection />
      <FeaturedSection />
      <TestimonialsSection />
      <FeaturesSection />
      <MissionSection />
      <FAQSection />
    </motion.div>
  );
};

export default Homepage;
