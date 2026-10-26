"""
Análisis de sentimiento para discursos geopolíticos.

Método primario: léxico español propio, transparente y sin dependencias externas
ni llamadas de red. TextBlob queda como referencia secundaria documentada.

Los umbrales ±0.1 para las etiquetas positivo/negativo/neutral son heurísticos,
NO están calibrados con anotación humana: ver README "Qué mide y qué no".
"""

import json
import re
import unicodedata
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

# Umbrales heurísticos, sin calibrar (documentado en README).
POSITIVE_THRESHOLD = 0.1
NEGATIVE_THRESHOLD = -0.1


def _strip_accents(token: str) -> str:
    """Normaliza un token quitando acentos (forma canónica del léxico)."""
    nfkd = unicodedata.normalize("NFD", token.lower())
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


# Negaciones que invierten la polaridad de la palabra siguiente (ventana de 3 tokens).
NEGATION_WORDS = {
    _strip_accents(w) for w in ("no", "nunca", "jamás", "ni", "sin", "tampoco")
}

# Léxico español: solo palabras de polaridad clara. Se normaliza (minúsculas,
# sin acentos) al definirlo; no es exhaustivo a propósito: es un léxico
# pequeño, auditable y versionado en el repo. Términos neutros o ambiguos en
# discurso político ("seguridad", "defensa", "sanción", "pensión"...) se
# excluyen a propósito para no inflar la polaridad.
SPANISH_POSITIVE = {
    "paz",
    "concordia",
    "armonía",
    "convivencia",
    "reconciliación",
    "prosperidad",
    "progreso",
    "desarrollo",
    "bienestar",
    "futuro",
    "esperanza",
    "optimismo",
    "dignidad",
    "justicia",
    "libertad",
    "democracia",
    "soberanía",
    "unidad",
    "solidaridad",
    "fraternidad",
    "hermandad",
    "amistad",
    "cooperación",
    "esfuerzo",
    "logro",
    "éxito",
    "victoria",
    "ganancia",
    "mejora",
    "fortalecimiento",
    "fortaleza",
    "grandeza",
    "glorioso",
    "heroico",
    "admirable",
    "celebrar",
    "celebración",
    "felicitaciones",
    "felicidad",
    "alegría",
    "amor",
    "honor",
    "homenaje",
    "agradecer",
    "gratitud",
    "bendito",
    "bendecir",
    "confianza",
    "esperanzador",
    "alentar",
    "impulso",
    "impulsar",
    "edificar",
    "superar",
    "conquistar",
    "favorable",
    "beneficio",
    "beneficioso",
    "utilidad",
    "provecho",
    "riqueza",
    "abundancia",
    "salud",
    "avance",
    "modernización",
    "tecnología",
    "innovación",
    "calidad",
    "empleo",
    "vivienda",
    "beca",
    "becas",
    "gratuito",
    "gratuidad",
    "ayuda",
    "protección",
    "garantía",
    "igualdad",
    "equidad",
    "inclusión",
    "participación",
    "transparencia",
    "compromiso",
    "consenso",
    "diálogo",
    "pacto",
    "acuerdo",
    "solidario",
    "fraterno",
}

SPANISH_NEGATIVE = {
    "guerra",
    "conflicto",
    "crisis",
    "pobreza",
    "hambre",
    "muerte",
    "dolor",
    "sufrimiento",
    "violencia",
    "terrorismo",
    "dictadura",
    "tiranía",
    "opresión",
    "represión",
    "censura",
    "cárcel",
    "exilio",
    "desempleo",
    "desigualdad",
    "injusticia",
    "corrupción",
    "delincuencia",
    "crimen",
    "narcotráfico",
    "amenaza",
    "riesgo",
    "peligro",
    "terror",
    "miedo",
    "incertidumbre",
    "recesión",
    "inflación",
    "deuda",
    "déficit",
    "colapso",
    "destrucción",
    "daño",
    "perjuicio",
    "engaño",
    "mentira",
    "fracaso",
    "derrota",
    "pérdida",
    "padecer",
    "lamentable",
    "triste",
    "doloroso",
    "fatal",
    "terrible",
    "grave",
    "severo",
    "crítico",
    "alerta",
    "preocupación",
    "preocupante",
    "emergencia",
    "catástrofe",
    "desastre",
    "sequía",
    "inundación",
    "incendio",
    "epidemia",
    "enfermedad",
    "pandemia",
    "abuso",
    "acoso",
    "asesinato",
    "criminal",
    "ilegal",
    "inmoral",
    "abandono",
    "descuido",
    "negligencia",
    "obstáculo",
    "dificultad",
    "problema",
    "retroceso",
    "debilidad",
    "hostilidad",
    "tensión",
    "confusión",
    "desorden",
    "caos",
    "fraude",
    "soborno",
    "extorsión",
    "secuestro",
    "hurto",
    "robo",
    "subempleo",
    "carencia",
    "escasez",
    "castigo",
    "multa",
    "embargo",
    "bloqueo",
}

