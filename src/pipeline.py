"""
HR Chat Analytics – Minimal Pipeline (zws1–zws4)
"""
import os, re, string
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except Exception:
    WORDCLOUD_AVAILABLE = False

BASE = Path(__file__).resolve().parents[1]
DATADIR = BASE / "data"
OUTDIR = BASE / "results"
OUTDIR.mkdir(parents=True, exist_ok=True)

def try_read_csv(path: Path):
    encodings = ["utf-16", "utf-8", "latin-1"]
    delims = [";", ","]
    last = None
    for enc in encodings:
        for d in delims:
            try:
                df = pd.read_csv(path, encoding=enc, delimiter=d)
                if df.shape[1] >= 1:
                    return df
            except Exception as e:
                last = e
    raise last or RuntimeError(f"Konnte {path} nicht lesen.")

def find_conversations_file() -> Path:
    # prioritize conversations_example.csv for demo
    demo = DATADIR / "conversations_example.csv"
    if demo.exists():
        return demo
    cands = sorted([p for p in DATADIR.glob("conversations*.csv")])
    if not cands:
        raise FileNotFoundError("Lege eine Datei 'conversations_example.csv' oder 'conversations_final.csv' in data/ ab.")
    for p in cands:
        if p.name.lower() == "conversations_final.csv":
            return p
    return cands[0]

def split_transcript(s):
    if pd.isna(s):
        return None
    return str(s).split("||")

def remove_tobi(seq):
    if not isinstance(seq, list):
        return None
    keep = [x for x in seq if not str(x).startswith("TOBi")]
    return keep if len(keep) > 1 else None

def get_second(seq):
    try:
        return seq[1]
    except Exception:
        return None

def clean_anon(s: str) -> str:
    s = re.sub(r"(?i)Firstname\sLastname|Firstname|Lastname", " ", s)
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"(?i)\+*XX\s\(*X\)*\sXXX\sXXX\sXXXX", " ", s)
    s = re.sub(r"(?i)xx+", " ", s)
    s = re.sub(r"(?i)\sx\s", " ", s)
    return s

def make_bar(labels, values, title, outpath):
    plt.figure()
    plt.title(title)
    plt.plot(labels, values, "o-")
    plt.bar(labels, values, width=0.4)
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()

def make_wc(text, title, outpath):
    # optional PNG wordcloud (font availability may vary)
    if not WORDCLOUD_AVAILABLE:
        return
    try:
        wc = WordCloud(width=1280, height=800, max_words=100, background_color="white").generate(text)
        plt.figure()
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(title)
        plt.savefig(outpath, bbox_inches="tight")
        plt.close()
    except Exception as e:
        print(f"[Info] Wordcloud übersprungen: {e}")

def main():
    conv = find_conversations_file()
    df = try_read_csv(conv).copy()

    # detect transcript col
    transcript_col = None
    for cand in ["Transcript", "Transkript", "transcript", "transkript"]:
        if cand in df.columns:
            transcript_col = cand
            break
    if transcript_col is None:
        textiness = df.apply(lambda s: s.astype(str).str.len().median() if s.dtype == object else 0)
        transcript_col = textiness.sort_values(ascending=False).index[0]

    df["transcript_splitted"] = df[transcript_col].apply(split_transcript).apply(remove_tobi)
    df = df.dropna(subset=["transcript_splitted"]).reset_index(drop=True)

    text_all = "".join([str(parts) for parts in df["transcript_splitted"]])
    zws1 = len(text_all)
    make_wc(text_all, "Wordcloud Zwischenstand 1", OUTDIR / "Wordcloud_zwischenstand1.png")

    df["user_transcript"] = df["transcript_splitted"].apply(get_second)
    df = df.dropna(subset=["user_transcript"]).reset_index(drop=True)
    text_user = " ".join(df["user_transcript"].astype(str))
    zws2 = len(text_user)
    make_wc(text_user, "Wordcloud Zwischenstand 2", OUTDIR / "Wordcloud_zwischenstand2.png")
    make_bar(["zws1","zws2"], [zws1,zws2], "Zwischenstand zws1–zws2", OUTDIR / "Barplot_zws1-2.png")

    df["user_transcript"] = df["user_transcript"].astype(str).apply(clean_anon)
    text_user3 = " ".join(df["user_transcript"])
    zws3 = len(text_user3)
    make_wc(text_user3, "Wordcloud Zwischenstand 3", OUTDIR / "Wordcloud_zwischenstand3.png")
    make_bar(["zws1","zws2","zws3"], [zws1,zws2,zws3], "Zwischenstand zws1–zws3", OUTDIR / "Barplot_zws1-3.png")

    df["user_transcript"] = df["user_transcript"].str.lower()
    exclist = "".join([c for c in (string.punctuation + string.digits)])
    trans = str.maketrans("", "", exclist)
    df["user_transcript"] = df["user_transcript"].apply(lambda s: s.translate(trans))

    text_user4 = " ".join(df["user_transcript"])
    zws4 = len(text_user4)
    make_wc(text_user4, "Wordcloud Zwischenstand 4", OUTDIR / "Wordcloud_zwischenstand4.png")
    make_bar(["zws1","zws2","zws3","zws4"], [zws1,zws2,zws3,zws4], "Zwischenstand zws1–zws4", OUTDIR / "Barplot_zws1-4.png")

    # Save cleaned data (step 4)
    (OUTDIR / "data_after_step4_no_spacy.csv").write_text(df.to_csv(index=False), encoding="utf-8")
    print("Fertig. Ergebnisse in:", str(OUTDIR))

if __name__ == "__main__":
    main()
