# Individual presentation demonstration and defense guide

## Recommended order for the 15 minute talk

The presentation has 19 slides with speaker notes. Reserve about two minutes for the live website and finish with the limitations and your individual accountability. Rehearse the slide notes rather than reading technical paragraphs verbatim.

## Browser demonstration

1. Open https://newsbot-intelligence-system-2-p97f.onrender.com/health and confirm an HTTP 200 response and the BBC model availability indicator.
2. Open the homepage. The default dashboard reports the **historical 1,440 article BBC aggregate**. Show categories and statistical topic components. Do not call these headlines from today.
3. Use the steel dataset switch to select synthetic demonstration records. State that the conversation and hosted retrieval use these 60 fictional articles; export CSV only for the chosen source.
4. Enter an English article excerpt of at least 30 characters that you have the right to use. Inspect the BBC category, raw model score, sentiment, named entities and generated extractive summary. The audio waveform can read the generated summary if browser voice support is present.
5. In the multilingual lab, use the offline query `Noticias sobre tecnología y robótica`. Explain that it is a limited local keyword mapping, not full sentence translation or hosted MiniLM. Show the Colab results slide for real pretrained multilingual MiniLM inference.
6. Visit the BBC RSS panel, open a headline through its direct BBC link and point to the visible publisher attribution.
7. End with one limitation: no timestamp verified historical trends or real multilingual cross publisher cultural interpretation has been established.

## Questions to expect

**Why is SVM better but Logistic Regression deployed?**  Linear SVM had 96.88% holdout accuracy versus 95.83% for the deployed Logistic Regression. The latter supplied convenient class score outputs. Those probabilities are not calibrated and do not verify factual truth.

**Why does the chatbot show synthetic content?**  The public repository does not redistribute original historical BBC article bodies. The chatbot indexes 60 explicitly synthetic teaching passages, while separate BBC derived aggregates provide authentic scientific evidence.

**Does 100% multilingual Recall mean NewsBot is fully accurate in all languages?**  No. It means all 18 intentionally constructed teaching queries retrieved the expected item at rank one from six synthetic passages. It is a limited evaluation and does not test translation or cultural bias.

**What did I contribute individually?**  I supplied and validated data, addressed the midterm execution environment, directed and reviewed integration, executed the multilingual model notebook in Colab, verified research outputs and managed an individually accountable portfolio. ChatGPT assisted in implementation and drafts; no unverified personal coding claims are made.

**Why no trend chart over time?**  The BBC train CSV lacked independently verified publication dates. A chronological graph would be methodologically unsound.

**How would this work in pharmaceutical quality assurance?**  Text categorization and monitoring might assist triage in principle, but regulated applications would need validated source rights, independent datasets, audit trails, domain evaluation and human oversight before use in decisions.

## Recovery plans

If Render Free wakes slowly, narrate the model architecture and use slide 8 classification results, slide 9 error matrix, and slide 12 Colab benchmark while the service starts. If the external translation provider rate limits, use the offline search and clearly label its limitations. If RSS is unreachable, show the official source URL directly without claiming the feed is loaded. If browser speech is unsupported, proceed with the extractive summary text.