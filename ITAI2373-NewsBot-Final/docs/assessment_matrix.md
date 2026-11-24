# Professor rubric traceability | Individual NewsBot 2.0

**Published grading:** 200 core points, divided into Repository (50), Advanced Analysis (75), Comprehensive Documentation (40) and Presentation (35). The instructor also lists a second qualitative review of Technical Excellence (100), Documentation (50) and Presentation (50); **these are alternative groupings of the same 200 points, not additional points**.

**Extra credit available:** Up to 30 points for the optional Flask web frontend and up to 20 points for advanced research. Neither is guaranteed. See [fully evidenced bonus report](BONUS_EVIDENCE.md) and [individual compliance status](individual_submission_compliance.md).

| Criterion | Current evidence | Remaining limitations / evaluation risk |
| --- | --- | --- |
| Repository 50 | Public individual GitHub repository with modular src, version bounded requirements, settings/key template, 9 notebooks (7 prescribed + 2 additional), tests, processing/model/result directories, docs, reports, meaningful commit history, GitHub Actions | Raw BBC CSV intentionally excluded for content rights; instructor needs student to supply authorized local dataset for exact reproduction |
| Topic discovery 20 of Advanced 75 | LDA and NMF on authentic BBC aggregate and separate demo text, selectable interactive topic chart | No BBC publication timestamps, so topic evolution cannot be claimed |
| Language models 20 of Advanced 75 | Extractive summarizer, grounded insight template, TF IDF and LSA retrieval; real MiniLM in the executed Colab experiment | No validated hosted BBC semantic full text search; query expansion limited |
| Multilingual 20 of Advanced 75 | English/Spanish/French detection, optional consent-gated translation, curated offline word mapping, executed MiniLM benchmark | Translation quality and real cross-publisher cultural context not validated |
| Conversation 15 of Advanced 75 | Intent handling, category and sentiment filters, multistep session context, source IDs, summaries | Stored article content is the **60 synthetic examples**, not the BBC historical articles |
| Technical documents 15 of Documentation 40 | Refined 17 page technical PDF, source API/installation/configuration docs, diagram and data provenance | Student should confirm version applicability and personal attestation |
| User docs 15 of Documentation 40 | User guide, FAQ, notebooks, live demo runbook, practice MP4 with synthetic voice clearly marked | A **personal on-camera tutorial** has not been verified; practice MP4 is not student appearance evidence |
| Business docs 10 of Documentation 40 | Individual 3 page executive summary, hypothetical ROI, use cases, competitive comparison | ROI is illustrative and has not been realized commercially |
| Presentation 35 | Individual 20 slide PowerPoint with notes and live website/demo plan; student reports instructor accepts solo format | Personal delivery and Q&A must be completed by student |
| **Bonus web frontend, up to 30** | Render Free Flask site, authentic BBC evidence dashboard, attributed official RSS links, article analysis, new 2–5 article batch analysis, natural language query UI, multilingual lab, interactive visualizations and responsive glass UI | Manual browser acceptance and accessibility/security audit remain prudent |
| **Bonus advanced research, up to 20** | 25 measured BBC low-data supervised classifier fits: 5 training sizes × 5 seeds, a fixed 288 example holdout, mean/stdev plot, CSV, original evaluation script, notebook 09 and `GET /api/research/fewshot` | This is a **low-data supervised learning curve**, not LLM few-shot prompting or unseen-category adaptation; instructor determines eligibility |

## Individual scope

The student reported that the professor accepts an individual submission and does not intend to create a team. Existing group instructions and contribution marks should therefore be discussed as individually integrated work, not fictitious coordination. The source files and research statement disclose AI help and external MIT Uiverse contributors.

## Core limitations deliberately not concealed

* BBC training documents have no publication date: genuine time evolution remains not measurable.
* Original BBC article bodies are not republished on GitHub or Render.
* The historical BBC classification percentages are **holdout** evidence only, not live news accuracy guarantees.
* Multilingual MiniLM's reported perfect controlled retrieval is based on **six synthetic items and 18 intentionally constructed queries**, not independent cross-cultural news validation.
* A separate synthetic source powers the conversational search.
* Model probabilities are uncalibrated. No fact-checking or untested human bias classifications are claimed.
