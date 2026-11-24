# NewsBot Intelligence System 2.0
## Individual submission package

**Student:** Idris O. Junaid  
**Course:** ITAI 2373 Natural Language Processing  
**Canvas due date:** December 1, 2026 by 11:59 PM Central Time  
**Professor's individual format:** Accepted according to the student's November 24, 2026 communication. The original PDF instructions still describe groups; the files transparently use `Individual` as the corresponding filename segment.

### Upload these exact four files

1. `FP_TechnicalDoc_IdrisJunaid_Individual_ITAI2373.pdf`  (17 pages)
2. `FP_ExecutiveSummary_IdrisJunaid_Individual_ITAI2373.pdf`  (3 pages)
3. `FP_Presentation_IdrisJunaid_Individual_ITAI2373.pptx`  (20 slides with individually written presentation notes; includes Flask frontend bonus)
4. `FP_ReflectiveJournal_Individual_ITAI2373.pdf`  (3 pages)

**GitHub portfolio:** https://github.com/IdrisJunaidAI/NewsBot-Intelligence-System-2.0  
**Live web application:** https://newsbot-intelligence-system-2-p97f.onrender.com

### Demonstration evidence included

The portfolio contains historical BBC evaluation JSON, 1,440 distinct historical labeled BBC documents represented through derived aggregates, the trained real BBC classifier, an executed multilingual MiniLM Colab notebook, 60 intentionally synthetic teaching articles, a separated official BBC RSS headline view, a live Render Free Flask site, and CI evidence of 50 passing Python / Flask tests on November 24, 2026. The presentation includes a five step browser demonstration sequence.

### Scientific facts that must not be overstated

* BBC Logistic Regression reached **95.83% accuracy** and **95.67% macro F1** on a 288 article historical held out set after duplicate removal. The **Linear SVM comparison** reached **96.88% accuracy**, but is not the deployed model.
* MiniLM Recall@1 was **18/18**, on **six synthetic passages and 18 constructed questions** only. It does not demonstrate general real news multilingual accuracy or scored translation quality.
* The 735 record BBC Test file has no verified labels, so it **cannot** support an external accuracy estimate.
* The web chatbot searches a **synthetic 60 article** corpus. Authentic historical BBC category and topic aggregates are displayed separately. Current BBC RSS links form a third source.
* The historical BBC training file lacks verified publication dates. Claims about topic evolution and historical sentiment trends remain unsupported.
* Class probabilities are uncalibrated. The product is educational and not a professional fact checker, licensed publisher archive, or validated regulatory decision system.

### Academic originality and attribution review

The prose and presentation have been substantively rewritten to express the project's measured evidence in a consistent individual narrative. The technical report includes numbered references and sources. The Uiverse components retain their MIT author comments in GitHub source. The project explicitly discloses AI assistance with coding, drafting, debugging and slide production.

**This package is not a Turnitin or institutional similarity result.** Neither originality scores nor grades can be guaranteed. The student must read the documents, correct anything that does not reflect firsthand experience, cite any further reused text, and be prepared to explain the code and experiments. Do not remove the AI assistance disclosure merely to make the work appear unaided.

### Final personal review before Canvas

* [ ] Confirm your displayed name and professor's preferred filename convention.
* [ ] Open every PDF and the PowerPoint on the device used for presentation.
* [ ] Inspect all slides and speaker notes. Rehearse the approximately 15 minute individual explanation.
* [ ] Confirm the live website and GitHub are accessible to your professor.
* [ ] Run the live demonstration using an appropriately sourced article excerpt.
* [ ] Confirm references, dataset rights and AI assistance statements are accurate.
* [ ] Upload the required files and submit the two URLs in Canvas.

**Do not upload this entire ZIP in place of the individually named files unless your Canvas instructor explicitly accepts a ZIP.**

## Matching the professor's repository report structure and bonus opportunities

The `reports/` folder now includes the descriptive filenames `executive_summary.pdf`, `technical_report.pdf` and `presentation_slides.pdf` requested in the repository tree. Canvas submission still uses the named `FP_...` files above. The presentation is now a 20 slide PowerPoint with 20-slide PDF reading copy. The optional `FP_BonusEvidence_IdrisJunaid_Individual_ITAI2373.pdf` supplies a two-page explanation of the tested batch frontend and authentic BBC limited-data study. Bonus marks remain at the professor's discretion. See `../docs/BONUS_EVIDENCE.md`.
