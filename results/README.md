# Ergebnisse

Die hier abgelegten Grafiken entstehen durch Ausführen der Pipeline
```bash
python src/pipeline.py
```
Voraussetzung ist eine passende `conversations_*.csv` im Verzeichnis
`data/`. Der Lauf erzeugt sämtliche unten beschriebenen Abbildungen.

## Grafiken und Erkenntnisse

- **Barplot_zws1-2.png** – Vergleich der Textmenge vor und nach dem
  Entfernen der Bot‑Passagen. Die Menge an Zeichen verringert sich
  deutlich.
- **Barplot_zws1-3.png** – Ergänzt den Anonymisierungsschritt; erneut
  nimmt die Textlänge durch das Entfernen personenbezogener Angaben ab.
- **Barplot_zws1-4.png** – Letzter Bereinigungsschritt (Kleinschreibung,
  Entfernen von Satzzeichen/Ziffern). Es bleibt nur der tatsächlich
  analysierbare Nutzertest.

- **Wordcloud_zwischenstand1.svg** – Wordcloud aller Chatpassagen. Viele
  Funktionswörter und Agenten‑Namen dominieren, was weiteren
  Bereinigungsbedarf zeigt.
- **Wordcloud_zwischenstand2.svg** – Wordcloud der zweiten
  Nutzer‑Nachricht nach Entfernen der Bot‑Zeilen. Die Wörter spiegeln
  bereits konkrete Anliegen wider, enthalten aber noch Zeitstempel und
  Namen.
- **Wordcloud_zwischenstand3.svg** – Nach der Anonymisierung bleiben
  vor allem Begriffe wie „agent“ oder „self-service-portal“ übrig, ohne
  personenbezogene Daten.
- **Wordcloud_zwischenstand4.svg** – Endgültige Wordcloud nach
  Kleinschreibung und Entfernen von Zeichen. Sie zeigt klar die
  entscheidenden Schlüsselwörter, etwa „agent“, „über“ und „zeitraum“.

- **topwords_simple.png** – Balkendiagramm der häufigsten Wörter im
  bereinigten Datensatz. „agent“, „über“ und „das“ treten am häufigsten
  auf und verdeutlichen typische Gesprächsbausteine.

