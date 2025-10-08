import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { completeOnboarding } from '../api';
import { useToast } from '@/components/ui/use-toast';

const Onboarding = () => {
  const [phone, setPhone] = useState('');
  const [time, setTime] = useState('08:00');
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const onboardingMutation = useMutation({
    mutationFn: () => completeOnboarding(phone, time),
    onSuccess: (response) => {
      // THE FIX: Instantly update the application's user data with the
      // data we just received from the backend. This is not a race condition.
      queryClient.setQueryData(['currentUser'], { authenticated: true, user: response.data.user });

      toast({
        title: "Welcome!",
        description: "Your profile is complete.",
      });
      // Now that the state is guaranteed to be updated, we can safely navigate.
      navigate('/news');
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Prevent the default browser form submission
    onboardingMutation.mutate();
  };

  return (
    <motion.div
      // ... (keep motion props)
      className="container mx-auto px-4 py-12 flex justify-center items-center min-h-[80vh]"
    >
      <Card className="glass-card w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-light tracking-tighter">Welcome to NewsVerse!</CardTitle>
          <CardDescription className="text">
            Just one more step to personalize your experience.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* THIS IS THE FIX: We use onSubmit to handle it with JavaScript */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="phone" className="text-sm font-light text-muted-foreground mb-2 block">Phone Number (for WhatsApp)</label>
              <Input 
                id="phone" 
                name="phone_number" 
                type="tel" 
                placeholder="+1234567890" 
                required 
                className="bg-background/50"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="time" className="text-sm font-light text-muted-foreground mb-2 block">Preferred Notification Time (24h)</label>
              <Input 
                id="time" 
                name="preferred_time" 
                type="time" 
                required 
                className="bg-background/50"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </div>
            <Button type="submit" className="w-full neuro-button" disabled={onboardingMutation.isPending}>
              {onboardingMutation.isPending ? "Saving..." : "Complete Registration"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Skip for now
            </Link>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default Onboarding;