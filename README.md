# NewsBot Intelligence System 2.0

**ITAI 2373 Natural Language Processing | Individual capstone portfolio | Idris O. Junaid**

[Live NewsBot website](https://newsbot-intelligence-system-2-p97f.onrender.com)  
[Full project folder](ITAI2373-NewsBot-Final/)  
[Individual submission compliance matrix](ITAI2373-NewsBot-Final/docs/individual_submission_compliance.md)

The default website dashboard now shows **authentic historical BBC News research evidence** from 1,440 distinct labeled BBC articles, with NMF/LDA aggregate topics and honest statistical limitations. The current BBC News RSS links are displayed separately, with attribution and links to the original articles. Conversational article retrieval remains a clearly labeled synthetic 60 item demonstration because the original BBC full article bodies are not redistributed on the public site.

The historical BBC classifier achieved **95.83% held out accuracy and 95.67% macro F1** using Logistic Regression on 288 held out articles. The Linear SVM comparison achieved **96.88% accuracy**. The separate executed Google Colab multilingual MiniLM study achieved **18 of 18** first rank retrieval matches on six synthetic documents and 18 controlled English, Spanish and French queries. These are different experiments with different source boundaries.

## Individual submission and historical preservation

This is the student's individual project. The original midterm notebook, technical report and reflective report remain preserved in the repository root. Current technical documentation, executive summary, 20 slide presentation and three page individual reflection are filed in `ITAI2373-NewsBot-Final/reports/`.

The student reports that the professor approved completing this capstone individually and will not form groups. The published rubric still contains group wording, so the reports and presentation use `Individual` in the group name filename position. The student's report of approval has not been independently verified against written instructor correspondence. No fictional collaborators or contributions are reported.

AI tools assisted with software scaffolding, test authoring and document drafting. The student is accountable for independent comprehension, verification and the final submission. Credit is documented in [individual contributions](ITAI2373-NewsBot-Final/docs/individual_contributions.md).

## Responsible publisher handling

The original historical BBC article texts are not in this repository. The public dashboard contains no full article bodies, only derived aggregates, classifier weights and topic words. The project is educational and not commercial; actual rights for publisher reuse must be reviewed before any further deployment or redistribution.

## Test and run

```bash
cd ITAI2373-NewsBot-Final
python -m pip install -r requirements.txt
python train.py --demo
python -m pytest -q
python scripts/smoke_real_classifier.py
python app.py
```

The source code, licenses, setup and reproducibility guidance are under the project folder.

## Canvas presentation choice and personal repository

The detailed rubric permits **PowerPoint OR a 10 to 15 minute recorded video**, not both. The final individual PowerPoint contains **20 slides with presenter notes**. A separate AI narrated practice MP4 can aid rehearsal, but it is **not** a video of the student appearing and should not be submitted as if it were personal camera footage. If the student selects the video format instead of PowerPoint, record personal narration, include the individual presenter appearing, and demonstrate the live website. See [individual repository and video submission notes](ITAI2373-NewsBot-Final/docs/VIDEO_PRESENTATION_AND_INDIVIDUAL_REPOSITORY.md).

**Individual portfolio repository link for Canvas:** https://github.com/IdrisJunaidAI/NewsBot-Intelligence-System-2.0

## Professor rubric alignment and optional bonus evidence

The repository now includes the prescribed source, notebook and documentation paths, including the separate `data/processed/` directory, nine teaching and research notebooks, source tested bonus endpoints, and the example generic PDF report aliases alongside the exact individual Canvas filenames.

The **optional web frontend bonus (up to 30 points)** includes an interactive authentic historical BBC research dashboard, single article classification, **2 to 5 article batch analysis**, synthetic article conversational queries, a multilingual lab and multiple charts. The **advanced research extension (up to 20 points)** is a 25-run measured historical BBC reduced-training-data classification study, available through an interactive learning curve and a reproducible notebook. This is not LLM few-shot prompting or evidence of unseen-category recognition.

[Read the source-linked evidence for both bonuses](ITAI2373-NewsBot-Final/docs/BONUS_EVIDENCE.md) | [View the 2-page bonus PDF](ITAI2373-NewsBot-Final/reports/FP_BonusEvidence_IdrisJunaid_Individual_ITAI2373.pdf) | [See all professor rubric requirements](ITAI2373-NewsBot-Final/docs/assessment_matrix.md).

**Presentation:** The authoritative PowerPoint is now 20 slides and has 20 speaker notes. The independent earlier practice video contains 19 slides with synthetic narration; it is not a filmed student appearance. The active presentation choice for Canvas remains the 20 slide PowerPoint.
