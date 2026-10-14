# Submission checklist

The experiment journals contain 283 original responses and 45 product revision responses. Original prompt hashes match the saved requests. The finalization notebook replays these actual records offline without making new API calls.

| Requirement | Evidence | Status |
|---|---|---|
| Named notebook with code and actual results | prompt_engineering_lab.ipynb and accompanying Python implementations | Prepared with saved offline replay outputs |
| v1/v2/v3 for all three tasks | prompts.py and notebook prompt sections | Included |
| Independent 5/10/15 baseline tests | raw_responses.jsonl, notebook and failure report | Complete |
| Failure patterns and all-version metrics | failure_analysis_report.md | Complete; original failed responses retained |
| Few-shot sentiment and products; CoT extraction | Original templates plus product revision | Implemented and tested; effects not isolated |
| Task variations | Original and revision journals | Complete; two extraction variations failed and are documented |
| Final independent 15-run tests | Original sentiment/extraction v3 and revised product v3r1 | Base-case criteria passed |
| Improved prompts documentation | improved_prompts_documentation.md | Updated with tested v3r1 and limitations |
| One-paragraph root reflection | lab_summary.md | Completed from actual evidence |
| Product manual factual/style assessment | Both reviewed CSV files | Complete; original 1/15 and revised 15/15 combined passes |
| README and repository file map | README.md | Updated README supplied in the readiness patch |
| GitHub-only submission | https://github.com/s-rostovskyi/lab-prompt-engineering | Remote HEAD matched clean local commit 7c7cd3e8b874e25afdcb87e621eea9418915f3c1; course PR still needed |

Before submitting, open the completed notebook to confirm its saved outputs are visible, retain all experiment journals and reviewed CSV files, ensure .env and cache directories are excluded, and commit the lab materials to the stated repository. Submit its URL. Optional HTML export can help reviewers but is not required. The experiment checker has passed; it does not establish extraction variation success or production readiness.

## Course pull request

The fork relationship to ai-consulting-bootcamp/lab-prompt-engineering is confirmed. No course pull request from s-rostovskyi:main was found during the audit. Create it after pushing the readiness documentation update; respond to reviewer feedback. Submit the fork URL in the portal as required.
