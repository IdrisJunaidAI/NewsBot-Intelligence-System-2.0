# Industrial Studio UI: Five MIT Uiverse Components

## Existing architecture and inspiration

This revision remains within Flask, native HTML, plain CSS and JavaScript. It does not migrate the working BBC analytics system to React or Tailwind. The visual direction is dark industrial geometry, metallic forms, selective neon highlights, negative space and soft depth based on the provided photograph and linked design inspiration.

## Placement and working behaviors

1. **Audio waveform input:** Uiverse by asif_6635. The article analyzer uses the browser speech synthesis feature to read a real generated extractive summary. Playback is disabled until that summary exists. Its time label measures actual elapsed playback rather than displaying an invented audio duration. The UI does not serve a podcast or an MP3.

2. **Animated SPACE button:** Uiverse by StealthWorm. The original moving star field, glow, multicolor gradient ring and hover effect are scoped to the hero EXPLORE control. It scrolls to authentic BBC analytics.

3. **Industrial steel switch:** Uiverse by Pradeepsaranbishnoi. The two metal switch states select historical BBC analytics (default) or an explicitly synthetic demonstration. CSV export follows the chosen source.

4. **Twelve dot loader:** Uiverse by Nawsome. Its original 3D rotating dot geometry appears while actual dashboard, analysis, conversation or multilingual requests are pending, and is cleared when requests settle.

5. **Torch checkbox:** Uiverse by kelvyn_8843. Its 3D voxel lamp controls only studio illumination of the hero and is not connected to model scoring or data provenance.

## Credits, accessibility, and limits

Exact author and MIT credits appear in comments at the beginning of the new component CSS and JavaScript and immediately beside each HTML element. All generic styles are namespaced to avoid overriding existing Flask page components. Native buttons, labels, visible keyboard focus, mobile layouts, progress status, and reduced-motion accommodations are included.

Speech playback depends on browser and operating system support. The underlying voice may be processed by the browser or OS locally or remotely; users should not submit confidential articles. No additional server text-to-speech integration has been introduced. The loader has no fictional completion percentage.

The dashboard still defaults to authentic aggregates from 1,440 unique historical BBC articles; live attributed RSS headlines are separate. The chatbot and multilingual stored-article search remain an explicitly synthetic English teaching collection. UI animations do not affect statistical evaluation.

## Validation

Run python -m pytest -q. Confirm on a real browser that the EXPLORE button scrolls, dataset switch modifies the analytics and CSV source, torch changes ambient lighting, the loader displays only during requests, and summary playback appears only after successful article analysis. Verify a narrow mobile viewport, keyboard focus and the reduced-motion preference. The existing Render Free compute plan remains sufficient; this UI adds no paid resources.
