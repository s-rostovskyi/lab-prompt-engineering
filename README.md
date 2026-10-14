# Prompt Engineering Lab - TechFlow Solutions

This completed lab investigates sentiment classification, product descriptions and structured extraction through zero-shot, constrained, few-shot and step-by-step prompts. The main experiment session is `20261014T163343Z_9a1efd`.

## Start here

1. Open [the completed notebook](prompt_engineering_lab.ipynb) for all prompt versions and saved actual responses.
2. Read [the failure analysis](failure_analysis_report.md), [final prompt documentation](improved_prompts_documentation.md) and [single-paragraph reflection](lab_summary.md).
3. See [the product revision report](results/20261014T163343Z_9a1efd/product_revision_report.md) for the manually evaluated improvement.

Original model calls were executed by the Python runners. The notebook replays their recorded evidence offline: running it does not make new API calls or overwrite finalized reports. Final base-case checks passed 15/15 for sentiment v3, extraction v3 and product v3r1. Extraction corrected-date and embedded-instruction variations failed 0/5 each and remain explicitly documented limitations.

## File map

| File or folder | Purpose |
|---|---|
| `instructions.md`, `rubric.md` | Original course assignment and grading criteria; retained unchanged |
| `prompt_engineering_lab.ipynb` | Completed evidence notebook: all original versions, actual responses, metrics, analysis and product revision |
| `failure_analysis_report.md` | Baseline diagnosis, version comparisons, variations, limitations and original failure evidence |
| `improved_prompts_documentation.md` | Original v3 templates and evidence-based product v3r1 final selection |
| `lab_summary.md` | Required one-paragraph reflection at repository root |
| `prompts.py` | Original v1/v2/v3 prompts and synthetic reference cases |
| `run_lab.py` | Concurrent API runner and original report generator |
| `evaluation.py` | Original deterministic evaluator; its factual-screen limitations are documented |
| `product_prompt_revision.py`, `product_followup.py` | Revised product prompt, independent batches and combined experiment validator |
| `validate_lab.py` | Original validator; still rejects the historical product v3 manual result |
| `results/20261014T163343Z_9a1efd/` | Main session: API configuration, original/revised JSONL logs, reviewed CSVs and product revision report |
| Other timestamped `results/` directories | Earlier experiments retained for traceability; not pooled into reported final metrics |
| `results/metrics.json` | Original experiment automatic metrics, including the original product screen |
| `source_notes.md` | Course sources, methodological decisions and evidence provenance |
| `product_revision_instructions.md` | Revision rationale and reproduction instructions |
| `submission_checklist.md` | Deliverable coverage and final submission steps |
| `completion_checks.json`, `validation_status.json` | Supplemental validation/provenance records, not substitutes for actual journals |
| `requirements.txt`, `.gitignore` | Dependencies and exclusions for local credentials/cache files |

## Read or replay the completed notebook

Use Python 3.10 or later. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter notebook prompt_engineering_lab.ipynb
```

No API key is needed to replay recorded notebook evidence. Open the notebook with this folder as its working directory. Saved outputs are already included. The model used in the main journals is `gpt-4o-mini-2024-07-18`, requested through the `gpt-4o-mini` alias at temperature 0.7 with three workers and a 700-token output limit.

## Verify completed experiment records

```powershell
python product_followup.py --session 20261014T163343Z_9a1efd --validate
```

This checks completeness of the original experiment, original final sentiment/extraction thresholds, and the independent revised product batch against automatic checks and completed manual reviews. The reviewed final product result is 15/15. It does not verify extraction variation success or production readiness. The original `validate_lab.py` still checks historical product v3 and therefore correctly reports that historical manual failure.

## Reproduce new API experiments

Keep a local `.env` next to the notebook/scripts with `OPENAI_API_KEY=...`; it is ignored by Git. Existing values do not need to be replaced. API calls incur account charges. Use a fresh session and retain completed evidence. To reproduce the prepared original versions:

```powershell
python run_lab.py --stage all
```

The command prints a new session identifier. Original full execution is 283 logical calls, excluding retries. Analyze responses between stages when conducting a new evidence-driven iteration; `--stage all` only reproduces the existing prepared versions. The runner saves journals and regenerates root `failure_analysis_report.md`, `lab_summary.md` and `results/metrics.json`: use a separate working copy if you want to preserve the finalized submission narrative.

To reproduce the product revision in that new session, replace NEW_SESSION below with the printed identifier:

```powershell
python product_followup.py --session NEW_SESSION --stage advanced
python product_followup.py --session NEW_SESSION --stage variations
python product_followup.py --session NEW_SESSION --stage final
```

These add 45 logical API calls, excluding retries. Review their new CSV rather than copying previous assessments. The product follow-up writes separate revision files and preserves original responses and reviews.

## Submission workflow

This repository is a fork of [ai-consulting-bootcamp/lab-prompt-engineering](https://github.com/ai-consulting-bootcamp/lab-prompt-engineering). The course `instructions.md` requires a pull request back to that repository for AI review against `rubric.md`. Push the finished work, open that PR and address any blocking feedback. Also submit the fork URL in the portal deliverable field as required by the lab page. Keep the original `instructions.md` and `rubric.md`; their ungraded checkboxes are reviewer-owned templates, not statements that the work is missing.

HTML/PDF export is optional. Failed historical tests are retained as evidence. No API key or unrelated project materials should be committed.
