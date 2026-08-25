"""Download and process Chilean presidential speeches from BCN and presidencia.cl.

Downloads PDFs, extracts text with pdfplumber, and saves:
  - Individual JSON files to data/raw/speeches/
  - A consolidated CSV to data/processed/speeches.csv

Usage:
    python src/collect_speeches.py
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path

import pandas as pd
import pdfplumber
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "speeches"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_CSV = PROCESSED_DIR / "speeches.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*",
}

# Real Chilean presidential speeches (Cuentas Públicas and first messages).
# Source: BCN Historia Política and presidencia.cl
SPEECHES: list[dict[str, str]] = [
    {
        "year": "1832",
        "speaker": "José Joaquín Prieto",
        "description": "Primer mensaje presidencial",
        "url": "https://www.bcn.cl/historiapolitica/constitucion/ref/ML-0832000-1",
        "filename": "1832_prieto_primer_mensaje.pdf",
    },
    {
        "year": "1842",
        "speaker": "Manuel Montt",
        "description": "Mensaje anual al Congreso",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=6",
        "filename": "1842_montt_cuenta_publica.pdf",
    },
    {
        "year": "1873",
        "speaker": "José Manuel Balmaceda",
        "description": "Mensaje anual al Congreso",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=15",
        "filename": "1873_balmaceda_cuenta_publica.pdf",
    },
    {
        "year": "1902",
        "speaker": "Germán Riesco",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=22",
        "filename": "1902_riesco_cuenta_publica.pdf",
    },
    {
        "year": "1925",
        "speaker": "Emiliano Figueroa",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=27",
        "filename": "1925_figueroa_cuenta_publica.pdf",
    },
    {
        "year": "1932",
        "speaker": "Arturo Alessandri",
        "description": "Segundo gobierno - Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=29",
        "filename": "1932_alessandri_cuenta_publica.pdf",
    },
    {
        "year": "1942",
        "speaker": "Juan Antonio Ríos",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=31",
        "filename": "1942_rios_cuenta_publica.pdf",
    },
    {
        "year": "1946",
        "speaker": "Gabriel González Videla",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=32",
        "filename": "1946_gonzalez_videla_cuenta_publica.pdf",
    },
    {
        "year": "1952",
        "speaker": "Carlos Ibáñez del Campo",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=34",
        "filename": "1952_ibanez_cuenta_publica.pdf",
    },
    {
        "year": "1960",
        "speaker": "Jorge Alessandri",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=36",
        "filename": "1960_jalessandri_cuenta_publica.pdf",
    },
    {
        "year": "1965",
        "speaker": "Eduardo Frei Montalva",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=37",
        "filename": "1965_frei_montalva_cuenta_publica.pdf",
    },
    {
        "year": "1971",
        "speaker": "Salvador Allende",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=39",
        "filename": "1971_allende_cuenta_publica.pdf",
    },
    {
        "year": "1990",
        "speaker": "Patricio Aylwin",
        "description": "Primer mensaje anual al Congreso Nacional",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=42",
        "filename": "1990_aylwin_cuenta_publica.pdf",
    },
    {
        "year": "1994",
        "speaker": "Eduardo Frei Ruiz-Tagle",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=43",
        "filename": "1994_frei_rt_cuenta_publica.pdf",
    },
    {
        "year": "2000",
        "speaker": "Ricardo Lagos",
        "description": "Cuenta Pública",
        "url": "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/detalle?tipo=presidentes&id=44",
        "filename": "2000_lagos_cuenta_publica.pdf",
    },
    {
        "year": "2006",
        "speaker": "Michelle Bachelet",
        "description": "Primer gobierno - Cuenta Pública",
        "url": "https://s3.amazonaws.com/gobcl-prod/public_files/Campa%C3%B1as/Cuenta-P%C3%BAblica-2006/Cuenta_Publica_2006.pdf",
        "filename": "2006_bachelet_1_cuenta_publica.pdf",
    },
    {
        "year": "2010",
        "speaker": "Sebastián Piñera",
        "description": "Primer gobierno - Cuenta Pública",
        "url": "https://s3.amazonaws.com/gobcl-prod/public_files/Campa%C3%B1as/Cuenta-P%C3%BAblica-2010/Cuenta_Publica_2010.pdf",
        "filename": "2010_pinera_1_cuenta_publica.pdf",
    },
    {
        "year": "2014",
        "speaker": "Michelle Bachelet",
        "description": "Segundo gobierno - Cuenta Pública",
        "url": "https://s3.amazonaws.com/gobcl-prod/public_files/Campa%C3%B1as/Cuenta-P%C3%BAblica-2014/Cuenta_Publica_2014.pdf",
        "filename": "2014_bachelet_2_cuenta_publica.pdf",
    },
    {
        "year": "2018",
        "speaker": "Sebastián Piñera",
        "description": "Segundo gobierno - Cuenta Pública",
        "url": "https://s3.amazonaws.com/gobcl-prod/public_files/Campa%C3%B1as/Cuenta-P%C3%BAblica-2018/Cuenta_Publica_2018.pdf",
        "filename": "2018_pinera_2_cuenta_publica.pdf",
    },
    {
        "year": "2022",
        "speaker": "Gabriel Boric",
        "description": "Cuenta Pública",
        "url": "https://s3.amazonaws.com/gobcl-prod/public_files/Campa%C3%B1as/Cuenta-P%C3%BAblica-2022/Cuenta_Publica_2022.pdf",
        "filename": "2022_boric_cuenta_publica.pdf",
    },
]


def _slugify(text: str) -> str:
    """Sanitize text for filenames."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "_", text).strip("_")


def download_pdf(url: str, dest: Path, retries: int = 2) -> bool:
    """Download a PDF file. Returns True on success."""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, verify=False)
            if resp.status_code == 200 and "pdf" in resp.headers.get("Content-Type", "").lower():
                dest.write_bytes(resp.content)
                return True
            if resp.status_code == 200 and len(resp.content) > 1000:
                dest.write_bytes(resp.content)
                return True
        except requests.RequestException as exc:
            print(f"  [WARN] Attempt {attempt + 1} failed for {url}: {exc}")
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    return False


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF using pdfplumber."""
    pages_text: list[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as exc:
        print(f"  [WARN] pdfplumber failed for {pdf_path.name}: {exc}")
        return ""
    return "\n\n".join(pages_text)


def save_speech_json(speech: dict, text: str, output_dir: Path) -> None:
    """Save a single speech as a JSON file."""
    output = {
        "year": speech["year"],
        "speaker": speech["speaker"],
        "description": speech["description"],
        "source_url": speech["url"],
        "filename": speech["filename"],
        "text": text,
        "text_length": len(text),
    }
    json_path = output_dir / speech["filename"].replace(".pdf", ".json")
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    """Download speeches, extract text, and create consolidated CSV."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, str]] = []

    for speech in SPEECHES:
        print(f"[{speech['year']}] {speech['speaker']}...")
        pdf_path = RAW_DIR / speech["filename"]

        if not pdf_path.exists():
            ok = download_pdf(speech["url"], pdf_path)
            if not ok:
                print(f"  [SKIP] Could not download: {speech['url']}")
                continue
        else:
            print(f"  [OK] Already downloaded: {pdf_path.name}")

        text = extract_text_from_pdf(pdf_path)
        if not text or len(text) < 50:
            print(f"  [SKIP] No text extracted from {pdf_path.name}")
            continue

        save_speech_json(speech, text, RAW_DIR)

        results.append(
            {
                "year": speech["year"],
                "speaker": speech["speaker"],
                "text": text,
                "source_url": speech["url"],
            }
        )
        print(f"  [OK] Extracted {len(text):,} characters")

        time.sleep(1)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(PROCESSED_CSV, index=False, encoding="utf-8")
        print(f"\n[DONE] {len(df)} speeches saved to {PROCESSED_CSV}")
    else:
        print("\n[DONE] No speeches were processed. Check network connectivity.")


if __name__ == "__main__":
    main()
