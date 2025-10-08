import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { List, X } from 'phosphor-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { logoutUser } from '../api';

const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const isHomepage = location.pathname === '/';
  const isLoginPage = location.pathname === '/login';
  const { user, isAuthenticated, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const loginUrl = 'http://localhost:8000/login/google';

  const logoutMutation = useMutation({
    mutationFn: logoutUser,
    onSuccess: () => {
      // THE FIX: Manually and instantly update the user data in the cache to null.
      // This forces the useAuth hook and all other components to re-render immediately
      // with the logged-out state, without waiting for a refresh or another fetch.
      queryClient.setQueryData(['currentUser'], null);
      navigate('/');
    },
    onError: (error) => {
      console.error("Logout API call failed, but forcing logout on the client.", error);
      // Still force the UI to update even if the API call failed for some reason.
      queryClient.setQueryData(['currentUser'], null);
      navigate('/');  
    }
  });

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    if (!isHomepage) {
      navigate('/');
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMobileMenuOpen(false);
  };

  const handleMobileLogout = () => {
    logoutMutation.mutate();
    setIsMobileMenuOpen(false);
  };
  // THIS IS THE FIX: The "News" item has been removed from this array.
  const navItems = [
    { name: 'Testimonials', href: 'testimonials', isHomepageOnly: true },
    { name: 'Features', href: 'features', isHomepageOnly: true },
    { name: 'FAQ', href: 'faq', isHomepageOnly: true },
    { name: 'About', href: '/about', isPageLink: true },
    { name: 'Contact', href: '/contact', isPageLink: true },
  ];

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'glass-card' : 'bg-transparent'}`}
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-2xl font-light tracking-tighter bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              NewsVerse
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8 relative left-[-30px]">
              {navItems.map((item) => {
                if (item.isHomepageOnly) {
                  return (
                    <button key={item.name} onClick={() => scrollToSection(item.href)} className="text-muted-foreground hover:text-foreground transition-colors duration-300 font-light">
                      {item.name}
                    </button>
                  );
                }
                if (item.isPageLink) {
                  return (
                    <Link key={item.name} to={item.href} className="text-muted-foreground hover:text-foreground transition-colors duration-300 font-light">
                      {item.name}
                    </Link>
                  );
                }
                return null;
              })}
            </div>

            {/* Auth Controls & Mobile Trigger */}
            <div className="flex items-center gap-2">
              {isLoading ? (
                <div className="h-10 w-10 bg-muted/50 rounded-full animate-pulse" />
              ) : isAuthenticated && user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                      <Avatar>
                        <AvatarImage src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
                        <AvatarFallback>{user.name.charAt(0).toUpperCase()}</AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56 glass-card">
                    <DropdownMenuLabel>
                      <div className="flex flex-col space-y-1 font-normal">
                        <p className="text-sm font-medium leading-none">{user.name}</p>
                        <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild><Link to="/preferences">Preferences</Link></DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onSelect={() => logoutMutation.mutate()}>
                      Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                !isLoginPage && (
                <Link to="/login" className="hidden md:block">
                  <button className="neuro-button px-6 py-2 rounded-lg text-sm">Sign In</button>
                </Link>
                )
              )}
              <button onClick={() => setIsMobileMenuOpen(true)} className="md:hidden p-2 text-foreground">
                <List size={24} weight="light" />
              </button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* ... (Mobile Menu code remains the same, it will automatically update based on the navItems array) ... */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 h-full w-4/5 max-w-sm glass-card z-50"
          >
            <div className="p-6 flex flex-col h-full">
              <button onClick={() => setIsMobileMenuOpen(false)} className="p-2 text-foreground self-end">
                <X size={24} weight="light" />
              </button>
              <nav className="flex flex-col space-y-6 mt-8">
                {navItems.map((item) => {
                  if (item.isHomepageOnly) {
                    return <button key={item.name} onClick={() => scrollToSection(item.href)} className="text-left text-lg text-muted-foreground hover:text-foreground">{item.name}</button>;
                  }
                  if (item.isPageLink) {
                    return <Link key={item.name} to={item.href} onClick={() => setIsMobileMenuOpen(false)} className="text-lg text-muted-foreground hover:text-foreground">{item.name}</Link>;
                  }
                  return null;
                })}
                <div className="pt-4 space-y-4">
                  {isAuthenticated && user ? (
                    <>
                      <div className="flex items-center gap-4">
                        <Avatar>
                          <AvatarImage src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
                          <AvatarFallback>{user.name.charAt(0).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div className="font-normal">
                          <p className="text-sm font-medium leading-none">{user.name}</p>
                        </div>
                      </div>
                      <Button className="w-full" variant="ghost" onClick={handleMobileLogout}>
                        Log out
                      </Button>
                    </>
                  ) : (
                    !isLoginPage && (
                    <Link to="/login" onClick={() => setIsMobileMenuOpen(false)} className="w-full">
                      <Button className="w-full neuro-button">Sign In</Button>
                    </Link>
                    )
                  )}
                </div>
              </nav>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Navigation;

