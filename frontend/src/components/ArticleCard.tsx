import { motion } from 'framer-motion';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toggleLike, rateArticle, Article } from '../api';
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { ThumbsUp, BookOpen, Star, ShareNetwork } from 'phosphor-react';
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface ArticleCardProps {
  article: Article;
  onViewDetails: (article: Article) => void;
  queryToInvalidate: 'articles' | 'randomArticles';
}

const ArticleCard = ({ article, onViewDetails, queryToInvalidate }: ArticleCardProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isRatingOpen, setIsRatingOpen] = useState(false);
  const [rating, setRating] = useState(5);

  const likeMutation = useMutation({
    mutationFn: () => toggleLike(article._id, article.title),
    onSuccess: (data) => {
      toast({
        title: data.data.liked ? "Article Liked!" : "Article Unliked",
      });
      queryClient.invalidateQueries({ queryKey: [queryToInvalidate] });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "You must be logged in to like an article.",
        variant: "destructive",
      });
    },
  });

  const rateMutation = useMutation({
    mutationFn: (newRating: number) => rateArticle(article._id, newRating),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Your rating has been submitted!",
      });
      queryClient.invalidateQueries({ queryKey: [queryToInvalidate] });
      setIsRatingOpen(false);
    },
    onError: () => {
      toast({
        title: "Error",
        description: "You have already rated this article or are not logged in.",
        variant: "destructive",
      });
      setIsRatingOpen(false);
    },
  });

  const handleRatingSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    rateMutation.mutate(rating);
  };

  return (
    <Dialog open={isRatingOpen} onOpenChange={setIsRatingOpen}>
      <TooltipProvider delayDuration={200}>
        <motion.div
          layout
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="glass-card rounded-2xl p-4 flex flex-col h-full"
        >
          {/* Text content area */}
          <div className="flex-grow">
            <h3 className="text-lg font-light text-foreground leading-tight">
              {article.title}
            </h3>
          </div>

          {/* THE FIX: Footer with source on left, and horizontal row of buttons on right */}
          <div className="flex justify-between items-center w-full pt-4 mt-auto">
            <p className="text-xs text-muted-foreground">{article.source}</p>
            
            <div className="flex items-center gap-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={() => likeMutation.mutate()}
                    variant={article.user_has_liked ? "default" : "outline"}
                    size="icon"
                    className="h-8 w-8"
                  >
                    <ThumbsUp size={14} weight="light"/>
                  </Button>
                </TooltipTrigger>
                <TooltipContent><p>{article.user_has_liked ? 'Unlike' : 'Like'}</p></TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="icon" disabled={article.user_has_rated} className="h-8 w-8">
                      <Star size={14} weight="light"/>
                    </Button>
                  </DialogTrigger>
                </TooltipTrigger>
                <TooltipContent><p>{article.user_has_rated ? 'Rated' : 'Rate'}</p></TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button onClick={() => onViewDetails(article)} variant="outline" size="icon" className="h-8 w-8">
                    <BookOpen size={14} weight="light"/>
                  </Button>
                </TooltipTrigger>
                <TooltipContent><p>Details</p></TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="icon" asChild className="h-8 w-8">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      <ShareNetwork size={14} weight="light"/>
                    </a>
                  </Button>
                </TooltipTrigger>
                <TooltipContent><p>Source</p></TooltipContent>
              </Tooltip>
            </div>
          </div>
        </motion.div>
      </TooltipProvider>

      {/* Rating Dialog (no changes here) */}
      <DialogContent className="glass-card">
        {/* ... */}
      </DialogContent>
    </Dialog>
  );
};

export default ArticleCard;