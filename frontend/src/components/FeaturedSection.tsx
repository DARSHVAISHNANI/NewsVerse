import { motion } from 'framer-motion';

const FeaturedSection = () => {
  const publications = [
    { name: 'TechCrunch', logo: 'TC' },
    { name: 'Forbes', logo: 'Forbes' },
    { name: 'Reuters', logo: 'Reuters' },
    { name: 'Bloomberg', logo: 'Bloomberg' },
    { name: 'WSJ', logo: 'WSJ' },
    { name: 'CNN', logo: 'CNN' },
  ];

  return (
    <section className="py-20 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <p className="text-muted-foreground font-light text-lg">
            Featured in leading publications
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center"
        >
          {publications.map((pub, index) => (
            <motion.div
              key={pub.name}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="glass-card rounded-2xl p-6 h-20 flex items-center justify-center group hover:scale-105 transition-transform duration-300"
            >
              <span className="text-lg font-light text-muted-foreground group-hover:text-foreground transition-colors">
                {pub.logo}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturedSection;