import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Star, Quotes } from 'phosphor-react';

const TestimonialsSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Investment Analyst',
      company: 'Goldman Sachs',
      content: 'NewsVerse has revolutionized how I stay informed. The AI insights help me identify market-moving news before my competitors.',
      result: '40% faster news analysis',
      avatar: 'SC',
      rating: 5,
    },
    {
      name: 'Michael Rodriguez',
      role: 'Portfolio Manager',
      company: 'BlackRock',
      content: 'The precision of NewsVerse\s AI analysis is incredible. It filters out the noise and highlights what really matters.',
      result: '65% improvement in decision speed',
      avatar: 'MR',
      rating: 5,
    },
    {
      name: 'Emily Watson',
      role: 'Research Director',
      company: 'JPMorgan',
      content: 'I can\t imagine working without NewsVerse now. It\s like having a team of analysts working 24/7.',
      result: '50% increase in research efficiency',
      avatar: 'EW',
      rating: 5,
    },
    {
      name: 'David Kim',
      role: 'Hedge Fund Manager',
      company: 'Citadel',
      content: 'NewsVerse gives me the edge I need in today\s fast-moving markets. The insights are always spot-on.',
      result: '30% better trade timing',
      avatar: 'DK',
      rating: 5,
    },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % testimonials.length);
    }, 5000);

    return () => clearInterval(timer);
  }, [testimonials.length]);

  return (
    <section id="testimonials" className="py-20 px-6 relative">
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
            Trusted by{' '}
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Industry Leaders
            </span>
          </h2>
          <p className="text-xl text-muted-foreground font-light max-w-2xl mx-auto">
            See how NewsVerse is transforming how professionals stay informed
          </p>
        </motion.div>

        <div className="relative max-w-4xl mx-auto">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5 }}
            className="glass-card rounded-3xl p-8 md:p-12"
          >
            <div className="flex items-start space-x-4 mb-6">
              <Quotes size={32} weight="light" className="text-primary mt-2" />
              <div className="flex-1">
                <p className="text-xl font-light leading-relaxed mb-6 text-foreground">
                  {testimonials[currentIndex].content}
                </p>
                
                <div className="flex items-center space-x-1 mb-6">
                  {[...Array(testimonials[currentIndex].rating)].map((_, i) => (
                    <Star key={i} size={20} weight="fill" className="text-primary" />
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center text-white font-light">
                      {testimonials[currentIndex].avatar}
                    </div>
                    <div>
                      <h4 className="font-light text-foreground">
                        {testimonials[currentIndex].name}
                      </h4>
                      <p className="text-muted-foreground text-sm">
                        {testimonials[currentIndex].role} at {testimonials[currentIndex].company}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-primary font-light text-lg">
                      {testimonials[currentIndex].result}
                    </div>
                    <div className="text-muted-foreground text-sm">
                      Improvement
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Navigation Dots */}
          <div className="flex justify-center space-x-2 mt-8">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === currentIndex ? 'bg-primary' : 'bg-muted'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;