SPANISH_POSITIVE = {_strip_accents(w) for w in SPANISH_POSITIVE}
SPANISH_NEGATIVE = {_strip_accents(w) for w in SPANISH_NEGATIVE}

_TOKEN_RE = re.compile(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]+")


def _tokenize(text: str) -> list[str]:
    """Extrae tokens normalizados (minúsculas, sin acentos) del texto."""
    return [_strip_accents(t) for t in _TOKEN_RE.findall(text)]


def score_spanish_lexicon(text: str) -> dict:
    """
    Puntúa un texto con el léxico español propio.

    polarity = (n_pos - n_neg) / (n_pos + n_neg + 1), en [-1, 1].
    subjectivity = fracción de tokens cubiertos por el léxico (0 = nada léxico).
    Una negación ("no", "nunca"...) invierte la polaridad de la palabra
    de sentimiento que sigue en la ventana de 3 tokens.

    Umbral ±0.1: heurístico, sin calibrar, ver README.
    """
    tokens = _tokenize(text)
    n_pos = 0
    n_neg = 0
    for i, tok in enumerate(tokens):
        if tok in SPANISH_POSITIVE:
            polarity = 1
        elif tok in SPANISH_NEGATIVE:
            polarity = -1
        else:
            continue
        window = tokens[max(0, i - 3) : i]
        if any(w in NEGATION_WORDS for w in window):
            polarity = -polarity
        if polarity > 0:
            n_pos += 1
        else:
            n_neg += 1

    denom = n_pos + n_neg + 1
    polarity_score = round((n_pos - n_neg) / denom, 4)
    subjectivity = round((n_pos + n_neg) / max(len(tokens), 1), 4)

    if polarity_score > POSITIVE_THRESHOLD:
        label = "positivo"
    elif polarity_score < NEGATIVE_THRESHOLD:
        label = "negativo"
    else:
        label = "neutral"

    return {
        "polarity": polarity_score,
        "subjectivity": subjectivity,
        "label": label,
    }


def analyze_sentiment_lexicon(texts: list[str]) -> list[dict]:
    """Análisis de sentimiento con el léxico español propio (método primario)."""
    return [score_spanish_lexicon(text) for text in texts]


def analyze_sentiment_textblob(texts: list[str]) -> list[dict]:
    """
    Análisis de sentimiento con TextBlob (método secundario de referencia).

    TextBlob usa un léxico y modelo entrenados sobre textos en inglés; su
    aplicabilidad a discursos en español NO está validada. Se conserva solo
    como comparación documentada, no como método principal.
    """
    if not TEXTBLOB_AVAILABLE:
        print("[SENTIMENT] TextBlob no instalado. pip install textblob")
        return []
    results = []
    for text in texts:
        blob = TextBlob(text[:5000])
        results.append(
            {
                "polarity": round(blob.sentiment.polarity, 4),
                "subjectivity": round(blob.sentiment.subjectivity, 4),
                "label": "positivo"
                if blob.sentiment.polarity > 0.1
                else "negativo"
                if blob.sentiment.polarity < -0.1
                else "neutral",
            }
        )
    return results


def run_sentiment_analysis(
    data_dir: Path = Path("data"), output_dir: Path = Path("data/export")
) -> dict:
    """
    Análisis de sentimiento de discursos geopolíticos.

    Método: léxico español propio (sin red, sin APIs externas).
    Los umbrales ±0.1 son heurísticos y no están calibrados.

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

    print("[SENTIMENT] Usando léxico español propio (heurístico, sin calibrar)")
    sentiments = analyze_sentiment_lexicon(texts)

    # Aggregate
    df = pd.DataFrame(sentiments)
    df["source"] = sources[: len(df)]

    polarity_dist = {
        "positivo": len(df[df["label"] == "positivo"]),
        "neutral": len(df[df["label"] == "neutral"]),
        "negativo": len(df[df["label"] == "negativo"]),
    }

    results = {
        "method": "lexicon_es",
        "thresholds_uncalibrated": True,
        "n_documents": len(texts),
        "polarity_distribution": polarity_dist,
        "mean_polarity": round(df["polarity"].mean(), 4)
        if "polarity" in df.columns
        else 0,
        "mean_subjectivity": round(df["subjectivity"].mean(), 4)
        if "subjectivity" in df.columns
        else 0,
        "per_document": df.to_dict(orient="records")
        if len(df) <= 50
        else df.head(20).to_dict(orient="records"),
    }

    print(f"[SENTIMENT] Distribución: {polarity_dist}")
    print(f"[SENTIMENT] Polaridad media: {results['mean_polarity']:.3f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "sentiment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    run_sentiment_analysis()
