# NewsBot Intelligence System 2.0

**ITAI 2373 Natural Language Processing | Individual capstone portfolio | Idris O. Junaid**

[Live NewsBot website](https://newsbot-intelligence-system-2-p97f.onrender.com)  
[Full project folder](ITAI2373-NewsBot-Final/)  
[Individual submission compliance matrix](ITAI2373-NewsBot-Final/docs/individual_submission_compliance.md)

The default website dashboard now shows **authentic historical BBC News research evidence** from 1,440 distinct labeled BBC articles, with NMF/LDA aggregate topics and honest statistical limitations. The current BBC News RSS links are displayed separately, with attribution and links to the original articles. Conversational article retrieval remains a clearly labeled synthetic 60 item demonstration because the original BBC full article bodies are not redistributed on the public site.

The historical BBC classifier achieved **95.83% held out accuracy and 95.67% macro F1** using Logistic Regression on 288 held out articles. The Linear SVM comparison achieved **96.88% accuracy**. The separate executed Google Colab multilingual MiniLM study achieved **18 of 18** first rank retrieval matches on six synthetic documents and 18 controlled English, Spanish and French queries. These are different experiments with different source boundaries.

## Individual submission and historical preservation

This is the student's individual project. The original midterm notebook, technical report and reflective report remain preserved in the repository root. Current technical documentation, executive summary, 20 slide presentation and three page individual reflection are filed in `ITAI2373-NewsBot-Final/reports/`.

The published instructor instructions specify a group format and a group journal. The `Individual` filename segment in this version is a transparent proposed alternative, **not confirmed instructor approval**. No fictional collaborators or contributions are reported.

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
