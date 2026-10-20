"""Tests for collect_speeches module (BCN corpus download/parse)."""

from pathlib import Path
from typing import ClassVar

from src.collect_speeches import (
    DEFAULT_YEARS,
    download_pdf,
    parse_listing,
    parse_pdf_date,
    save_corpus,
    select_speeches,
)

FIXTURE_HTML = """
<section>
<div class="Rtable Rtable--3cols hide-row"><div class="Rtable-cell">Fecha</div></div>
<!-- row -->
<div class="Rtable Rtable--3cols gap">
    <div class="Rtable-cell"><span>1846-1842</span></div>
    <div class="Rtable-cell">
        <span>Discursos de S.E. Don Manuel Bulnes Prieto en la apertura:
        periodo 1841-1846</span>
    </div>
    <div class="Rtable-cell">
        <ul class="list-unstyled">
            <li>
                <a class="rspkr_dr_added" target="_blank"
                   href="https://www.bcn.cl/obtienearchivo?id=recursoslegales/10221.3/45809/1/18420601.pdf"
                   title="18420601.pdf" onclick="x()">
                   <i class="fa fa-file-pdf-o"></i> 01-06-1842</a>
                (<a rel="nofollow" class="text-danger ml-3"
                   href="http://docreader.readspeaker.com/docreader/?cid=bxvfy&amp;lang=es_mx&amp;url=https://www.bcn.cl/obtienearchivo?id=recursoslegales/10221.3/45809/1/18420601.pdf"
                   >Escuchar</a>)
            </li>
            <li>
                <a class="rspkr_dr_added" target="_blank"
                   href="https://www.bcn.cl/obtienearchivo?id=recursoslegales/10221.3/45809/2/18430601.pdf"
                   title="18430601.pdf" onclick="x()">
                   <i class="fa fa-file-pdf-o"></i> 01-06-1843</a>
            </li>
        </ul>
    </div>
</div>
<!-- row -->
<div class="Rtable Rtable--3cols gap">
    <div class="Rtable-cell"><span>2026-2022</span></div>
    <div class="Rtable-cell">
        <span>Mensajes Presidenciales de S.E. Don Gabriel Boric Font,
        01 junio: periodo 2022-2026</span>
    </div>
    <div class="Rtable-cell">
        <ul class="list-unstyled">
            <li>
                <a class="rspkr_dr_added" target="_blank"
                   href="https://www.bcn.cl/obtienearchivo?id=recursoslegales/10221.3/83042/1/01-06-2026.pdf"
                   title="01-06-2026.pdf" onclick="x()">
                   <i class="fa fa-file-pdf-o"></i> Descargar</a>
            </li>
        </ul>
    </div>
</div>
</section>
"""


def test_parse_pdf_date_yyyymmdd():
    url = "https://www.bcn.cl/obtienearchivo?id=recursoslegales/1/2/3/19940521.pdf"
    assert parse_pdf_date(url, "") == (1994, 5, 21)


def test_parse_pdf_date_dd_mm_yyyy_filename():
    url = "https://www.bcn.cl/obtienearchivo?id=recursoslegales/1/2/3/01-06-2026.pdf"
    assert parse_pdf_date(url, "") == (2026, 6, 1)


def test_parse_pdf_date_visible_fallback():
    url = "https://www.bcn.cl/obtienearchivo?id=recursoslegales/1/2/3/archivo.pdf"
    assert parse_pdf_date(url, "21-05-1990") == (1990, 5, 21)
    assert parse_pdf_date(url, "Descargar") is None


def test_parse_listing_extracts_speeches():
    refs = parse_listing(FIXTURE_HTML)
    assert len(refs) == 3
    years = sorted(r["year"] for r in refs)
    assert years == [1842, 1843, 2026]
    by_year = {r["year"]: r for r in refs}
    assert by_year[1842]["speaker"] == "Manuel Bulnes Prieto"
    assert by_year[2026]["speaker"] == "Gabriel Boric Font"
    assert by_year[1842]["url"].endswith("18420601.pdf")


def test_parse_listing_dedupes_docreader_links():
    refs = parse_listing(FIXTURE_HTML)
    urls = [r["url"] for r in refs]
    assert len(urls) == len(set(urls))
    assert all(u.startswith("https://www.bcn.cl/") for u in urls)


def test_select_speeches_missing_year_is_skipped():
    refs = parse_listing(FIXTURE_HTML)
    selected = select_speeches(refs, (1842, 1999))
    assert [s["year"] for s in selected] == [1842]


def test_select_speeches_prefers_may_june():
    refs = [
        {"year": 2000, "month": 9, "day": 11, "url": "b.pdf"},
        {"year": 2000, "month": 5, "day": 21, "url": "a.pdf"},
    ]
    selected = select_speeches(refs, (2000,))
    assert selected[0]["url"] == "a.pdf"


def test_default_years_has_no_duplicates():
    assert len(DEFAULT_YEARS) == len(set(DEFAULT_YEARS))


def test_download_pdf_rejects_non_pdf(tmp_path, monkeypatch):
    class FakeResponse:
        status_code = 200
        headers: ClassVar[dict[str, str]] = {"Content-Type": "text/html"}
        content = b"<!DOCTYPE html><html>404</html>"

    import src.collect_speeches as mod

    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: FakeResponse())
    dest = tmp_path / "fake.pdf"
    assert download_pdf("https://example.org/x.pdf", dest, retries=0) is False
    assert not dest.exists()


def test_download_pdf_accepts_pdf_magic(tmp_path, monkeypatch):
    class FakeResponse:
        status_code = 200
        headers: ClassVar[dict[str, str]] = {"Content-Type": "application/pdf"}
        content = b"%PDF-1.4 fake content"

    import src.collect_speeches as mod

    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: FakeResponse())
    dest = tmp_path / "real.pdf"
    assert download_pdf("https://example.org/x.pdf", dest, retries=0) is True
    assert dest.read_bytes().startswith(b"%PDF-")


def test_save_corpus_writes_attribution(tmp_path):
    import pandas as pd

    from src.collect_speeches import SOURCE_ATTRIBUTION

    df = pd.DataFrame(
        [
            {
                "year": 1842,
                "speaker": "Manuel Bulnes Prieto",
                "text": "Discurso real extraído del PDF.",
                "description": "Discursos de S.E. Don Manuel Bulnes Prieto: periodo 1841-1846",
                "source_url": "https://www.bcn.cl/obtienearchivo?id=x/18420601.pdf",
                "source": SOURCE_ATTRIBUTION,
            }
        ]
    )
    out = tmp_path / "speeches.csv"
    save_corpus(df, out)
    back = pd.read_csv(out)
    assert list(back.columns) == [
        "year",
        "speaker",
        "text",
        "description",
        "source_url",
        "source",
    ]
    assert "Biblioteca del Congreso Nacional" in back.loc[0, "source"]
    assert Path(out).exists()
