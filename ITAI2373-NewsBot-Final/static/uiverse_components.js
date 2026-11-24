/*
From Uiverse.io by asif_6635 - https://uiverse.io/asif_6635/moody-turtle-2
MIT License, Copyright (c) asif_6635 (Asif)

From Uiverse.io by StealthWorm - https://uiverse.io/StealthWorm/spotty-horse-48
MIT License, Copyright (c) StealthWorm (thierry)

From Uiverse.io by Pradeepsaranbishnoi - https://uiverse.io/Pradeepsaranbishnoi/honest-penguin-58
MIT License, Copyright (c) Pradeepsaranbishnoi (Pradeep Saran)

From Uiverse.io by Nawsome - https://uiverse.io/Nawsome/breezy-ape-20
MIT License, Copyright (c) Nawsome

From Uiverse.io by kelvyn_8843 - https://uiverse.io/kelvyn_8843/big-cheetah-20
MIT License, Copyright (c) KSAplay (Kenny), kelvyn_8843 (kelv)

Integration code only; borrowed visuals remain in uiverse_components.css.
*/
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const activeRequests = new Set();
  const loader = byId('nb-loading-curtain');
  const loaderText = byId('nb-loading-message');
  const loadingLabels = {
    analyze_out:'ANALYZING ARTICLE',
    chat_out:'ASKING NEWSBOT',
    ml_result:'PROCESSING LANGUAGE',
    ml_search_results:'SEARCHING TOPICS',
    dashboard_status:'LOADING BBC EVIDENCE'
  };

  function setLoading(requestId, busy) {
    if (busy) activeRequests.add(requestId);
    else activeRequests.delete(requestId);
    if (!loader) return;
    loader.hidden = activeRequests.size === 0;
    loader.setAttribute('aria-hidden',loader.hidden?'true':'false');
    if (!loader.hidden) {
      const recent = [...activeRequests].slice(-1)[0];
      loaderText.textContent = loadingLabels[recent] || 'PROCESSING REQUEST';
    }
  }

  const motionReduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const explore = byId('nb-explore');
  if (explore) {
    explore.addEventListener('click',() => {
      byId('analytics_title').scrollIntoView({
        behavior:motionReduced ? 'auto':'smooth',block:'start'
      });
    });
  }

  const torch = byId('nb_torch_toggle');
  if (torch) {
    const updateTorch = () => {
      document.body.classList.toggle('nb-illumination',torch.checked);
      const label = byId('nb-torch-label');
      if (label) label.textContent = 'STUDIO LIGHT / ' + (torch.checked ? 'ON':'OFF');
    };
    torch.addEventListener('change',updateTorch);
    updateTorch();
  }

  const audioButton = byId('nb-summary-play');
  const audioPlayer = byId('nb-summary-player');
  const audioTime = byId('nb-wave-time');
  const audioCaption = byId('nb-wave-caption');
  const audioIcon = byId('nb-wave-icon');
  const analysisOutput = byId('analyze_out');
  const speechSupported = 'speechSynthesis' in window &&
     'SpeechSynthesisUtterance' in window;

  let phrase = '';
  let currentUtterance = null;
  let playing = false;
  let paused = false;
  let seconds = 0;
  let clock = null;
  let speechGeneration = 0;
  const playPath = 'M8 5v14l11-7z';
  const pausePath = 'M6 5h4v14H6zm8 0h4v14h-4z';

  function drawElapsed() {
    if (audioTime) audioTime.textContent =
      Math.floor(seconds/60) + ':' + String(seconds%60).padStart(2,'0');
  }

  function stopClock() {
    if (clock !== null) window.clearInterval(clock);
    clock = null;
  }

  function reflectPlayback() {
    if (!audioButton || !audioPlayer) return;
    audioPlayer.dataset.playing = String(playing && !paused);
    audioButton.setAttribute('aria-label',playing && !paused
      ? 'Pause generated article summary'
      : paused ? 'Resume generated article summary' : 'Play generated article summary');
    if (audioIcon) audioIcon.setAttribute('d',playing && !paused ? pausePath : playPath);
    audioButton.disabled = !speechSupported || !phrase;
  }

  function finishSpeech(reason) {
    stopClock();
    playing = false;
    paused = false;
    currentUtterance = null;
    reflectPlayback();
    if (audioCaption && reason) audioCaption.textContent = reason;
  }

  function resetSpeech() {
    speechGeneration += 1;
    if (speechSupported) window.speechSynthesis.cancel();
    stopClock();
    seconds = 0;
    drawElapsed();
    playing = false;
    paused = false;
    currentUtterance = null;
    reflectPlayback();
  }

  function collectSummary() {
    if (!analysisOutput) return;
    const node = analysisOutput.querySelector('.summary-text');
    const nextPhrase = node ? node.textContent.trim().slice(0,2500) : '';
    if (nextPhrase !== phrase) {
      resetSpeech();
      phrase = nextPhrase;
      reflectPlayback();
      if (audioCaption) {
        audioCaption.textContent = !speechSupported
          ? 'Speech playback is not supported by this browser.'
          : phrase
          ? 'Play the generated summary using your browser’s speech voice.'
          : 'Analyze an article to enable browser speech playback.';
      }
    }
  }

  if (audioButton) {
    if (analysisOutput && 'MutationObserver' in window) {
      new MutationObserver(collectSummary).observe(analysisOutput,{
        childList:true,subtree:true,characterData:true
      });
    }
    collectSummary();
    audioButton.addEventListener('click',() => {
      if (!speechSupported || !phrase) return;
      const engine = window.speechSynthesis;
      if (playing && !paused) {
        engine.pause();
        paused = true;
        stopClock();
        reflectPlayback();
        return;
      }
      if (playing && paused) {
        engine.resume();
        paused = false;
        clock = window.setInterval(() => {seconds += 1;drawElapsed();},1000);
        reflectPlayback();
        return;
      }
      resetSpeech();
      const myGeneration = speechGeneration;
      const speech = new window.SpeechSynthesisUtterance(phrase);
      currentUtterance = speech;
      speech.lang = 'en-US';
      speech.rate = .95;
      speech.onstart = () => {
        if (myGeneration !== speechGeneration) return;
        playing = true;
        paused = false;
        reflectPlayback();
        clock = window.setInterval(() => {seconds += 1;drawElapsed();},1000);
      };
      speech.onend = () => {
        if (myGeneration === speechGeneration)
          finishSpeech('Summary playback completed.');
      };
      speech.onerror = () => {
        if (myGeneration === speechGeneration)
          finishSpeech('Speech service unavailable in this browser.');
      };
      if (audioCaption) audioCaption.textContent = 'Reading extractive summary…';
      try {
        engine.speak(speech);
      } catch (_) {
        finishSpeech('Speech playback could not start.');
      }
    });
    window.addEventListener('pagehide',() => {
      if (currentUtterance) resetSpeech();
    });
  }

  window.NewsBotUI = Object.freeze({setLoading});
})();
