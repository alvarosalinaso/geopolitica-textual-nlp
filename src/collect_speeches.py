"""Descarga los Mensajes Presidenciales (Cuentas Públicas) desde el sitio de la BCN.

Ajuste A-2 (auditoría 2026-10):
- Los PDF se descargan en ejecución a ``data/raw/speeches/``, carpeta ignorada por git.
  NUNCA se commitean PDFs de BCN.
- En el repositorio solo queda el texto extraído en ``data/processed/speeches.csv``
  con la URL de origen de cada discurso y la atribución a la Biblioteca del Congreso
  Nacional (BCN).
- Las URLs NO están hardcodeadas: se obtienen parseando el índice oficial de
  "Mensajes Presidenciales ante el Congreso Pleno" de Historia Política (BCN). Esto
  corrige las URLs rotas anteriores (S3 gobcl con 403 y ML-0832000-1 con 404).

Base legal del texto conservado en el repo: Ley 17.336 de Propiedad Intelectual
(Chile), art. 41 — "Quedan excluidas de la protección de la presente ley [...] cualquier
documento público del Estado, tales como [...] discursos oficiales de autoridades
públicas [...], cuya reproducción será lícita después de publicadas por el Estado y
siempre que obedezcan fielmente al texto original". Los Mensajes Presidenciales ante el
Congreso son discursos oficiales publicados por el Estado (BCN/Congreso). El texto se
reproduce sin alteraciones, con URL de origen y atribución.

Uso:
    python src/collect_speeches.py                # año por defecto de la selección curada
    python src/collect_speeches.py --years 1842 1990
"""

from __future__ import annotations

import argparse
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

# Índice oficial (una sola página con todos los períodos, 1832–actualidad)
LISTING_URL = (
    "https://www.bcn.cl/historiapolitica/corporaciones/cuentas_publicas/"
    "detalle?tipo=presidentes"
)

SOURCE_ATTRIBUTION = (
    "Biblioteca del Congreso Nacional (BCN) — Historia Política: "
    "Mensajes Presidenciales ante el Congreso Pleno"
)

# Selección curada: un mensaje por presidencia/período, cubriendo 1832–2022.
# Nota: el índice de la BCN no publica 1925; se usa 1926 (mismo gobierno,
# Emiliano Figueroa) en su lugar.
DEFAULT_YEARS: tuple[int, ...] = (
    1832,
    1842,
    1873,
    1902,
    1926,
    1932,
    1942,
    1946,
    1952,
    1960,
    1965,
    1971,
    1990,
    1994,
    2000,
    2006,
    2010,
    2014,
    2018,
    2022,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/pdf,*/*",
}

ROW_RE = re.compile(
    r'<div class="Rtable Rtable--3cols gap">(.*?)(?=<div class="Rtable Rtable--3cols'
    r' gap">|</section>)',
    re.DOTALL,
)
ANCHOR_RE = re.compile(
    r'<a\s[^>]*href="(https://www\.bcn\.cl/obtienearchivo\?id=[^"]+?\.pdf)"'
    r"[^>]*>(.*?)</a>",
    re.DOTALL,
)
DATE_RE = re.compile(r"(\d{1,2})-(\d{1,2})-(\d{4})")
SPEAKER_RE = re.compile(
    r"(?:S\.E\.\s*)?(?:Don|Doña)\s+"
    r"((?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ'’.-]*\s*){1,4})"
)


def parse_pdf_date(url: str, visible_text: str) -> tuple[int, int, int] | None:
    """Obtiene (year, month, day) de un PDF a partir de su nombre o texto visible.

    El índice de la BCN mezcla dos formatos de nombre de archivo:
    ``20250601.pdf`` (yyyymmdd) y ``01-06-2026.pdf`` (dd-mm-yyyy).
    """
    name = url.rsplit("/", 1)[-1]
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    if re.fullmatch(r"\d{8}", name):
        return int(name[:4]), int(name[4:6]), int(name[6:8])
    if re.fullmatch(r"\d{1,2}-\d{1,2}-\d{4}", name):
        day, month, year = name.split("-")
        return int(year), int(month), int(day)
    match = DATE_RE.search(visible_text)
    if match:
        day, month, year = match.groups()
        return int(year), int(month), int(day)
    return None


def _slugify(text: str) -> str:
    """Sanitize text for filenames."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "_", text).strip("_")


def fetch_listing(url: str = LISTING_URL, timeout: int = 60) -> str:
    """Descarga el índice HTML de Mensajes Presidenciales de la BCN."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_listing(html: str) -> list[dict]:
    """Extrae todas las referencias a PDF del índice de la BCN.

    Retorna una lista de dicts con: year, month, day, url, speaker, row_title.
    """
    refs: list[dict] = []
    seen_urls: set[str] = set()
    for chunk in ROW_RE.findall(html):
        anchors = ANCHOR_RE.findall(chunk)
        if not anchors:
            continue
        titles = re.findall(r"<span>(.*?)</span>", chunk, re.DOTALL)
        row_title = " ".join(re.sub(r"<[^>]+>", "", t).strip() for t in titles)
        speaker_match = SPEAKER_RE.search(row_title)
        speaker = " ".join(speaker_match.group(1).split()) if speaker_match else ""
        for url, inner in anchors:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            visible = re.sub(r"<[^>]+>", " ", inner).strip()
            date = parse_pdf_date(url, visible)
            if date is None:
                continue
            year, month, day = date
            refs.append(
                {
                    "year": year,
                    "month": month,
                    "day": day,
                    "url": url,
                    "speaker": speaker,
                    "row_title": row_title.strip(),
                }
            )
    return refs


def select_speeches(refs: list[dict], years: tuple[int, ...]) -> list[dict]:
    """Elige un discurso por año pedido.

    Preferencia: mensajes de apertura de mayo/junio (fechas típicas 21-05 / 01-06);
    desempate determinista por URL. Los años ausentes del índice se omiten.
    """
    selected: list[dict] = []
    for year in years:
        candidates = [r for r in refs if r["year"] == year]
        if not candidates:
            print(f"  [SKIP] {year}: no está en el índice de la BCN")
            continue
        candidates.sort(key=lambda r: (0 if r["month"] in (5, 6) else 1, r["url"]))
        selected.append(candidates[0])
    return selected


def download_pdf(url: str, dest: Path, retries: int = 3) -> bool:
    """Descarga un PDF validando que realmente sea PDF. True si tuvo éxito."""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            if resp.status_code == 200 and resp.content[:5] == b"%PDF-":
                dest.write_bytes(resp.content)
                return True
            if resp.status_code == 200:
                print(
                    f"  [WARN] Respuesta no-PDF ({resp.headers.get('Content-Type')})"
                    f" para {url} — no se guarda"
                )
                return False
        except requests.RequestException as exc:
            print(f"  [WARN] Intento {attempt + 1} falló para {url}: {exc}")
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    return False


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrae el texto completo de un PDF con pdfplumber."""
    pages_text: list[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as exc:  # noqa: BLE001
        print(f"  [WARN] pdfplumber falló para {pdf_path.name}: {exc}")
        return ""
    return "\n\n".join(pages_text)


def build_corpus(
    years: tuple[int, ...] = DEFAULT_YEARS, raw_dir: Path = RAW_DIR
) -> pd.DataFrame:
    """Descarga los PDF seleccionados y extrae el texto a un DataFrame."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("[1/3] Obteniendo índice de la BCN...")
    refs = parse_listing(fetch_listing())
    print(f"      {len(refs)} documentos en el índice")
    selected = select_speeches(refs, years)
    print(f"      {len(selected)} años seleccionados")

    rows: list[dict] = []
    for ref in selected:
        year = ref["year"]
        print(f"[2/3] {year} {ref['speaker'] or '(sin orador parseado)'}...")
        filename = f"{year}_{_slugify(ref['speaker'] or 'discurso')}.pdf"
        pdf_path = raw_dir / filename

        if not pdf_path.exists():
            if not download_pdf(ref["url"], pdf_path):
                print(f"  [SKIP] Descarga fallida: {ref['url']}")
                continue
        else:
            print(f"  [OK] PDF ya descargado: {filename}")

        text = extract_text_from_pdf(pdf_path)
        if not text or len(text) < 200:
            print(f"  [SKIP] Texto insuficiente en {filename}")
            continue

        rows.append(
            {
                "year": year,
                "speaker": ref["speaker"],
                "text": text,
                "description": ref["row_title"],
                "source_url": ref["url"],
                "source": SOURCE_ATTRIBUTION,
            }
        )
        print(f"  [OK] {len(text):,} caracteres extraídos")
        time.sleep(0.5)

    return pd.DataFrame(rows)


def save_corpus(df: pd.DataFrame, csv_path: Path = PROCESSED_CSV) -> None:
    """Guarda el corpus extraído (solo texto + URL origen + atribución BCN)."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[3/3] {len(df)} discursos guardados en {csv_path}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=list(DEFAULT_YEARS),
        help="Años a descargar (por defecto: selección curada 1832-2022)",
    )
    args = parser.parse_args(argv)

    df = build_corpus(tuple(args.years))
    if df.empty:
        print("\n[DONE] Ningún discurso procesado. Revisa la conexión a la BCN.")
        return
    save_corpus(df)


if __name__ == "__main__":
    main()
