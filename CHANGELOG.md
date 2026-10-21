# Changelog

## Diagram and wording corrections — 21 October 2026

Applied to the 78-page submission copy on `main` (with the HOD, Principal and
Dr. Liji P I acknowledgment changes already in it). Only the regions below
changed; the other 70 pages are textually identical.

- **Figure 4.2 (p. 22), use case diagram — redrawn.** *Confirm fraud* and
  *Clear account* are separate use cases. `«include»` runs only from *Confirm
  fraud* to *Notify account holder by email*, because `fraud_review.py` queues
  the email (via `mailer.queue_fraud_confirmation`) only when an account becomes
  Confirmed Fraud. A note records that delivery depends on a usable address and
  that clearing sends nothing. The Account Holder is a secondary actor only. The
  Viewer role (`ROLES` in `scripts/create_user.py`) is shown, with the Fraud
  Analyst / Administrator as its specialisation; the shaded use cases are those
  guarded by `require_fraud_analyst`.
- **Section 4.3 (p. 21)** rewritten to explain the diagram as implemented.
- **Section 4.7.1 (p. 29):** "guards exactly three capabilities" replaced by
  the routes it actually guards — the investigation routes (record, review
  status, holder-email retry), notifications and model analytics.
- **Figure 4.1 (p. 18), architecture.** The detection layer shows the
  operational path Rule Engine → Graph Analysis → Feature Engineering → ML
  Scoring, with GNN training and evaluation as a dashed, optional branch that
  alert generation does not use (matching Figure 4.5, `app/api/gnn.py` and
  `app/ml/alerts.py`).
- **Figure 4.10 (p. 33) caption and its List of Figures entry:** now describe a
  static screenshot. Arrowheads show direction; the moving dots
  (`linkDirectionalParticles` in `MoneyFlowGraph.jsx`) exist only in the
  running application. The feeder / mule / collector / shell / cash-out
  description is kept.
- **Section 7.2.7 (p. 59) opening:** no longer claims that everything is
  reproducible; it points to the stored result files of Table 7.6 and states
  that the 22-second runtime is an informal observation. The rest of the page
  moves down one line.
- **Section 7.2.6 (p. 58):** "the one result in this chapter that cannot be
  independently reproduced" replaced by a statement that the runtime, unlike the
  results recorded in Table 7.6, has no stored record.
- **Bookmarks repaired.** The PDF outline on `main` resolved to page −1 after
  the earlier page swaps; it now has explicit page numbers again (88 entries,
  identical to the original upload).

Not changed, by request: the Isolation Forest description and Table 7.5's
evaluated-commit row.

## Name update — 21 October 2026

- Head of the Department (and project supervisor, as the report already
  described the HOD) changed from Dr. Liji P I to **Dr. Haripriya A P** in the
  declaration, the acknowledgment and the README.
- Principal changed from Dr. Suresh K to **Dr. Joseph Zacharias** in the
  acknowledgment.
- The acknowledgment sentence for the Head of the Department no longer uses a
  pronoun.

## Final revision — 21 October 2026

Baseline: the 78-page `… - FINAL.pdf` uploaded on 21 October 2026 (commit
`5df4e8a`). No LaTeX sources were in the repository, so the report was rebuilt
as an editable XeLaTeX project from that PDF — same text, typeface (Liberation
Serif / Mono), A4 margins, heading styles, header and footer rules, tables,
listings, figures and bibliography. The result is 79 pages. The submission date
(November 2026) and all student, supervisor and institution details are
unchanged.

### Technical corrections, verified against `fraud-detection-graphml` at `3800cc1`

- **Evaluated commit and Isolation Forest.** The report claimed the Isolation
  Forest contamination had been corrected to `y_train.mean()`. No commit of the
  application repository, including `3800cc1`, contains that change — every
  commit uses `y.mean()`. Listing 5.3 now shows the committed code; Section 7.1.2
  and Table 7.2 state the actual setting; Table 7.5 now separates the commit
  verified (`3800cc1`), the original evaluation run (commit not recorded; at or
  after `892ea22` / `9f0f5e9`), and the uncommitted training-only estimate. The
  two settings were compared in this revision and give identical predictions, so
  no metric changed.
- **Use-case diagram (Figure 4.2).** Redrawn: Confirm fraud and Clear account are
  separate use cases; «include» runs only from Confirm fraud to Notify account
  holder by email, with a note that delivery depends on a usable address and that
  clearing sends nothing; the Account Holder is a secondary actor only.
- **Viewer role.** Added as an actor, with the Fraud Analyst / Administrator as
  its specialisation. Section 4.3, Section 4.7.1 and Section 3.4.2 now match
  `app/deps.py`: `require_fraud_analyst` guards the whole investigation router
  (investigation record, review, email retry), the notification endpoints and the
  GNN evaluation — not "exactly three capabilities".
- **Reproducibility.** The claim that everything in Chapter 7 could be reproduced
  from the repository was replaced by Table 7.6, which classifies each result as
  reproduced exactly, reproduced approximately, supported by stored artefacts
  only, a working-database snapshot, or an informal observation. Table 7.7 now
  says the result files are gitignored.
- **Runtime.** The 22-second figure is labelled as a single informal
  observation; the verification timings (16.9 s and 18.7 s, different hardware)
  are reported separately and not presented as a benchmark.
- **Figure 4.10 caption.** Now describes a static screenshot: arrowheads show
  direction; the moving dots exist only in the running application.
- **Further discrepancies found and fixed:** real-time alerts fire when a
  confirmed account *sends* a transaction (not "takes part in"); R6 times each
  hop against the previous one (a loop may span 96 h), not "cycle completed
  within 48 hours"; ring roles follow money flow, not "degree ordering"
  (Section 6.1.3, Limitation 10); the client has eighteen pages, not fourteen;
  Listing 4.1/4.2 comments use the real `account_type` values and the
  `TXN0000001` format; Listings 5.1–5.4 are now faithful excerpts with omissions
  marked (the fraud-ring part of Listing 5.2 and Listing 5.3 were paraphrased);
  the alert listing notes its 0.70 threshold versus the 0.80 default.

### Verification performed

- Pipeline re-run from the committed seed data at `3800cc1` under two library
  sets. Exact matches: rule engine (2,565 / 2,562 / 3 / 101), Random Forest
  (scikit-learn 1.5.2), Isolation Forest, all fraud-ring figures, split sizes,
  GNN split identifier. XGBoost: F1 0.831 versus 0.825 stored — disclosed in
  Section 7.2.2; stored metrics left unchanged.
- Test suite: 57 passed, 2 skipped, matching Table 6.4 file by file.
- GNN models were not re-run (PyTorch could not be installed in the container).
- Evidence: `verification/`.

### Additions

- Limitation 11 (artefacts and environment not archived) and a matching
  future-work sentence in Chapter 8.
- `README.md`, `CHANGELOG.md`, `.gitignore`, `report/latexmkrc`, `verification/`.
