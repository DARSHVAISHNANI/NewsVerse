import { motion } from 'framer-motion';
import { Brain, Lightning, ChartLineUp, Shield } from 'phosphor-react';

const FeaturesSection = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms analyze thousands of news sources to deliver the most relevant insights.',
    },
    {
      icon: Lightning,
      title: 'Real-Time Updates',
      description: 'Get instant notifications about breaking news and market-moving events as they happen.',
    },
    {
      icon: ChartLineUp,
      title: 'Trend Prediction',
      description: 'Predictive analytics help you stay ahead of emerging trends and market shifts.',
    },
    {
      icon: Shield,
      title: 'Verified Sources',
      description: 'Only trusted, verified news sources are included in our analysis for maximum reliability.',
    },
  ];

  return (
    <section id="features" className="py-20 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-light tracking-tighter mb-4">
            Powerful{' '}
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Features
            </span>
          </h2>
          <p className="text-xl text-muted-foreground font-light max-w-2xl mx-auto">
            Everything you need to stay informed and make better decisions
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="glass-card rounded-3xl p-8 group hover:scale-105 transition-all duration-300"
            >
              <div className="flex items-start space-x-4">
                <div className="p-3 rounded-2xl bg-gradient-primary/10 group-hover:bg-gradient-primary/20 transition-colors duration-300">
                  <feature.icon 
                    size={32} 
                    weight="light" 
                    className="text-primary" 
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-light tracking-tight mb-3 text-foreground">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground font-light leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;