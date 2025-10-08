// src/components/ArticleDetailModal.tsx
import { Article } from '../api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface ArticleDetailModalProps {
  article: Article | null;
  isOpen: boolean;
  onClose: () => void;
}

const ArticleDetailModal = ({ article, isOpen, onClose }: ArticleDetailModalProps) => {
  if (!article) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>{article.title}</DialogTitle>
          <DialogDescription>
            <strong>Source:</strong> {article.source} | <strong>Sentiment:</strong> {article.sentiment || 'N/A'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
          <section>
            <h4 className="font-semibold mb-2">Fact Check</h4>
            <p><strong>Verdict:</strong> {article.fact_check?.llm_verdict ? '✅ Verified' : '❌ Unverified'}</p>
            <p className="text-sm text-muted-foreground"><em>{article.fact_check?.fact_check_explanation || 'No explanation available.'}</em></p>
          </section>
          <section>
            <h4 className="font-semibold mb-2">Concise Summary</h4>
            <p className="text-sm">{article.summarization?.summary || 'No summary available.'}</p>
          </section>
          <section>
            <h4 className="font-semibold mb-2">Story Summary</h4>
            <p className="text-sm">{article.summarization?.story_summary || 'No story summary available.'}</p>
          </section>
        </div>
        <DialogFooter>
          <Button onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ArticleDetailModal;