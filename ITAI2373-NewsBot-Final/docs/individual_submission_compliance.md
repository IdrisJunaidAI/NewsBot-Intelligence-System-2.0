# Individual Capstone Compliance Matrix

**Basis:** ITAI 2373 Final Project, NewsBot Intelligence System 2.0, detailed instructor PDF (18 pages) plus Canvas overview due December 1, 2026.

**Individual submission approval reported by student on November 24, 2026:** The student confirms the professor is comfortable with individual completion and does not intend to create groups. The earlier group format in the assignment remains the published template, but this is now an instructor-approved individual pathway **as reported by the student**. Written instructor confirmation has not been independently inspected. The filename segment `Individual` transparently substitutes for `[GroupName]`; confirm the exact naming convention if the instructor expects a different label.

| Requirement | Evidence | Status and gap |
| --- | --- | --- |
| Enhanced GitHub repository (50 points) | Modular src, config, 8 notebooks, tests, README and CI | Verified public individual repository; authorized full-text BBC CSV intentionally excluded |
| Enhanced classification, confidence scoring | Real BBC Logistic Regression 95.83% accuracy; model comparisons | Measured internal holdout, uncalibrated probability |
| LDA and NMF topic modeling | Real BBC aggregate topic assignments plus teaching demonstration | Implemented; unverified temporal evolution because original CSV has no timestamps |
| Sentiment evolution | Historical BBC TextBlob polarity and demo VADER | Sentiment measured, but time evolution unavailable without verified dates |
| Entity relationships | spaCy NER and within article entity cooccurrence | Implemented; cooccurrence is not verified relationship |
| Summarization | Extractive sentence selection with source limitations | Implemented; no evaluated abstractive LLM output |
| Content enhancement and insight generation | Structured grounded template explanation | Implemented as a rule template, not LLM generation |
| Semantic search and embeddings | LSA hosted; multilingual MiniLM executed in Colab | Controlled six document benchmark, not full BBC retrieval |
| Query expansion | Simple category and intent parsing | Full semantic query expansion not established |
| Multilingual detection | English, Spanish and French | Tested on controlled examples |
| Translation integration | Consent protected third party provider | Implemented integration, actual provider quality not independently verified |
| Cross language coverage/cultural context | Colab cross language retrieval on synthetic passages | No authentic parallel multi publisher comparison; gap remains |
| Conversational interface | Flask intents, state, article IDs, filters | Operates on synthetic demo; BBC historical search not public |
| Technical documentation (15 points) | Individual detailed PDF, API, installation and configuration | Draft created; student final review required |
| User documentation (15 points) | User guide, notebooks, FAQ, live demo steps | Synthetic narrated rehearsal video prepared; no independently verified personal on-camera demonstration |
| Business docs (10 points) | Executive summary, ROI scenario, comparisons | Hypothetical ROI not realized |
| Presentation (35 points) | 20 slide individual deck with speaker notes | Individual presentation approved as reported by the student; rehearsal required |
| Reflective journal | Three page individual journal | Individual format approved as reported by the student; retain complete independent reflection |
| Web application bonus | Render Free Flask site, responsive dashboard and attributed BBC RSS | Implemented with batch analysis and interactive research chart; still an educational prototype; browser QA recommended |
| Research extension | 5,10,25,50,100 shots per category repeated study | 25 real BBC fit rows, notebook 09, summary API and chart; instructor determines bonus eligibility |

## Before submission

1. Individual submission has been approved according to the student's November 24 update. Confirm the GroupName filename placeholder only if the instructor specifies a different label.
2. Confirm repository is accessible to the instructor. Repository is public; check that the instructor can open the URL while signed out.
3. Reopen all PDFs and PPTX for your own accuracy review and confirm files render correctly.
4. Verify latest live BBC aggregate dashboard, synthetic toggle, multilingual lab and RSS behaviour from a browser.
5. Rehearse a 15 minute individual walkthrough with authentic BBC evaluation and Colab experiment.
6. Submit exactly one file set on Canvas and include repository and web links. Do not claim the 735 unlabeled test entries provide accuracy.
7. Include an accurate AI assistance declaration, attribution and appropriate publisher reuse rights.


## Bonus demonstration updates

**Frontend bonus:** `POST /api/batch/analyze` validates and analyzes two to five article excerpts in one request; the glass frontend provides a new batch form. **Research bonus:** `GET /api/research/fewshot` serves statistics computed from the committed 25-row authentic BBC sample-size study, and notebook 09 explains the methodology. See `docs/BONUS_EVIDENCE.md`. These are bonus eligibility demonstrations, not guaranteed marks.
