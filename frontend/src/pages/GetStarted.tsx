import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getRandomArticles, Article } from "../api";
import ArticleCard from "../components/ArticleCard";
import ArticleDetailModal from "../components/ArticleDetailModal";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import { useAuth } from "../hooks/useAuth";

const GetStarted = () => {
  const { isAuthenticated } = useAuth();
  const { data: articles, isLoading, isError } = useQuery<Article[]>({
    queryKey: ['randomArticles'],
    queryFn: async () => (await getRandomArticles()).data,
    enabled: isAuthenticated, // Only fetch if the user is authenticated
  });

  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  if (!isAuthenticated) {
      return (
          <div className="text-center py-24">
              <h1 className="text-3xl font-light">Please log in</h1>
              <p className="text-muted-foreground mt-2">Login to discover new articles.</p>
          </div>
      )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="container mx-auto px-4 py-12"
    >
      <header className="text-center mb-12">
        <h1 className="text-5xl font-light tracking-tighter">Discover New Articles</h1>
        <p className="text-muted-foreground mt-2">Here are 5 articles to get you started.</p>
      </header>
      
      {isLoading ? (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex flex-col space-y-3">
                  <Skeleton className="h-[200px] w-full rounded-xl" />
                  <div className="space-y-2">
                      <Skeleton className="h-4 w-[250px]" />
                      <Skeleton className="h-4 w-[200px]" />
                  </div>
              </div>
            ))}
        </div>
      ) : isError ? (
        <p className="text-center text-destructive">Could not fetch articles. Please try again later.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles?.map((article) => (
            <ArticleCard
              key={article._id}
              article={article}
              onViewDetails={() => setSelectedArticle(article)}
            />
          ))}
        </div>
      )}

      <ArticleDetailModal
        article={selectedArticle}
        isOpen={!!selectedArticle}
        onClose={() => setSelectedArticle(null)}
      />
    </motion.div>
  );
};

export default GetStarted;