# Financial Fraud Detection Using Graph Machine Learning — MCA Project Report

Project report submitted to the APJ Abdul Kalam Technological University in
partial fulfilment of the award of the degree of **Master of Computer
Applications**.

- **Student:** Aarjav Oravakandi (TVE25MCA-2002)
- **Department:** Department of Computer Applications, College of Engineering Trivandrum
- **Supervisor:** Dr. Haripriya A P, Head of the Department
- **Submission:** November 2026

The report describes a fraud detection system that models a transaction
history as a directed, weighted account graph and layers a six-rule engine,
NetworkX graph analytics, Random Forest / XGBoost / Isolation Forest, GCN and
GraphSAGE, fraud-ring assembly and an analyst investigation workflow over it.

## Files

| Path | Contents |
|---|---|
| `Financial_Fraud_Detection_GraphML_Project_Report_TVE25MCA-2002 - FINAL.pdf` | **The submission copy** (78 pages) — see below |
| `report/patches/` | Sources of the targeted corrections applied to the submission copy |
| `report/main.tex`, `report/preamble.tex` | Full LaTeX edition (79 pages; document order / shared preamble) |
| `report/frontmatter/` | Title page, declaration, certificate, acknowledgment, abstract |
| `report/chapters/` | Chapters 1–8, one file each |
| `report/bibliography.tex` | The 18 numbered references |
| `report/figures/diagrams/` | TikZ sources of Figures 4.1–4.5 (architecture, use case, DFDs, pipeline) |
| `report/figures/images/` | Screenshots, the ER diagram and the Chapter 7 result charts |
| `verification/` | Scripts, outputs and environment of the final verification re-run (Section 7.2.7) |
| `CHANGELOG.md` | Summary of the final revision |

## Which PDF is which

The **submission copy** is the 78-page report chosen by the author. It is not
compiled from `report/main.tex`: the latest corrections (Figures 4.1 and 4.2,
the Figure 4.10 caption and its List of Figures entry, Sections 4.3, 4.7.1,
7.2.6 and 7.2.7) were typeset as fragments in `report/patches/patches.tex`,
with the same preamble, and placed over the corresponding regions of that PDF
by `report/patches/apply_patches.py`. Every other page is unchanged. To
regenerate it, run from `report/`:

```bash
latexmk -xelatex -outdir=patches patches/patches.tex
git show "5649fd6:Financial_Fraud_Detection_GraphML_Project_Report_TVE25MCA-2002 - FINAL.pdf" > base.pdf
git show "5df4e8a:Financial_Fraud_Detection_GraphML_Project_Report_TVE25MCA-2002 - FINAL.pdf" > outline.pdf
python3 patches/apply_patches.py base.pdf patches/patches.pdf FINAL-new.pdf outline.pdf
```

(PyMuPDF ≥ 1.24. `base.pdf` is the submission copy before these corrections;
`outline.pdf`, the originally uploaded report, supplies the bookmarks — it has
the same pagination.)

`report/main.tex` builds a fuller 79-page edition that also carries the
corrections described in `CHANGELOG.md` under "Final revision" (Isolation
Forest provenance, reproducibility evidence table, faithful code listings).

## Building the full LaTeX edition

Requires TeX Live 2023 or later with XeLaTeX and `latexmk`, and the
Liberation fonts (`fonts-liberation` on Debian/Ubuntu). Packages used:
`fontspec`, `unicode-math`, `titlesec`, `fancyhdr`, `listings`, `tikz`,
`booktabs`, `tabularx`, `longtable`, `caption`, `subcaption`, `enumitem`,
`needspace`, `xurl`, `hyperref`, `microtype`.

```bash
cd report
latexmk          # uses latexmkrc -> XeLaTeX; writes report/main.pdf
cp main.pdf "../Financial_Fraud_Detection_GraphML_Project_Report_TVE25MCA-2002 - FINAL.pdf"
latexmk -c       # remove auxiliary files
```

## Relationship to the application

The application itself lives in
<https://github.com/Aarjav-333/fraud-detection-graphml>. Every code listing,
rule threshold, role permission and result in the report was checked against
that repository at commit `3800cc1`; Section 7.2.7 of the report and
`verification/README.md` state which results were reproduced from it and which
rest on stored result files.
