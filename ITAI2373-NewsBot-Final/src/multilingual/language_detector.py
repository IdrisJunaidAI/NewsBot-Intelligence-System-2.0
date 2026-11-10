"""Language identification; optional statistical detector plus cautious fallback."""
import re
try:from langdetect import detect,DetectorFactory
except ImportError:detect=None
else:DetectorFactory.seed=0
_WORDS={
    'en':set('the and government said with companies market team this is new after for in of'.split()),
    'es':set('el la los las de que y en para con un una gobierno empresa mercado según noticias'.split()),
    'fr':set('le la les des de et dans avec pour une un gouvernement entreprises marché selon nouvelles'.split())
}
class LanguageDetector:
    def detect(self,text):
        if not text or len(text.strip())<20:return {'language':'unknown','method':'insufficient text'}
        if detect:
            try:return {'language':detect(text),'method':'langdetect statistical model'}
            except Exception:pass
        words=re.findall(r'\b\w+\b',text.lower())
        scores={l:sum(w in dictionary for w in words) for l,dictionary in _WORDS.items()}
        best=max(scores,key=scores.get)
        return {'language':best if scores[best]>=2 else 'unknown',
                'method':'limited language stopword heuristic; install langdetect',
                'note':'Heuristic is not reliable for short or code-switched articles'}
