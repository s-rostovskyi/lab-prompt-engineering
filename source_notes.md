# Source materials

All four attachments from the referenced conversation were reviewed. Originals were left unchanged. The submission package contains authored lab materials rather than copied portal pages containing personal information.

1. **LAB - Prompt Engineering Lab.mhtml**: TechFlow scenario, three tasks, provided baseline messages/product, steps 1–13, independent 5/10/15-run tests, three versions, few-shot, CoT, final 15-run evaluation, variations, four mandatory deliverables and GitHub submission rules. HTML/PDF export and bonus challenges are optional. An automatic evaluator is included as an additional tool.
2. **m2_02_advanced-prompt-techniques.ipynb**: all 60 cells, OpenAI client, gpt-4o-mini, temperature, few-shot/CoT examples, repeated calls, token optimization, LLM judge and bias. Original outputs are empty and cannot serve as experiment results. Its one-shot string is not assigned to prompt; this defect was not copied. Our implementation records API errors separately from model responses.
3. **Prompt Engineering Fundamentals(1).mhtml**: prompting techniques, knowledge/format/token limitations, empirical iteration, bias and version control. Course heuristics are hypotheses rather than guarantees. Temperature zero and seed are not treated as proof of reproducibility.
4. **prompt_eng_deck.pptx**: nine slides on recency, sycophancy, verbosity, list-making, hedging, positivity, authority, anchoring and format rigidity. The lab applies explicit formats, length limits, evidence-based outputs and mixed/negative feedback tests. Neither a positive label nor improved metrics is assumed.

## Methodological decisions

- Baseline uses the messages and product supplied in the assignment. Variation cases are authored for educational testing, not represented as real customer data.
- An extraction date without a year remains March 15; no calendar year is invented.
- CoT is implemented as an internal step-by-step checking instruction with final JSON only. Hidden reasoning quality is not directly measured.
- v2/v3 were authored before actual calls were available. Confirm or revise them after inspecting measured baseline failures; this limitation is stated in the report and summary.
- Product checks evaluate structure, length and selected unsupported claims. They do not establish persuasiveness or rule out every hallucination; human review is required.
- Chat Completions follows the course implementation. The official [OpenAI API reference](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create) was checked on October 14, 2026. The completed journals now contain 328 recorded successful API responses using gpt-4o-mini-2024-07-18; finalization verified their prompt hashes and experiment checks. No new API calls were made during finalization. Account access is evidenced by those stored responses, not by a new connection test.

## Completed experiment evidence

The original notebook source had no saved outputs. The final notebook was populated by executing an offline replay of the recorded JSONL evidence. All original failed batches and the independent product revision are retained. Original prompts were hypotheses when authored; the completed reports now evaluate their actual measured results. Extraction date-normalization and embedded-instruction failures remain unresolved.
