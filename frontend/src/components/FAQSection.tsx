import { motion } from 'framer-motion';
import { useState } from 'react';
import { Plus, Minus } from 'phosphor-react';

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: 'How does NewsVerse AI analyze news?',
      answer: 'Our AI uses advanced natural language processing and machine learning algorithms to analyze thousands of news sources in real-time. It identifies key trends, sentiment, and potential market impacts while filtering out noise and misinformation.',
    },
    {
      question: 'What news sources does NewsVerse cover?',
      answer: 'We monitor over 10,000 verified news sources including major publications like Reuters, Bloomberg, Associated Press, and many specialized industry publications. All sources are continuously verified for credibility and accuracy.',
    },
    {
      question: 'Can I customize my news feed?',
      answer: 'Absolutely! NewsVerse Pro allows you to create custom news feeds based on specific topics, companies, industries, or keywords. You can also set personalized alert thresholds and notification preferences.',
    },
    {
      question: 'How accurate are the AI insights?',
      answer: 'Our AI insights maintain a 95%+ accuracy rate based on extensive backtesting and real-world validation. However, we always recommend using our insights as part of your broader decision-making process rather than sole determinants.',
    },
    {
      question: 'Is there a free trial available?',
      answer: 'Yes! We offer a 14-day free trial of NewsVerse Pro with no credit card required. You\'ll have full access to all features including real-time alerts, custom feeds, and API access.',
    },
    {
      question: 'How quickly do I receive breaking news alerts?',
      answer: 'Our system processes news in real-time with alerts typically sent within 30 seconds of a story breaking. Pro users can customize alert sensitivity and receive priority notifications for market-moving events.',
    },
  ];

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-light tracking-tighter mb-4">
            Frequently Asked{' '}
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Questions
            </span>
          </h2>
          <p className="text-xl text-muted-foreground font-light">
            Everything you need to know about NewsVerse
          </p>
        </motion.div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="glass-card rounded-2xl overflow-hidden"
            >
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-6 py-6 text-left flex items-center justify-between hover:bg-white/5 transition-colors duration-300"
              >
                <span className="text-lg font-light text-foreground">
                  {faq.question}
                </span>
                <div className="ml-4">
                  {openIndex === index ? (
                    <Minus size={20} weight="light" className="text-primary" />
                  ) : (
                    <Plus size={20} weight="light" className="text-primary" />
                  )}
                </div>
              </button>
              
              <motion.div
                initial={false}
                animate={{
                  height: openIndex === index ? 'auto' : 0,
                  opacity: openIndex === index ? 1 : 0,
                }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="px-6 pb-6">
                  <p className="text-muted-foreground font-light leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQSection;