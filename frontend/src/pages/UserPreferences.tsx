import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getUserPreferences, updateUserPreferences, scheduleNotifications, triggerPipeline, deleteAccount } from '../api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { motion } from 'framer-motion';
import { Bell, Clock, Cpu } from 'phosphor-react';
import { useNavigate } from 'react-router-dom';
import { Trash } from 'phosphor-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const UserPreferences = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [phone, setPhone] = useState('');
  const [time, setTime] = useState('08:00');

  // Fetch initial preferences
  const { data: preferencesData, isLoading: isLoadingPreferences } = useQuery({
    queryKey: ['preferences'],
    queryFn: async () => {
      const response = await getUserPreferences();
      return response.data;
    },
    retry: false, // Don't retry if the user is not logged in
  });

  // Populate form when data is fetched
  useEffect(() => {
    if (preferencesData) {
      setPhone(preferencesData.phone_number || '');
      setTime(preferencesData.preferred_time || '08:00');
    }
  }, [preferencesData]);

  // Mutation for updating preferences
  const updateMutation = useMutation({
    mutationFn: () => updateUserPreferences(phone, time),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences'] });
      toast({
        title: "Success!",
        description: "Your preferences have been saved.",
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to save preferences. Please try again.",
        variant: "destructive",
      });
      console.error("Save error:", error);
    },
  });

  // Mutation for scheduling notifications
  const scheduleMutation = useMutation({
    mutationFn: scheduleNotifications,
    onSuccess: (data) => {
      toast({
        title: "Notifications Scheduled!",
        description: data.data.message,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Scheduling Failed",
        description: error.response?.data?.error || 'An unexpected error occurred.',
        variant: "destructive",
      });
    },
  });

  // Mutation for triggering the pipeline
  const pipelineMutation = useMutation({
    mutationFn: triggerPipeline,
    onSuccess: (data) => {
      toast({
        title: "Pipeline Started",
        description: "News analysis is running in the background.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to start the pipeline.",
        variant: "destructive",
      });
    }
  });
  const navigate = useNavigate();

  // Mutation for deleting the user's account
  
  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => {
      toast({
        title: "Account Deleted",
        description: "Your account has been successfully deleted.",
      });
      // THE FIX: Instantly set the user data to null, forcing a UI update.
      queryClient.setQueryData(['currentUser'], null);
      navigate('/');
    },
    onError: (error: any) => {
      toast({
        title: "Deletion Failed",
        description: error.response?.data?.error || 'An unexpected error occurred.',
        variant: "destructive",
      });
      //  // Also force a logout on the client-side if the API call fails
      // queryClient.setQueryData(['currentUser'], null);
      // navigate('/');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl mx-auto space-y-8 pb-20"
    >
      <h1 className="text-4xl font-light tracking-tighter">Account Preferences</h1>

      {/* Manage Preferences Card */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell size={24} weight="light" />
            Notification Settings
          </CardTitle>
          <CardDescription className="text-muted-foreground font-light leading-relaxed">
            Set your phone number and the time you'd like to receive your daily news briefing on WhatsApp.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingPreferences ? (
            <div className="space-y-4">
              <div className="h-10 w-full bg-muted/50 rounded-lg animate-pulse" />
              <div className="h-10 w-full bg-muted/50 rounded-lg animate-pulse" />
              <div className="h-10 w-32 bg-muted/50 rounded-lg animate-pulse" />
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="phone" className="text-sm font-light text-muted-foreground mb-2 block">Phone Number</label>
                <Input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1234567890"
                  className="bg-background/50"
                />
              </div>
              <div>
                <label htmlFor="time" className="text-sm font-light text-muted-foreground mb-2 block">Preferred Time (24h format)</label>
                <Input
                  id="time"
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="bg-background/50"
                />
              </div>
              <Button type="submit" className="neuro-button" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Saving...' : 'Save Preferences'}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>

      {/* Schedule Notifications Card */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock size={24} weight="light" />
            Schedule Daily Briefing
          </CardTitle>
          <CardDescription className="text-muted-foreground font-light leading-relaxed">
            Activate your daily WhatsApp notifications. This will generate your first set of recommendations and schedule daily delivery.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="neuro-button" onClick={() => scheduleMutation.mutate()} disabled={scheduleMutation.isPending}>
            {scheduleMutation.isPending ? 'Scheduling...' : 'Schedule Daily News'}
          </Button>
        </CardContent>
      </Card>

      {/* Manual Pipeline Trigger Card */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu size={24} weight="light" />
            Manual Sync
          </CardTitle>
          <CardDescription className="text-muted-foreground font-light leading-relaxed">
            Manually trigger the AI pipeline to fetch and analyze the very latest news articles right now.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="neuro-button" onClick={() => pipelineMutation.mutate()} disabled={pipelineMutation.isPending}>
            {pipelineMutation.isPending ? 'Analyzing...' : 'Run Analysis Pipeline'}
          </Button>
        </CardContent>
      </Card>
      {/* Danger Zone Card */}
      <Card className="glass-card border-destructive/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <Trash size={24} weight="light" />
            Delete Account
          </CardTitle>
          <CardDescription className="text">
            This action is permanent and cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className="neuro-button">
                Delete My Account
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="glass-card">
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete your account and all associated data from our servers. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => deleteMutation.mutate()}>
                  Yes, delete my account
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default UserPreferences;

