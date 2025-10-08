import { motion } from 'framer-motion';

const About = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-24 text-center"
    >
      <h1 className="text-5xl font-light mb-4">About NewsVerse</h1>
      <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
        NewsVerse was founded with the mission to democratize news intelligence. We use cutting-edge AI to analyze thousands of sources, providing you with unbiased, fact-checked, and summarized news to help you make smarter decisions.
      </p>
    </motion.div>
  );
};

export default About;
