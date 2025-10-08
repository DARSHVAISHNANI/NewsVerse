import React from 'react';
import Navigation from './Navigation';
import Footer from './Footer';

// This component ensures a consistent layout across all pages of your application.
const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      {/* 'flex-grow' makes the main content area expand to fill available space,
          pushing the footer to the bottom of the page. 
          'pt-20' adds padding to the top to prevent content from hiding under the fixed navigation bar.
      */}
      <main className="flex-grow pt-20">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;

