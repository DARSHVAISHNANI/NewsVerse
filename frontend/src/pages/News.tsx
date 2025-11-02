import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getRecommendations, Article } from "../api";
import ArticleDetailModal from "../components/ArticleDetailModal";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import ArticleCard from "../components/ArticleCard"; // Import the new card

const News = () => {
  const { data: articles, isLoading, isError } = useQuery<Article[]>({
    queryKey: ['recommendations'],
    queryFn: async () => (await getRecommendations()).data,
  });

  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="relative min-h-screen container mx-auto px-4 py-12">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/4 z-0 pointer-events-none opacity-30">
        <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 0.7, opacity: 1 }}
            transition={{ duration: 1 }}
            style={{ width: '800px', height: '800px' }}
        >
            <iframe 
                src='https://my.spline.design/worldplanet-MHxva3kCAuvHHDNWdCIgBFKB/' 
                frameBorder='0' 
                width='100%' 
                height='100%'
            ></iframe>
        </motion.div>
      </div>

      <div className="relative z-10">
        <header className="text-center mb-12">
            <h1 className="text-5xl font-light tracking-tighter">Today's News Feed</h1>
            <p className="text-muted-foreground mt-2">Your AI-curated articles for today</p>
        </header>

        {isLoading ? (
            <div className="space-y-6 max-w-4xl mx-auto">
                {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-32 w-full rounded-2xl" />)}
            </div>
        ) : isError ? (
            <div className="text-center text-destructive">
                <p>Failed to fetch recommended articles. Is the backend running?</p>
            </div>
        ) : !articles || articles.length === 0 ? (
            <div className="text-center text-muted-foreground py-12">
                <p className="text-lg mb-2">No recommendations available yet.</p>
                <p className="text-sm">Complete your preferences and check back later for personalized articles!</p>
            </div>
        ) : (
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {articles.map((article) => (
              <ArticleCard
                key={article._id}
                article={article}
                onViewDetails={setSelectedArticle}
                queryToInvalidate="recommendations"
              />
            ))}
          </motion.div>
        )}
      </div>

      <ArticleDetailModal
        article={selectedArticle}
        isOpen={!!selectedArticle}
        onClose={() => setSelectedArticle(null)}
      />
    </div>
  );
};

export default News;