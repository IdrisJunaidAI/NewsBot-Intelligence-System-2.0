# Prismatic Glass Studio | UI refinement

## Design rationale

This enhancement evolves the industrial NewsBot research portfolio into a premium smoked crystal interface, with translucent dark blue glass, subtle reflective borders, blurred background color, silver highlights and ice blue emphasis. The previous industrial stylesheet remains loaded underneath so the original page has a stable appearance if the glass layer is removed. No images, fonts or third party scripts are required.

The added stylesheet is \`static/prismatic_glass.css\` and is intentionally linked **after** the original \`studio_theme.css\` and licensed \`uiverse_components.css\` in \`templates/index.html\`.

The editorial hierarchy remains:
1. Individual research identity and accurate data scope in the hero.
2. Historical BBC analytical evidence by default.
3. Current BBC RSS headline links with publisher attribution.
4. Separate English, Spanish and French language experiments.
5. Article analysis and synthetic teaching corpus conversation.

### Glass treatment

Card panels use translucent linear gradient surfaces, insets that resemble reflective light, subtle borders, blur and color saturation. The atmospheric background mixes midnight navy with muted cyan and violet. A glass navigation rail creates a clear site wide visual language. Three concise hero capability labels distinguish historical BBC analytics, multilingual experimentation and attributed RSS links.

### Accessibility and constraints

Frosted panels retain high contrast text. The design offers solid color CSS fallback for browsers without backdrop filter support. It respects \`prefers-reduced-motion\`, \`prefers-reduced-transparency\` and \`prefers-contrast\` where supported. Mobile widths receive simpler layouts and blur reduction.

The original five Uiverse controls, their credit comments and MIT licenses are unchanged. The website does not add external calls, dependencies, subscription charges or alter the data endpoints. The steel switch still determines BBC versus demonstration data. A glass appearance never implies that the chatbot indexes authentic BBC news content.

### Individual submission status

The student informed the assistant on November 24, 2026 that the professor accepts individual completion and does not want to create any group. The individual submission statements in the README and compliance/contribution records reflect that report. The detailed course material originally referenced groups, so exact filename labels should be reconciled against any instructor naming guidance. The existing individual PDFs and PPTX were **not regenerated** in this visual change; their content requires a final consistency review before Canvas submission.

### Verification

Run \`python -m pytest -q\` and CI. Confirm homepage, stylesheet asset, dashboard source switch, CSV export, RSS links, multilingual consent, analysis requests, and the torch, waveform, loader and star effects in a real browser. Automated tests verify structure and served assets, not the appearance of browser compositing or spoken audio. No paid Render resources are required.
