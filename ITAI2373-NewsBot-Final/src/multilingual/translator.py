"""Consent-gated optional external translation with rate limit protection.

External GoogleTranslator via deep-translator may raise TooManyRequests (HTTP 429).
We never bypass rate limits, retry automatically or expose raw provider errors.
The optional external request is separate from the offline topic retrieval path.
"""
import importlib.util
import time

ALLOWED = frozenset({"en","es","fr"})
COOLDOWN_SECONDS = 600

class Translator:
    def __init__(self,provider_factory=None,clock=None):
        self.provider_factory=provider_factory
        self._clock=clock or time.monotonic
        self._cooldown_until=0.0

    def status(self):
        installed=(self.provider_factory is not None or importlib.util.find_spec("deep_translator") is not None)
        seconds=max(0,int(self._cooldown_until-self._clock()))
        return {"installed":bool(installed),
                "ready":"optional consent-gated external provider; subject to remote rate limits",
                "languages":sorted(ALLOWED),"provider":"deep-translator GoogleTranslator (external)",
                "rate_limited":seconds>0,"local_cooldown_seconds":seconds,
                "offline_topic_search":True,
                "privacy":"Text is sent to a third party only on explicit request with consent; do not send sensitive information",
                "translation_quality":"Not independently evaluated; names, negation and cultural meaning may be altered"}

    def translate(self,text,source="auto",target="en",external_consent=False):
        if not isinstance(text,str) or not text.strip():
            raise ValueError("A nonempty text is required")
        text=text.strip()
        if len(text)>2000:
            raise ValueError("Maximum translation input is 2000 characters")
        if source not in (ALLOWED|{"auto"}) or target not in ALLOWED:
            raise ValueError("English, Spanish and French are the supported translation languages")
        if source==target:
            return {"available":True,"text":text,"provider":"identity, no translation required",
                    "source":source,"target":target,"external_service_used":False,
                    "note":"No machine translation performed"}
        if not external_consent:
            return {"available":False,"text":None,"source":source,"target":target,
                    "reason":"Consent required before text is sent to an external translation service",
                    "error_code":"consent_required","external_service_used":False}
        if self._clock()<self._cooldown_until:
            return {"available":False,"text":None,"source":source,"target":target,
                    "error_code":"rate_limited","external_service_used":False,
                    "reason":"External translation was recently rate limited. Please use offline topic search; retry translation later."}
        factory=self.provider_factory
        if factory is None:
            try:
                from deep_translator import GoogleTranslator
                factory=GoogleTranslator
            except ImportError:
                return {"available":False,"text":None,"source":source,"target":target,
                        "error_code":"provider_unavailable","external_service_used":False,
                        "reason":"Optional external translation dependency is unavailable. Offline topic search works without it."}
        try:
            result=factory(source=source,target=target).translate(text)
            if not isinstance(result,str) or not result.strip():
                raise RuntimeError("Empty translation result")
            return {"available":True,"text":result.strip(),
                    "provider":"GoogleTranslator via deep-translator",
                    "source":source,"target":target,"external_service_used":True,
                    "note":"External machine translation; verify proper names, meaning and local context."}
        except Exception as exc:
            limited=(type(exc).__name__=="TooManyRequests" or
                     getattr(getattr(exc,"response",None),"status_code",None)==429)
            if limited:
                self._cooldown_until=self._clock()+COOLDOWN_SECONDS
            return {"available":False,"text":None,"source":source,"target":target,
                    "error_code":"rate_limited" if limited else "provider_unavailable",
                    "external_service_used":True,
                    "reason":("External translation rate limit reached. Offline topic search remains available; retry translation later."
                              if limited else
                              "External translation provider is temporarily unavailable. Use offline topic search instead.")}
