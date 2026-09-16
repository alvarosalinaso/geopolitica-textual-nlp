"""Dash Dashboard: Chilean Political Discourse NLP Analysis — Illuminated Manuscript Edition."""

import json
from pathlib import Path

import dash
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

app = dash.Dash(
    __name__,
    title="Discurso Presidencial Chileno — NLP",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

COLORS = {
    "parchment": "#f4e8c1",
    "parchment_light": "#faf0d7",
    "burgundy": "#6b1d1d",
    "burgundy_light": "#8a2e2e",
    "gold": "#c5a55a",
    "gold_light": "#d4b96e",
    "green": "#2d5016",
    "navy": "#1a2744",
    "text": "#3a2a1a",
    "text_muted": "#7a6a5a",
    "cream": "#faf0d7",
    "border_gold": "#c5a55a",
    "border_burgundy": "#6b1d1d",
}

DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = DATA_DIR / "export"


def load_data():
    data = {}
    csv_path = PROCESSED_DIR / "speeches.csv"
    if csv_path.exists():
        data["speeches"] = pd.read_csv(csv_path)
    ner_path = EXPORT_DIR / "ner_entities.json"
    if ner_path.exists():
        with open(ner_path) as f:
            data["ner"] = json.load(f)
    sent_path = EXPORT_DIR / "sentiment_results.json"
    if sent_path.exists():
        with open(sent_path) as f:
            data["sentiment"] = json.load(f)
    topics_path = EXPORT_DIR / "topics.json"
    if topics_path.exists():
        with open(topics_path) as f:
            data["topics"] = json.load(f)
    return data


DATA = load_data()

PAPER_TEXTURE = (
    "repeating-linear-gradient("
    "0deg, transparent, transparent 2px, rgba(139,119,80,0.03) 2px, rgba(139,119,80,0.03) 4px),"
    "repeating-linear-gradient("
    "90deg, transparent, transparent 2px, rgba(139,119,80,0.03) 2px, rgba(139,119,80,0.03) 4px)"
)


def ornate_border(extra_style=None):
    base = {
        "border": f"2px solid {COLORS['border_gold']}",
        "outline": f"1px solid {COLORS['border_burgundy']}",
        "outlineOffset": "3px",
    }
    if extra_style:
        base.update(extra_style)
    return base


def flourish(char="❧"):
    return html.Span(
        char,
        style={"color": COLORS["gold"], "fontSize": "1.4rem", "margin": "0 8px"},
    )


def section_divider():
    return html.Div(
        style={
            "textAlign": "center",
            "margin": "35px 0 30px 0",
            "padding": "0 40px",
            "display": "flex",
            "alignItems": "center",
            "gap": "12px",
            "justifyContent": "center",
        },
        children=[
            html.Span("—", style={"color": COLORS["gold"], "letterSpacing": "4px"}),
            html.Span("✦", style={"color": COLORS["burgundy"], "fontSize": "1rem"}),
            html.Span("—", style={"color": COLORS["gold"], "letterSpacing": "4px"}),
        ],
    )


def chapter_header(numeral, title):
    return html.Div(
        style={
            "textAlign": "center",
            "marginBottom": "30px",
            "paddingBottom": "20px",
            "borderBottom": f"2px solid {COLORS['gold']}",
            "position": "relative",
        },
        children=[
            html.Div(
                "✦  ❋  ✦",
                style={"color": COLORS["gold"], "fontSize": "0.8rem", "letterSpacing": "6px", "marginBottom": "8px"},
            ),
            html.Div(
                f"Caput {numeral}",
                style={
                    "fontSize": "0.85rem",
                    "color": COLORS["text_muted"],
                    "fontStyle": "italic",
                    "letterSpacing": "3px",
                    "textTransform": "uppercase",
                    "marginBottom": "6px",
                },
            ),
            html.H2(
                title,
                style={
                    "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
                    "fontSize": "1.8rem",
                    "fontWeight": "bold",
                    "color": COLORS["burgundy"],
                    "margin": "0",
                    "letterSpacing": "1px",
                },
            ),
            html.Div(
                "❧",
                style={
                    "color": COLORS["gold"],
                    "fontSize": "1.2rem",
                    "marginTop": "10px",
                },
            ),
        ],
    )


def card(title, children, color=None):
    if color is None:
        color = COLORS["parchment_light"]
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": color,
            "borderRadius": "4px",
            "padding": "25px 28px",
            "marginBottom": "28px",
            **ornate_border(),
            "boxShadow": "2px 3px 12px rgba(58,42,26,0.15)",
            "backgroundImage": PAPER_TEXTURE,
        },
        children=[
            html.H3(
                [flourish("✦"), title, flourish("✦")],
                style={
                    "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
                    "color": COLORS["burgundy"],
                    "fontSize": "1.2rem",
                    "fontWeight": "bold",
                    "marginBottom": "18px",
                    "paddingBottom": "12px",
                    "borderBottom": f"2px solid {COLORS['gold']}",
                    "textAlign": "center",
                    "letterSpacing": "1px",
                },
            ),
        ] + child_list,
    )


