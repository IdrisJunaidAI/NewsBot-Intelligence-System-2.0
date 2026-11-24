"""Transparent multilingual search routes with a reliable offline alternative.

"semantic": installed multilingual MiniLM encoder only (not active on Render Free).
"offline": curated news-topic Spanish/French -> English keywords plus LSA/TF IDF.
"translated": consent-gated third-party translation; if it fails, disclose a
limited offline topic mapping fallback. Never imply a full translation occurred.
"""
from src.multilingual.offline_query import offline_news_query

class CrossLingualAnalyzer:
    def __init__(self,search,detector=None,translator=None):
        self.search_engine=search
        self.detector=detector
        self.translator=translator

    def _offline(self,query,language,top_k,why=None,external_used=False):
        mapped=offline_news_query(query,language)
        if not mapped["available"]:
            return {"available":False,"mode":"offline","language":language,
                    "reason":mapped["reason"],
                    "external_service_used":bool(external_used)}
        search_mode="lsa" if getattr(self.search_engine,"lsa_available",False) else "lexical"
        results=self.search_engine.search(mapped["query_en"],top_k=top_k,mode=search_mode)
        note=mapped["note"]
        if why:
            note="External machine translation was unavailable. Offline keyword mapping used instead. "+note
        return {"available":True,"mode":"offline","language":language,
                "method":"Offline topic keywords + "+results["method"],
                "matches":results["results"],"normalized_query":mapped["query_en"],
                "matched_terms":mapped["matched_terms"],
                "unmapped_terms":mapped.get("unmapped_terms",[]),
                "external_service_used":bool(external_used),
                "fallback_from":why,
                "note":note,
                "source":"English synthetic classroom teaching collection, not live news"}

    def compare(self,query,top_k=5,mode="semantic",external_consent=False):
        if not isinstance(query,str) or len(query.strip())<4:
            raise ValueError("Please enter a meaningful search query")
        if mode not in ("semantic","translated","offline"):
            raise ValueError("Mode must be semantic, translated or offline")
        if not isinstance(top_k,int) or not 1<=top_k<=10:
            raise ValueError("top_k must be between 1 and 10")
        query=query.strip()
        if len(query)>500:
            raise ValueError("Maximum search query length is 500 characters")
        detection=self.detector.detect(query) if self.detector else {"language":"unknown"}
        code=detection["language"]
        if mode=="semantic":
            if self.search_engine.method!="multilingual sentence embeddings":
                return {"available":False,"mode":"semantic","language":detection,
                        "reason":"True multilingual neural retrieval requires the optional Sentence Transformers encoder; use the Colab notebook or a separately enabled model environment.",
                        "external_service_used":False}
            results=self.search_engine.search(query,top_k=top_k)
            return {"available":True,"mode":"semantic","language":detection,
                    "method":results["method"],"matches":results["results"],
                    "external_service_used":False,
                    "note":"Shared multilingual vectors; relevance is estimated, not fact verification"}
        if code=="unknown":
            return {"available":False,"mode":mode,"language":detection,
                    "reason":"Language uncertain. Try a longer English, Spanish or French query.",
                    "external_service_used":False}
        if code not in {"en","es","fr"}:
            return {"available":False,"mode":mode,"language":detection,
                    "reason":"This demonstration supports English, Spanish and French.",
                    "external_service_used":False}

        if mode=="offline":
            return {**self._offline(query,code,top_k),"language":detection}

        # Opt-in translation route, kept distinct from the local path.
        if code=="en":
            translated=None
            query_en=query
        else:
            if self.translator is None:
                return {"available":False,"mode":"translated","language":detection,
                        "reason":"External translator unavailable; choose Offline topic search.",
                        "external_service_used":False}
            translated=self.translator.translate(query,source=code,target="en",
                                                  external_consent=external_consent)
            if not translated["available"]:
                # Consent denied: DO NOT silently invoke an external service or
                # substitute a lower fidelity method under "translated" mode.
                if not external_consent:
                    return {"available":False,"mode":"translated","language":detection,
                            "reason":translated["reason"],"external_service_used":False}
                fallback=self._offline(query,code,top_k,
                                       why=translated.get("error_code","provider_unavailable"),
                                       external_used=translated.get("external_service_used",False))
                if fallback["available"]:
                    return {**fallback,"language":detection,
                            "translation_error_code":translated.get("error_code"),
                            "warning":translated["reason"]}
                return {"available":False,"mode":"translated","language":detection,
                        "reason":translated["reason"]+" "+fallback["reason"],
                        "translation_error_code":translated.get("error_code"),
                        "external_service_used":translated.get("external_service_used",False)}
            query_en=translated["text"]
        search_mode="lsa" if getattr(self.search_engine,"lsa_available",False) else "lexical"
        results=self.search_engine.search(query_en,top_k=top_k,mode=search_mode)
        return {"available":True,"mode":"translated","language":detection,
                "translated_query":query_en if translated else None,
                "method":("Translation-assisted " if translated else "Direct English ")+results["method"],
                "matches":results["results"],
                "external_service_used":bool(translated and translated.get("external_service_used")),
                "note":"Query converted to English with external translation then retrieved in English; NOT shared multilingual transformer retrieval. Translation quality is unverified."}
