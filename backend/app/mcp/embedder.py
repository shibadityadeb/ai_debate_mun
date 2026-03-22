from typing import List
from sentence_transformers import SentenceTransformer


class Embedder:
    

    _model_name: str = "all-MiniLM-L6-v2"
    _model: SentenceTransformer | None = None

    def __init__(self, model_name: str | None = None) -> None:
        """Initialize the embedder.
        Args:
            model_name: Optional SentenceTransformers model identifier.
        """
        if model_name:
            self._model_name = model_name

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        """Get or load the SentenceTransformer model singleton."""
        if cls._model is None:
            cls._model = SentenceTransformer(cls._model_name)
        return cls._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of input strings.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embeddings, one per input text.
        """
        if not isinstance(texts, list):
            raise TypeError("texts must be a list of strings")

        # Convert any non-string item to string to avoid model errors
        clean_texts = [str(t) for t in texts]

        model = self._get_model()
        embeddings = model.encode(clean_texts, convert_to_numpy=True)

        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()

        # Some backends may already return a Python list.
        return embeddings

