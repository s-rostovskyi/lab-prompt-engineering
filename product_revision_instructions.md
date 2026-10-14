# Product revision after manual review

The original final v3 product batch failed the supplied-facts rubric. The reviewed CSV contains 14 unsupported-claim failures and one response with 29 words. The original automatic screen did not detect every unsupported claim. These are actual observations from the supplied CSV, not invented model runs.

The revision `v3r1` uses explicit exclusions and new few-shot examples that avoid promises about design, reliability, comfort or performance. Neutral purchase guidance supplies the required word count without inventing product facts. This limits persuasive richness because only a name and price are available. Its measured performance is not yet known.

## Install this update

Copy only `product_prompt_revision.py`, `product_followup.py`, and this instruction file to the same repository folder as `run_lab.py`. Keep your current notebook, original scripts, `.env`, `results` folder and reviewed `manual_review.csv`. Do not replace your completed work with the original unexecuted package.

## New experiments

Use the same session/model/temperature as the original experiment. Only product calls are repeated: 15 advanced, 15 variations (three cases times five) and 15 independent final calls. The update adds 45 API calls, plus any transient-error retries.

```powershell
python product_followup.py --session 20261014T163343Z_9a1efd --stage advanced
python product_followup.py --session 20261014T163343Z_9a1efd --stage variations
python product_followup.py --session 20261014T163343Z_9a1efd --stage final
```

Read the output and failures after each stage. Inspect `product_revision_report.md` and `product_revision_responses.jsonl` in the existing session folder. If further prompt edits are necessary, retain this revision and use a new revision identifier rather than combining different prompts into one batch.

The original `manual_review.csv` is preserved. New assessments go in `product_revision_manual_review.csv`. For each `revision_final` response, set `factual_pass` and `style_pass` to yes/no and add English notes. An assistant can review the exported file, but the CSV must identify assessments rather than fabricated responses. Use the same factual rubric for the original and revised batches.

```powershell
python product_followup.py --session 20261014T163343Z_9a1efd --validate
```

The updated validator requires at least 13/15 revised final responses to pass both automatic and manual checks. It also checks completeness of the original experiment and the original final sentiment/extraction thresholds. The original validator still evaluates the original v3 product batch and will continue to fail for that historical batch. This is expected and should remain documented.

## Notebook and narrative

Append a section titled `Product revision after manual review` to your executed notebook. State the observed failure, the revised prompt and why the original screen missed claims. Display the new actual outputs and revision report, retaining all original cells and results. You can run the commands above in notebook code cells with `!python` instead of `python`, or load the saved JSONL afterward.

Update `improved_prompts_documentation.md` with the revised prompt from `product_prompt_revision.py`. In `failure_analysis_report.md`, retain the original v3 results and add a clearly labeled v3r1 comparison based on the same manual rubric. Update the single paragraph in `lab_summary.md` after the new results are available. Avoid calling the original report generator after manual narrative edits because it regenerates the original report and summary.

Do not claim this revision meets the threshold until actual API results and factual/style assessments confirm it. Upload both the original and revision evidence to the existing GitHub repository.
