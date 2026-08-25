"""
Análisis de sentimiento para discursos geopolíticos.
Soporta OpenAI API (si hay key) o fallback lexicon-based con TextBlob.
"""
import json
import os
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


def analyze_sentiment_lexicon(texts: list[str]) -> list[dict]:
    """Análisis de sentimiento con TextBlob (lexicon-based)."""
    results = []
    for text in texts:
        blob = TextBlob(text[:5000])
        results.append({
            "polarity": round(blob.sentiment.polarity, 4),
            "subjectivity": round(blob.sentiment.subjectivity, 4),
            "label": "positivo" if blob.sentiment.polarity > 0.1 else "negativo" if blob.sentiment.polarity < -0.1 else "neutral",
        })
    return results


def analyze_sentiment_openai(texts: list[str], model: str = "gpt-4o-mini") -> list[dict]:
    """Análisis de sentimiento con OpenAI API."""
    try:
        import openai
        client = openai.OpenAI()
    except Exception:
        print("[SENTIMENT] OpenAI no disponible, usando lexicon fallback")
        return analyze_sentiment_lexicon(texts)
    
    results = []
    for text in texts:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Analiza el sentimiento geopolitical del siguiente texto. Responde SOLO con JSON: {\"polarity\": float -1 a 1, \"subjectivity\": float 0 a 1, \"label\": \"positivo\"|\"negativo\"|\"neutral\", \"confidence\": float 0 a 1, \"summary\": \"resumen en 10 palabras\"}"},
                    {"role": "user", "content": text[:4000]},
                ],
                temperature=0.1,
                max_tokens=200,
            )
            content = response.choices[0].message.content.strip()
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                results.append(result)
            else:
                results.append({"polarity": 0, "label": "neutral", "error": "parse_error"})
        except Exception as e:
            results.append({"polarity": 0, "label": "neutral", "error": str(e)})
    
    return results


def run_sentiment_analysis(data_dir: Path = Path("data"), output_dir: Path = Path("data/export")) -> dict:
    """
    Análisis de sentimiento de discursos geopolíticos.
    
    Returns:
        dict con distribución de sentimientos y estadísticas
    """
    texts = []
    sources = []

    csv_path = data_dir / "processed" / "speeches.csv"
    fallback_csv = data_dir / "sample_speeches.csv"
    if PANDAS_AVAILABLE and csv_path.exists():
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            text = str(row.get("text", ""))
            source = str(row.get("speaker", "")) + " " + str(row.get("year", ""))
            if len(text.strip()) > 100:
                texts.append(text)
                sources.append(source.strip())
    elif PANDAS_AVAILABLE and fallback_csv.exists():
        df = pd.read_csv(fallback_csv)
        for _, row in df.iterrows():
            text = str(row.get("text", ""))
            source = str(row.get("speaker", "")) + " " + str(row.get("year", ""))
            if len(text.strip()) > 100:
                texts.append(text)
                sources.append(source.strip())

    text_files = list(data_dir.rglob("*.txt")) + list(data_dir.rglob("*.md"))
    for tf in text_files[:20]:
        text = tf.read_text(encoding="utf-8", errors="ignore")
        if len(text.strip()) > 100:
            texts.append(text)
            sources.append(tf.name)
    
    if not texts:
        print("[SENTIMENT] No valid texts found")
        return {}
    
    print(f"[SENTIMENT] Analizando {len(texts)} documentos...")
    
    # Choose method
    use_openai = os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_API_KEY") != ""
    
    if use_openai:
        print("[SENTIMENT] Usando OpenAI API")
        sentiments = analyze_sentiment_openai(texts)
    else:
        print("[SENTIMENT] Usando TextBlob (lexicon-based) — añade OPENAI_API_KEY para mejor accuracy")
        sentiments = analyze_sentiment_lexicon(texts)
    
    # Aggregate
    df = pd.DataFrame(sentiments)
    df["source"] = sources[:len(df)]
    
    polarity_dist = {
        "positivo": len(df[df["label"] == "positivo"]),
        "neutral": len(df[df["label"] == "neutral"]),
        "negativo": len(df[df["label"] == "negativo"]),
    }
    
    results = {
        "method": "openai" if use_openai else "textblob",
        "n_documents": len(texts),
        "polarity_distribution": polarity_dist,
        "mean_polarity": round(df["polarity"].mean(), 4) if "polarity" in df.columns else 0,
        "mean_subjectivity": round(df["subjectivity"].mean(), 4) if "subjectivity" in df.columns else 0,
        "per_document": df.to_dict(orient="records") if len(df) <= 50 else df.head(20).to_dict(orient="records"),
    }
    
    print(f"[SENTIMENT] Distribución: {polarity_dist}")
    print(f"[SENTIMENT] Polaridad media: {results['mean_polarity']:.3f}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "sentiment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    run_sentiment_analysis()
