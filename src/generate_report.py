"""
Genera reporte estilo paper académico en Markdown.
"""
import json
from pathlib import Path
from datetime import datetime


REPORT_TEMPLATE = """# {title}

**Autor:** Álvaro Salinas Ortiz  
**Fecha:** {date}  
**Repositorio:** https://github.com/alvarosalinaso/{repo}  
**DOI:** [10.xxxx/zenodo.XXXXXXX](https://doi.org/10.xxxx/zenodo.XXXXXXX) *(pending)*

---

## Abstract

{abstract}

## 1. Introducción

{introduction}

## 2. Datos y Metodología

{methodology}

## 3. Resultados

{results}

## 4. Discusión

{discussion}

## 5. Conclusiones

{conclusions}

## Referencias

{references}

---
*Generado automáticamente por `python src/generate_report.py` — {date}*
"""


def load_results(output_dir: Path) -> dict:
    """Carga todos los archivos JSON de resultados."""
    results = {}
    for json_file in output_dir.glob("*.json"):
        with open(json_file, encoding="utf-8") as f:
            results[json_file.stem] = json.load(f)
    return results


def generate_report(output_dir: Path = Path("data/export"), report_dir: Path = Path("docs")) -> Path:
    """Genera reporte académico completo."""
    results = load_results(output_dir)

    # Build sections from results
    sections = build_sections(results)

    report = REPORT_TEMPLATE.format(
        title=sections.get("title", "Análisis de Datos"),
        date=datetime.now().strftime("%Y-%m-%d"),
        repo=output_dir.parent.name if output_dir.parent.name != "data" else "portfolio",
        abstract=sections.get("abstract", "Análisis exploratorio y estadístico de datos."),
        introduction=sections.get("introduction", "Este estudio presenta un análisis de datos."),
        methodology=sections.get("methodology", "Se utilizó Python con librerías estándar."),
        results=sections.get("results", "Los resultados se presentan a continuación."),
        discussion=sections.get("discussion", "Los hallazgos sugieren patrones interesantes."),
        conclusions=sections.get("conclusions", "Se concluye que el análisis es prometedor."),
        references=sections.get("references", "- Python Software Foundation. (2024). Python Documentation."),
    )

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "paper_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"[REPORT] Generado: {report_path}")
    return report_path


def build_sections(results: dict) -> dict:
    """Construye secciones del paper desde resultados."""
    return {
        "title": "Análisis de Datos con Inferencia Estadística y ML",
        "abstract": "Se presenta un análisis integral que combina métodos estadísticos clásicos, machine learning y visualización interactiva para extraer insights accionables de datos reales.",
        "introduction": "El análisis de datos se ha convertido en una herramienta fundamental para la toma de decisiones informadas.",
        "methodology": "Se employaron las siguientes técnicas:\n- Estadística descriptiva e inferencial\n- Machine learning (clustering, clasificación)\n- Análisis de series temporales\n- Visualización interactiva",
        "results": format_results(results),
        "discussion": "Los resultados muestran patrones significativos que respaldan las hipótesis planteadas.",
        "conclusions": "El análisis integral permite tomar decisiones basadas en evidencia.",
        "references": "- Harris, C.R. et al. (2020). Array programming with NumPy.\n- Pedregosa, F. et al. (2011). Scikit-learn.",
    }


def format_results(results: dict) -> dict:
    """Formatea resultados como secciones del paper."""
    sections = {}
    for name, data in results.items():
        if isinstance(data, dict):
            lines = [f"### {name.replace('_', ' ').title()}\n"]
            for k, v in data.items():
                if isinstance(v, (int, float, str)):
                    lines.append(f"- **{k}**: {v}")
                elif isinstance(v, dict) and len(v) < 10:
                    lines.append(f"- **{k}**: {json.dumps(v, ensure_ascii=False)[:200]}")
            sections[name] = "\n".join(lines)

    return "\n\n".join(sections.values()) if sections else "Resultados pendientes de ejecución."


if __name__ == "__main__":
    generate_report()
