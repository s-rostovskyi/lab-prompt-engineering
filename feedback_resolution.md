# Feedback response and evidence map

The feedback was treated as review input and checked against the recorded experiment, not accepted as a new specification or evidence of model success.

| Review point | Decision and implementation | Evidence |
|---|---|---|
| Required extraction correction/injection fix | Add separately versioned v3r1 and v3r2 prompts, precise date branches, distinction between facts and commands, examples and independent tests | Both original problematic cases now pass 5/5 in v3r2; all 85 latest calls pass |
| New tests reveal further weakness | Preserve first-revision failure; add a second revision and distinguish regressions from new holdouts | v3r1 yearless correction 2/5; v3r2 regression 20/20 and new holdout 20/20 |
| Compact v1/v2/v3 comparison | Add a cross-task table without conflating manual and automatic evaluation | Main report and notebook |
| Explain step-by-step extraction | Explain fact selection, correction resolution and normalization, without claiming isolated CoT efficacy | Prompt documentation and notebook |
| Step 3 marked Not attempted | Preserve results; add an explicit evidence map rather than fabricate extra runs | Original baseline v1: three tasks, five runs each, 15 recorded responses |
| Step 9 marked Not attempted | Make the existing few-shot implementation and 15-run evidence easier to locate | SENTIMENT_V3 has three examples; advanced sentiment batch has 15 recorded calls |
| Portable evaluation example | Add an explicitly authored offline fixture demonstration, separate from model evidence | Notebook evaluator demonstration |
| Shorten working product prompt | Defer: changing a tested prompt for style alone would invalidate its exact tested identity and require new product experiments | Existing 15/15 manual result retained unchanged |
| Optional bonus challenges | No unrequested router, temperature study or automatic meta-prompt pipeline added | Core lab scope retained |

The reviewer praised automatic prompt improvement and a multi-task prompt, but the submitted implementation does not contain an automatic meta-prompt loop or a single router prompt. Separate task templates and assistant-authored revisions are not represented as completed bonus experiments. The reviewer also described a possible return to the earlier corrected date; the actual original output selected the corrected day and lost the explicit year. The analysis preserves this distinction.

Historical API logs, original scores and reviewed CSVs are unchanged. New success claims are based on actual newly recorded API responses, not prompt inspection or fabricated outputs.
