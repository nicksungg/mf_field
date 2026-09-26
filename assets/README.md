# README figures

`graphical_abstract.pdf` is the same Figure 1 used in the manuscript.
`graphical_abstract.png` renders that PDF without changing its layout or fields.
Only the figure is included here, not the manuscript.

The animated overview places this figure above three result charts. The chart
values come from `analysis/data/table2_ranking.json`. The illustrated ensemble
uses fitted mixture weights, as in the paper figure.

To regenerate the PNG, install Poppler and run from the repository root:

```bash
pdftoppm -scale-to 2400 -png -singlefile assets/graphical_abstract.pdf assets/graphical_abstract
```

To rebuild the GIF and the three static chart images:

```bash
python -m pip install -r requirements-visuals.txt
python scripts/build_readme_visuals.py
```

No model training or ensemble fitting is performed. Figure hashes and chart
values are recorded in `visuals_manifest.json`.
