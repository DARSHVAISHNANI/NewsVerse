import { motion } from 'framer-motion';
import { TwitterLogo, LinkedinLogo, GithubLogo, EnvelopeSimple } from 'phosphor-react';

const Footer = () => {
  const footerLinks = {
    Product: ['Features', 'Pricing', 'API', 'Integrations'],
    Company: ['About', 'Careers', 'Contact', 'Blog'],
    Resources: ['Documentation', 'Help Center', 'Community', 'Status'],
    Legal: ['Privacy', 'Terms', 'Security', 'GDPR'],
  };

  const socialLinks = [
    { icon: TwitterLogo, href: '#', label: 'Twitter' },
    { icon: LinkedinLogo, href: '#', label: 'LinkedIn' },
    { icon: GithubLogo, href: '#', label: 'GitHub' },
    { icon: EnvelopeSimple, href: '#', label: 'Email' },
  ];

  return (
    <footer className="py-20 px-6 border-t border-border/50 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12 mb-12">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h3 className="text-2xl font-light tracking-tighter mb-4">
                <span className="bg-gradient-primary bg-clip-text text-transparent">
                  NewsVerse
                </span>
              </h3>
              <p className="text-muted-foreground font-light leading-relaxed mb-6 max-w-sm">
                Empowering professionals with AI-driven news intelligence for smarter decision making.
              </p>
              
              <div className="flex space-x-4">
                {socialLinks.map((social, index) => (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="p-2 glass-card rounded-xl hover:scale-110 transition-all duration-300 group"
                    aria-label={social.label}
                  >
                    <social.icon 
                      size={20} 
                      weight="light" 
                      className="text-muted-foreground group-hover:text-primary transition-colors" 
                    />
                  </motion.a>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Footer Links */}
          {Object.entries(footerLinks).map(([category, links], categoryIndex) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: categoryIndex * 0.1 }}
              viewport={{ once: true }}
            >
              <h4 className="font-light text-foreground mb-6 tracking-tight">
                {category}
              </h4>
              <ul className="space-y-4">
                {links.map((link, linkIndex) => (
                  <motion.li
                    key={link}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: linkIndex * 0.1 }}
                    viewport={{ once: true }}
                  >
                    <a
                      href="#"
                      className="text-muted-foreground hover:text-foreground transition-colors font-light text-sm"
                    >
                      {link}
                    </a>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Bottom Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="pt-8 border-t border-border/50 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0"
        >
          <p className="text-muted-foreground font-light text-sm">
            © 2024 NewsVerse. All rights reserved.
          </p>
          <p className="text-muted-foreground font-light text-sm">
            Made with AI intelligence for the future of news
          </p>
        </motion.div>
      </div>
    </footer>
  );
};

export default Footer;