"""Utilities to create a German wordcloud using spaCy"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
try:
    from wordcloud import WordCloud
except Exception:  # pragma: no cover - optional dependency
    WordCloud = None
import spacy

BASE = Path(__file__).resolve().parents[1]
OUTDIR = BASE / "results"
OUTDIR.mkdir(parents=True, exist_ok=True)


def _load_model():
    """Load the German spaCy model, downloading on demand."""
    try:
        return spacy.load("de_core_news_sm")
    except OSError:
        from spacy.cli import download

        download("de_core_news_sm")
        return spacy.load("de_core_news_sm")


def generate_spacy_wordcloud(text: str, *, out_prefix: str = "spacy_wordcloud") -> tuple[Path, Path]:
    """Generate a wordcloud based on spaCy lemma tokens.

    Parameters
    ----------
    text:
        Input text for analysis.
    out_prefix:
        Base filename (without extension) for generated files in ``results``.

    Returns
    -------
    tuple(Path, Path)
        Paths to the generated PNG and SVG files.
    """
    nlp = _load_model()
    doc = nlp(text)
    tokens = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
    processed = " ".join(tokens)
    if WordCloud is None:
        raise RuntimeError("wordcloud package not installed")
    wc = WordCloud(width=1280, height=800, max_words=100, background_color="white").generate(processed)
    png_path = OUTDIR / f"{out_prefix}.png"
    svg_path = OUTDIR / f"{out_prefix}.svg"
    try:
        svg = wc.to_svg()
        svg_path.write_text(svg, encoding="utf-8")
    except Exception:
        pass
    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(png_path, bbox_inches="tight")
    plt.close()
    return png_path, svg_path


if __name__ == "__main__":  # pragma: no cover
    sample = (
        "Das ist ein kurzer Beispieltext für die Erstellung einer Wortwolke. "
        "Die Wortwolke zeigt die wichtigsten Lemmata." 
    )
    generate_spacy_wordcloud(sample)
    print(f"Wortwolke erstellt im Ordner: {OUTDIR}")
