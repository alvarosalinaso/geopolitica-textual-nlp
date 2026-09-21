import sys
import tempfile
import pandas as pd
from pathlib import Path

# Test corpus processor
tmp = Path(tempfile.mkdtemp())

# Create sample CSV
csv_path = tmp / "speeches.csv"
pd.DataFrame({
    "year": [2020, 2021],
    "speaker": ["Speaker A", "Speaker B"],
    "text": ["El presidente de Chile visitó Argentina.", "Mención a Brasil y Perú."]
}).to_csv(csv_path, index=False)

sys.path.insert(0, 'src')
from corpus_processor import GeopoliticalExtractor, create_sample_speeches

extractor = GeopoliticalExtractor("es_core_news_sm")
if extractor.nlp is None:
    print("spaCy model not available, skipping NLP tests")
else:
    # Test process_corpus
    result = extractor.process_corpus(str(csv_path))
    print("process_corpus result:")
    print(result)
    assert isinstance(result, pd.DataFrame)
    assert "Year" in result.columns
    assert "Speaker" in result.columns
    assert "Mentioned_Location" in result.columns
    print("process_corpus: PASS")
    
    # Test extract_entities_with_confidence
    text = "El presidente de Chile visitó Argentina y se reunió en Santiago."
    entities = extractor.extract_entities_with_confidence(text)
    print("extract_entities_with_confidence:")
    for ent in entities:
        print(f"  {ent}")
    assert isinstance(entities, list)
    assert len(entities) >= 2
    for ent in entities:
        assert "text" in ent
        assert "label" in ent
        assert "start_char" in ent
        assert "end_char" in ent
        assert "confidence" in ent
    print("extract_entities_with_confidence: PASS")

# Test create_sample_speeches
df = create_sample_speeches()
print("create_sample_speeches:")
print(df)
assert isinstance(df, pd.DataFrame)
assert len(df) >= 7
assert "year" in df.columns
assert "speaker" in df.columns
assert "text" in df.columns
all_text = " ".join(df["text"].tolist())
assert "Chile" in all_text
assert "Santiago" in all_text
print("create_sample_speeches: PASS")

print("\nAll tests passed!")