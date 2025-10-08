import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const Contact = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-24"
    >
      <div className="max-w-xl mx-auto text-center">
        <h1 className="text-5xl font-light mb-4">Contact Us</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Have questions or want to partner with us? We'd love to hear from you.
        </p>
      </div>
      <form className="max-w-xl mx-auto space-y-4">
        <Input type="text" placeholder="Your Name" className="bg-input/50"/>
        <Input type="email" placeholder="Your Email" className="bg-input/50"/>
        <Textarea placeholder="Your Message" className="bg-input/50"/>
        <Button className="w-full neuro-button">Send Message</Button>
      </form>
    </motion.div>
  );
};

export default Contact;
