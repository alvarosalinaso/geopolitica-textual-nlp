"""
RAG (Retrieval-Augmented Generation) para análisis geopolítico.
Recupera contexto de documentos y genera respuestas con LLM.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

try:
    import pandas as pd  # noqa: F401

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from src.data_loader import list_text_files, write_json
except ImportError:  # ejecución directa: python src/rag_analysis.py
    from data_loader import list_text_files, write_json

logger = logging.getLogger(__name__)


class SimpleRAG:
    """RAG system con TF-IDF retrieval + LLM generation."""

    def __init__(self) -> None:
        self.documents: list[str] = []
        self.vectorizer = None
        self.tfidf_matrix = None

    def ingest(self, texts: list[str]) -> None:
        """Indexa documentos para retrieval."""
        self.documents = texts
        if SKLEARN_AVAILABLE and texts:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="spanish")
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Recupera los top_k documentos más relevantes."""
        if not SKLEARN_AVAILABLE or self.tfidf_matrix is None:
            return self.documents[:top_k]

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]

    def generate_with_llm(self, query: str, context: str) -> str:
        """Genera respuesta usando OpenAI API."""
        try:
            import openai

            client = openai.OpenAI()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Analiza el contexto como analista geopolítico. Responde basándote SOLO en el contexto proporcionado. Sé conciso y preciso.",
                    },
                    {
                        "role": "user",
                        "content": f"Contexto:\n{context[:3000]}\n\nPregunta: {query}",
                    },
                ],
                temperature=0.2,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:  # noqa: BLE001
            return f"[LLM no disponible: {e}] Usando respuesta basada en contexto recuperado."

    def generate_without_llm(self, query: str, context: str) -> str:
        """Genera respuesta sin LLM (extractiva simple)."""
        sentences = context.split(".")
        query_words = set(query.lower().split())

        scored = []
        for s in sentences:
            s_words = set(s.lower().split())
            overlap = len(query_words & s_words)
            scored.append((overlap, s.strip()))

        scored.sort(key=lambda x: x[0], reverse=True)
        relevant = [s for _, s in scored[:3] if s]

        return "Documentos relevantes encontrados:\n" + "\n".join(
            f"- {s}." for s in relevant
        )


def run_rag_analysis(
    data_dir: Path = Path("data"),
    output_dir: Path = Path("data/export"),
    queries: list[str] | None = None,
) -> dict:
    """
    Análisis RAG sobre documentos geopolíticos.

    Returns:
        dict con respuestas RAG y métricas de retrieval
    """
    if not PANDAS_AVAILABLE:
        logger.warning("pandas no instalado")
        return {}

    if not queries:
        queries = [
            "¿Cuáles son las principales entidades geopolíticas mencionadas en los discursos del Patronato?",
            "¿Qué países o regiones tienen mayor frecuencia de mención?",
            "¿Existen patrones de co-ocurrencia entre entidades geopolíticas?",
            "¿Cómo se distribuyen las referencias geográficas en los documentos?",
            "¿Qué temas geopolíticos dominan en el análisis textual?",
        ]

    text_files = list_text_files(data_dir)
    documents: list[str] = []
    for tf in text_files[:30]:
        text = tf.read_text(encoding="utf-8", errors="ignore")
        words = text.split()
        for i in range(0, len(words), 500):
            chunk = " ".join(words[i : i + 500])
            if len(chunk.strip()) > 100:
                documents.append(chunk)

    if not documents:
        logger.warning("No se encontraron documentos")
        return {}

    logger.info("Indexando %d chunks de %d documentos", len(documents), len(text_files))

    rag = SimpleRAG()
    rag.ingest(documents)

    has_llm = os.environ.get("OPENAI_API_KEY", "") != ""
    results = {
        "method": "openai" if has_llm else "tfidf_extractive",
        "n_documents": len(documents),
        "answers": [],
    }

    for q in queries:
        context_docs = rag.retrieve(q, top_k=3)
        context = "\n\n".join(context_docs)

        if has_llm:
            answer = rag.generate_with_llm(q, context)
        else:
            answer = rag.generate_without_llm(q, context)

        results["answers"].append(
            {
                "query": q,
                "answer": answer[:500],
                "n_context_docs": len(context_docs),
                "method": "openai" if has_llm else "extractive",
            }
        )
        logger.info("Q: %s... -> %d docs recuperados", q[:60], len(context_docs))

    write_json(results, output_dir / "rag_results.json")
    logger.info("%d consultas procesadas", len(queries))
    return results


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    run_rag_analysis()
