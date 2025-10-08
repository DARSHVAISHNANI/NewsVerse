import { motion } from 'framer-motion';
import { CheckCircle, Crown } from 'phosphor-react';

const MissionSection = () => {
  return (
    <section id="mission" className="py-20 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          {/* Mission Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-light tracking-tighter mb-6">
              Our{' '}
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                Mission
              </span>
            </h2>
            <p className="text-xl text-muted-foreground font-light leading-relaxed mb-8">
              We believe that access to timely, accurate, and intelligently analyzed news 
              shouldn't be a luxury. NewsVerse was built to democratize news intelligence, 
              giving everyone the power to make informed decisions in our rapidly changing world.
            </p>
            <p className="text-lg text-muted-foreground font-light leading-relaxed mb-8">
              Our AI doesn't just aggregate news—it understands context, identifies patterns, 
              and surfaces insights that human analysts might miss. We're not replacing human 
              judgment; we're amplifying it.
            </p>
            
            <div className="space-y-4">
              {[
                'Real-time analysis of global news sources',
                'Context-aware AI that understands nuance',
                'Personalized insights based on your interests',
                'Verified information from trusted sources'
              ].map((item, index) => (
                <motion.div
                  key={item}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="flex items-center space-x-3"
                >
                  <CheckCircle size={20} weight="light" className="text-primary" />
                  <span className="text-muted-foreground font-light">{item}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Pro Plan Card */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="glass-card rounded-3xl p-8 relative overflow-hidden">
              {/* Recommended Badge */}
              <div className="absolute -top-3 -right-3">
                <div className="bg-gradient-primary rounded-full px-4 py-2 flex items-center space-x-2">
                  <Crown size={16} weight="light" className="text-white" />
                  <span className="text-white text-sm font-light">Recommended</span>
                </div>
              </div>

              <div className="text-center">
                <h3 className="text-2xl font-light tracking-tight mb-2">NewsVerse Pro</h3>
                <p className="text-muted-foreground font-light mb-6">
                  For professionals who need the edge
                </p>

                <div className="mb-8">
                  <span className="text-4xl font-light">$29</span>
                  <span className="text-muted-foreground font-light">/month</span>
                </div>

                <div className="space-y-4 mb-8">
                  {[
                    'Advanced AI insights',
                    'Real-time alerts',
                    'Custom news feeds',
                    'API access',
                    'Priority support'
                  ].map((feature, index) => (
                    <motion.div
                      key={feature}
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                      viewport={{ once: true }}
                      className="flex items-center space-x-3"
                    >
                      <CheckCircle size={16} weight="light" className="text-primary" />
                      <span className="text-muted-foreground font-light text-sm">{feature}</span>
                    </motion.div>
                  ))}
                </div>

                <button className="w-full neuro-button px-6 py-3 rounded-2xl text-foreground font-light hover:scale-105 transition-transform duration-300">
                  Start Pro Trial
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default MissionSection;