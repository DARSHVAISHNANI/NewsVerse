import { motion } from 'framer-motion';
import { GoogleLogo } from 'phosphor-react';

const Login = () => {
  // Your backend provides the Google login URL
  const loginUrl = 'http://localhost:8000/login/google';

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background 3D object */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
        <iframe
          src='https://my.spline.design/worldplanet-MHxva3kCAuvHHDNWdCIgBFKB/'
          frameBorder='0'
          width='100%'
          height='100%'
          className="w-full h-full"
        ></iframe>
      </div>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        className="relative z-10 w-full max-w-md mx-auto px-6"
      >
        <div className="glass-card rounded-3xl p-8 md:p-12 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl md:text-4xl font-light tracking-tighter mb-4"
          >
            Welcome to{' '}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              NewsVerse
            </span>
            {/* FIX: Removed the space in the closing tag below */}
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-muted-foreground font-light mb-8"
          >
            Sign in to access your personalized news feed.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <a href={loginUrl}>
              <button className="w-full neuro-button px-6 py-3 rounded-xl text-foreground font-light flex items-center justify-center space-x-3 group">
                <GoogleLogo size={20} weight="light" />
                <span>Sign in with Google</span>
              </button>
            </a>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