def stat_row(stats):
    return html.Div(
        style={
            "display": "flex",
            "gap": "18px",
            "flexWrap": "wrap",
            "marginBottom": "30px",
            "justifyContent": "center",
        },
        children=[
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "160px",
                    "backgroundColor": COLORS["parchment_light"],
                    **ornate_border({
                        "borderRadius": "4px",
                        "padding": "22px 16px",
                        "textAlign": "center",
                        "boxShadow": "2px 2px 8px rgba(58,42,26,0.12)",
                        "backgroundImage": PAPER_TEXTURE,
                    }),
                },
                children=[
                    html.Div(
                        str(val),
                        style={
                            "fontSize": "2.4rem",
                            "fontWeight": "bold",
                            "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
                            "color": COLORS["burgundy"],
                            "lineHeight": "1",
                        },
                    ),
                    html.Div(
                        label,
                        style={
                            "fontSize": "0.75rem",
                            "color": COLORS["text_muted"],
                            "marginTop": "6px",
                            "textTransform": "uppercase",
                            "letterSpacing": "2px",
                            "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
                        },
                    ),
                ],
            )
            for val, label in stats
        ],
    )


PLOTLY_MANUSCRIPT_TEMPLATE = {
    "layout": {
        "paper_bgcolor": COLORS["parchment_light"],
        "plot_bgcolor": COLORS["parchment"],
        "font": {
            "family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
            "color": COLORS["text"],
        },
        "title": {
            "font": {"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["burgundy"], "size": 16},
            "x": 0.5,
            "xanchor": "center",
        },
        "xaxis": {"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
        "yaxis": {"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
    }
}

GOLD_BURGUNDY_SCALE = [
    "#c5a55a",
    "#b8944e",
    "#ab8342",
    "#9e7236",
    "#8a2e2e",
    "#6b1d1d",
]

WARM_BARS = [COLORS["gold"], COLORS["burgundy"], COLORS["green"], COLORS["navy"]]


def _build_layout():
    if "speeches" not in DATA:
        return card("Discurso NLP", html.P("No hay datos disponibles"))

    df = DATA["speeches"]
    stats = stat_row([
        (str(len(df)), "Discursos"),
        (str(df["speaker"].nunique()), "Presidentes"),
        (str(int(df["year"].min())) + "–" + str(int(df["year"].max())), "Periodo"),
    ])

    fig_timeline = px.scatter(
        df, x="year", y="speaker", color="speaker",
        hover_data=["text"], title="Discursos por Ano y Presidente",
    )
    fig_timeline.update_layout(
        template=PLOTLY_MANUSCRIPT_TEMPLATE,
        paper_bgcolor=COLORS["parchment_light"],
        plot_bgcolor=COLORS["parchment"],
        showlegend=False,
        height=500,
        font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
        title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
        xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
        yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
    )
    for trace in fig_timeline.data:
        trace.update(marker=dict(color=COLORS["burgundy"], size=10, symbol="diamond"))

    df2 = df.copy()
    df2["word_count"] = df2["text"].str.split().str.len()
    fig_words = px.line(
        df2, x="year", y="word_count", color="speaker",
        title="Extension de Discursos (palabras)", markers=True,
    )
    fig_words.update_layout(
        template=PLOTLY_MANUSCRIPT_TEMPLATE,
        paper_bgcolor=COLORS["parchment_light"],
        plot_bgcolor=COLORS["parchment"],
        height=400,
        font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
        title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
        xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
        yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
        legend={"font": {"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif"}},
    )
    for trace in fig_words.data:
        trace.update(
            line={"color": COLORS["burgundy"], "width": 2},
            marker={"symbol": "diamond", "size": 8, "color": COLORS["gold"], "line": {"color": COLORS["burgundy"], "width": 1}},
        )

    ner_block = html.P(
        "Ejecuta python src/analyze_all.py para generar datos NER",
        style={"fontStyle": "italic", "color": COLORS["text_muted"], "textAlign": "center"},
    )
    if "ner" in DATA and "top_entities" in DATA["ner"]:
        entities_df = pd.DataFrame(DATA["ner"]["top_entities"])
        fig_entities = px.bar(
            entities_df.head(20), x="count", y="entity", color="label",
            orientation="h", title="Top 20 Entidades Mas Mencionadas",
            color_discrete_sequence=WARM_BARS,
        )
        fig_entities.update_layout(
            template=PLOTLY_MANUSCRIPT_TEMPLATE,
            paper_bgcolor=COLORS["parchment_light"],
            plot_bgcolor=COLORS["parchment"],
            height=600,
            font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
            title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
            xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
            yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a", "categoryorder": "total ascending"},
        )
        for trace in fig_entities.data:
            trace.update(marker={"line": {"color": COLORS["burgundy"], "width": 1}})

        label_counts = entities_df["label"].value_counts()
        fig_labels = px.pie(
            values=label_counts.values, names=label_counts.index,
            title="Distribucion de Tipos de Entidad",
            color_discrete_sequence=[COLORS["burgundy"], COLORS["gold"], COLORS["green"], COLORS["navy"]],
        )
        fig_labels.update_layout(
            template=PLOTLY_MANUSCRIPT_TEMPLATE,
            paper_bgcolor=COLORS["parchment_light"],
            plot_bgcolor=COLORS["parchment"],
            height=400,
            font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
            title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
        )
        for trace in fig_labels.data:
            trace.update(marker={"line": {"color": COLORS["cream"], "width": 2}})

        ner_block = html.Div([
            card("Top 20 Entidades", dcc.Graph(figure=fig_entities)),
            card("Distribucion NER", dcc.Graph(figure=fig_labels)),
        ])

    sent_block = html.P(
        "Ejecuta python src/analyze_all.py para generar analisis de sentimiento",
        style={"fontStyle": "italic", "color": COLORS["text_muted"], "textAlign": "center"},
    )
    if "sentiment" in DATA and "per_document" in DATA["sentiment"]:
        sent_df = pd.DataFrame(DATA["sentiment"]["per_document"])
        if "polarity" in sent_df.columns:
            fig_sent = px.histogram(
                sent_df, x="polarity", nbins=30,
                title="Distribucion de Polaridad",
                color_discrete_sequence=[COLORS["burgundy"]],
            )
            fig_sent.update_layout(
                template=PLOTLY_MANUSCRIPT_TEMPLATE,
                paper_bgcolor=COLORS["parchment_light"],
                plot_bgcolor=COLORS["parchment"],
                height=400,
                font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
                title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
                xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
            )
            for trace in fig_sent.data:
                trace.update(marker={"color": COLORS["burgundy"], "line": {"color": COLORS["gold"], "width": 1}})
            sent_block = card("Sentimiento", dcc.Graph(figure=fig_sent))

    topics_block = html.P(
        "Ejecuta python src/topic_analysis.py para generar analisis de temas",
        style={"fontStyle": "italic", "color": COLORS["text_muted"], "textAlign": "center"},
    )
    if "topics" in DATA:
        td = DATA["topics"]
        topic_items = []
        if td.get("bigrams"):
            bdf = pd.DataFrame(td["bigrams"][:20])
            fig_bigrams = px.bar(
                bdf, x="count", y="bigram", orientation="h",
                title="Top 20 Bigramas",
                color_discrete_sequence=[COLORS["gold"]],
            )
            fig_bigrams.update_layout(
                template=PLOTLY_MANUSCRIPT_TEMPLATE,
                paper_bgcolor=COLORS["parchment_light"],
                plot_bgcolor=COLORS["parchment"],
                height=500,
                font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
                title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
                xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a", "categoryorder": "total ascending"},
            )
            for trace in fig_bigrams.data:
                trace.update(marker={"line": {"color": COLORS["burgundy"], "width": 1}})
            topic_items.append(card("Bigramas Mas Frecuentes", dcc.Graph(figure=fig_bigrams)))
        if td.get("topics"):
            tdf = pd.DataFrame(td["topics"])
            fig_topics = px.bar(
                tdf, x="topic_id", y="weight",
                title="Peso por Tema LDA",
                color="topic_id",
                color_continuous_scale=GOLD_BURGUNDY_SCALE,
            )
            fig_topics.update_layout(
                template=PLOTLY_MANUSCRIPT_TEMPLATE,
                paper_bgcolor=COLORS["parchment_light"],
                plot_bgcolor=COLORS["parchment"],
                height=350,
                font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
                title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
                xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                coloraxis_colorbar={"tickfont": {"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif"}},
            )
            topic_items.append(card("Temas LDA", dcc.Graph(figure=fig_topics)))

            words_data = []
            for t in td["topics"]:
                for w in t["words"][:5]:
                    words_data.append({"topic": f"Tema {t['topic_id']}", "word": w})
            if words_data:
                wdf = pd.DataFrame(words_data)
                fig_treemap = px.treemap(
                    wdf, path=["topic", "word"],
                    title="Palabras por Tema",
                    color="topic",
                    color_discrete_sequence=[COLORS["burgundy"], COLORS["gold"], COLORS["green"], COLORS["navy"]],
                )
                fig_treemap.update_layout(
                    template=PLOTLY_MANUSCRIPT_TEMPLATE,
                    paper_bgcolor=COLORS["parchment_light"],
                    plot_bgcolor=COLORS["parchment"],
                    height=450,
                    font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
                    title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
                )
                topic_items.append(card("Palabras Clave por Tema", dcc.Graph(figure=fig_treemap)))
        if td.get("document_topics"):
            doc_df = pd.DataFrame(td["document_topics"])
            pivot = doc_df.pivot_table(
                index="speaker", columns="topic", values="weight",
                aggfunc="mean", fill_value=0,
            )
            fig_heat = px.imshow(
                pivot,
                title="Distribucion de Temas por Presidente",
                labels={"color": "Peso"},
                aspect="auto",
                color_continuous_scale=[COLORS["cream"], COLORS["gold"], COLORS["burgundy"]],
            )
            fig_heat.update_layout(
                template=PLOTLY_MANUSCRIPT_TEMPLATE,
                paper_bgcolor=COLORS["parchment_light"],
                plot_bgcolor=COLORS["parchment"],
                height=500,
                font={"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif", "color": COLORS["text"]},
                title={"font": {"family": "Georgia, 'Palatino Linotype", "color": COLORS["burgundy"], "size": 16}, "x": 0.5},
                xaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                yaxis={"gridcolor": "#d4c9a8", "zerolinecolor": "#c5a55a"},
                coloraxis_colorbar={"tickfont": {"family": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif"}},
            )
            topic_items.append(card("Mapa de Calor: Temas por Presidente", dcc.Graph(figure=fig_heat)))
        if topic_items:
            topics_block = html.Div(topic_items)

    return html.Div([
        stats,
        chapter_header("I", "Linea de Tiempo"),
        card("Discursos a Traves de los Anos", [
            dcc.Graph(figure=fig_timeline),
            section_divider(),
            dcc.Graph(figure=fig_words),
        ]),
        chapter_header("II", "Entidades NER"),
        card("Entidades Nombradas", ner_block),
        chapter_header("III", "Sentimiento"),
        card("Analisis de Sentimiento", sent_block),
        chapter_header("IV", "Analisis Tematico"),
        card("Temas y Palabras Clave", topics_block),
    ])


app.layout = html.Div(
    style={
        "backgroundColor": COLORS["parchment"],
        "minHeight": "100vh",
        "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
        "color": COLORS["text"],
        "backgroundImage": PAPER_TEXTURE,
    },
    children=[
        html.Div(
            style={
                "background": f"linear-gradient(180deg, {COLORS['burgundy']} 0%, {COLORS['navy']} 100%)",
                "padding": "45px 20px 35px 20px",
                "textAlign": "center",
                "borderBottom": f"4px solid {COLORS['gold']}",
                "position": "relative",
            },
            children=[
                html.Div(
                    "❧  ✦  ❋  ✦  ❧",
                    style={
                        "color": COLORS["gold"],
                        "fontSize": "1rem",
                        "letterSpacing": "6px",
                        "marginBottom": "14px",
                    },
                ),
                html.H1(
                    "Discursos Presidenciales Chilenos",
                    style={
                        "fontFamily": "Georgia, 'Palatino Linotype', 'Book Antiqua', serif",
                        "fontSize": "2.4rem",
                        "fontWeight": "bold",
                        "color": COLORS["gold"],
                        "margin": "0",
                        "letterSpacing": "2px",
                    },
                ),
                html.Div(
                    "—  Analisis de Discurso y Plabra  —",
                    style={
                        "color": COLORS["gold_light"],
                        "marginTop": "8px",
                        "fontSize": "1.05rem",
                        "fontStyle": "italic",
                        "letterSpacing": "1px",
                    },
                ),
                html.Div(
                    "Cuentas Publicas · 1832–2000",
                    style={
                        "color": "#e0d5b8",
                        "marginTop": "10px",
                        "fontSize": "0.85rem",
                        "letterSpacing": "3px",
                        "textTransform": "uppercase",
                    },
                ),
                html.Div(
                    "❧  ✦  ❋  ✦  ❧",
                    style={
                        "color": COLORS["gold"],
                        "fontSize": "1rem",
                        "letterSpacing": "6px",
                        "marginTop": "14px",
                    },
                ),
            ],
        ),
        html.Div(
            style={
                "maxWidth": "1100px",
                "margin": "0 auto",
                "padding": "35px 25px 60px 25px",
            },
            children=[
                html.Div(
                    style={
                        "border": f"3px double {COLORS['gold']}",
                        "padding": "30px 25px",
                        "marginBottom": "40px",
                        "textAlign": "center",
                        "backgroundColor": COLORS["parchment_light"],
                        "backgroundImage": PAPER_TEXTURE,
                        "position": "relative",
                    },
                    children=[
                        html.Div(
                            "❧",
                            style={"position": "absolute", "top": "10px", "left": "14px", "color": COLORS["gold"], "fontSize": "1.1rem"},
                        ),
                        html.Div(
                            "❧",
                            style={"position": "absolute", "top": "10px", "right": "14px", "color": COLORS["gold"], "fontSize": "1.1rem", "transform": "scaleX(-1)"},
                        ),
                        html.Div(
                            "❧",
                            style={"position": "absolute", "bottom": "10px", "left": "14px", "color": COLORS["gold"], "fontSize": "1.1rem", "transform": "scaleY(-1)"},
                        ),
                        html.Div(
                            "❧",
                            style={"position": "absolute", "bottom": "10px", "right": "14px", "color": COLORS["gold"], "fontSize": "1.1rem", "transform": "scale(-1,-1)"},
                        ),
                        html.P(
                            "In Sapienza Veritas",
                            style={
                                "fontSize": "1rem",
                                "fontStyle": "italic",
                                "color": COLORS["burgundy"],
                                "letterSpacing": "3px",
                                "marginBottom": "6px",
                            },
                        ),
                        html.P(
                            "Este cuaderno contiene el analisis computacional del discurso politico chileno, extrayendo entidades, sentimiento y temas de las Cuentas Publicas presidenciales.",
                            style={
                                "fontSize": "0.9rem",
                                "color": COLORS["text_muted"],
                                "maxWidth": "700px",
                                "margin": "0 auto",
                                "lineHeight": "1.6",
                            },
                        ),
                    ],
                ),
                _build_layout(),
                html.Div(
                    style={
                        "textAlign": "center",
                        "marginTop": "50px",
                        "paddingTop": "25px",
                        "borderTop": f"2px solid {COLORS['gold']}",
                    },
                    children=[
                        html.Div(
                            "✦  ❋  ✦",
                            style={"color": COLORS["gold"], "fontSize": "0.9rem", "letterSpacing": "6px", "marginBottom": "10px"},
                        ),
                        html.P(
                            "El Fin del Cuaderno",
                            style={
                                "fontStyle": "italic",
                                "color": COLORS["text_muted"],
                                "fontSize": "0.9rem",
                                "letterSpacing": "2px",
                            },
                        ),
                        html.Div(
                            "❧",
                            style={"color": COLORS["gold"], "fontSize": "1.2rem", "marginTop": "8px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8051)))
