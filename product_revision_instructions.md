# Product revision v3r1: completed experiment

The original final product batch passed 14/15 automatic checks but only 1/15 combined factual/style review. Unsupported claims such as appearance, comfort, reliability and connection quality escaped the original screen. One response contained 29 words.

The revision added explicit exclusions, neutral few-shot examples and a final fact/word-count instruction. All 45 revised responses passed the recorded automatic checks and assistant factual/style review, including an independent final batch of 15/15. Final descriptions contain 32-36 words. Claims about superior marketing persuasiveness are not supported; the copy remains generic and repetitive.

## Evidence

See `results/20261014T163343Z_9a1efd/product_revision_responses.jsonl`, `product_revision_manual_review.csv` and `product_revision_report.md`. Original v3 evidence remains in `raw_responses.jsonl` and `manual_review.csv`. The notebook includes both histories and completed analysis.

## Validation

```powershell
python product_followup.py --session 20261014T163343Z_9a1efd --validate
```

This verifies original experiment completeness, the original sentiment/extraction final base cases and revised product combined automatic/manual checks. The original validator still rejects the original product manual result; that is expected historical evidence rather than a reason to edit old scores.

## Reproduction

Use the API reproduction procedure in README.md with a fresh completed original session. Run revised advanced, variations and final stages in order; they add 45 logical API calls. Inspect and assess the new actual responses independently. Do not rerun a completed revision batch or pool duplicate attempts. Keep model and API settings fixed.

The reviewed improvement concerns the supplied-facts/style contract. Original and revised automatic screens differ; compare factual accuracy using the same manual rubric. Extraction variation failures remain unresolved and are documented separately. No additional model calls are needed for the current submission.
