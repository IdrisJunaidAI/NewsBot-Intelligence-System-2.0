"""Bounded bilingual news-topic query mapping for offline English corpus retrieval.

This is a transparent, manually curated vocabulary adapter, NOT machine translation,
not a pretrained multilingual model, and not an exhaustive language dictionary.
It never sends text to a third party and is safe when external translation is down.
"""
import re
import unicodedata

# Limited to concepts represented in the five-class teaching corpus.
TOPIC_TERMS = {
    "es": {
        "tecnologia":"technology", "tecnologias":"technology", "tecnologico":"technology",
        "tecnologica":"technology", "robotica":"robotics", "robot":"robotics",
        "robots":"robotics", "algoritmo":"algorithm", "algoritmos":"algorithm",
        "inteligencia":"intelligence", "artificial":"artificial",
        "aprendizaje":"learning", "automatico":"machine learning",
        "software":"software", "datos":"data", "seguridad":"security",
        "ciberseguridad":"cybersecurity", "redes":"network", "internet":"internet",
        "ordenador":"computer", "computadora":"computer", "nube":"cloud",
        "ciencia":"science", "cientifico":"research", "investigacion":"research",
        "negocios":"business", "empresa":"company", "empresas":"companies",
        "economia":"economy", "economico":"economy", "mercado":"market",
        "mercados":"market", "finanzas":"finance", "banco":"bank",
        "bancos":"bank", "inversion":"investment", "comercio":"trade",
        "gobierno":"government", "politica":"politics", "politico":"politics",
        "parlamento":"parliament", "elecciones":"elections", "presidente":"president",
        "deporte":"sport", "deportes":"sport", "futbol":"football", "partido":"match",
        "equipo":"team", "campeonato":"championship", "jugador":"player",
        "entretenimiento":"entertainment", "pelicula":"film", "peliculas":"film",
        "cine":"cinema", "musica":"music", "actor":"actor", "actores":"actors",
        "universidad":"university", "educacion":"education", "industria":"industry",
        "energia":"energy", "clima":"climate", "salud":"health"
    },
    "fr": {
        "technologie":"technology", "technologies":"technology", "technologique":"technology",
        "robotique":"robotics", "robot":"robotics", "robots":"robotics",
        "algorithme":"algorithm", "algorithmes":"algorithm", "intelligence":"intelligence",
        "artificielle":"artificial", "artificiel":"artificial",
        "apprentissage":"learning", "automatique":"machine learning",
        "logiciel":"software", "logiciels":"software", "donnees":"data",
        "securite":"security", "cybersecurite":"cybersecurity", "reseau":"network",
        "reseaux":"network", "internet":"internet", "ordinateur":"computer",
        "informatique":"computing", "nuage":"cloud",
        "science":"science", "recherche":"research", "scientifique":"research",
        "affaires":"business", "entreprise":"company", "entreprises":"companies",
        "economie":"economy", "economique":"economy", "marche":"market",
        "marches":"market", "finance":"finance", "banque":"bank",
        "investissement":"investment", "commerce":"trade",
        "gouvernement":"government", "politique":"politics", "parlement":"parliament",
        "elections":"elections", "president":"president",
        "sport":"sport", "sports":"sport", "football":"football", "match":"match",
        "equipe":"team", "championnat":"championship", "joueur":"player",
        "divertissement":"entertainment", "film":"film", "films":"film",
        "cinema":"cinema", "musique":"music", "acteur":"actor", "acteurs":"actors",
        "universite":"university", "education":"education", "industrie":"industry",
        "energie":"energy", "climat":"climate", "sante":"health"
    }
}

IGNORE = {
    "es": set("noticias noticia sobre acerca de del el la los las y o en un una para con por que quien cuando nuevas nueva nuevo nuevos ultimas ultima reciente recientes".split()),
    "fr": set("actualites actualite nouvelles nouvelle sur de du des le la les et ou un une pour avec dans a au aux qui quoi quand dernier derniers dernieres recentes recent".split())
}

def _normalize(text):
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))

def offline_news_query(query, language):
    """Return mapped English topic terms, never assert full translation."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty")
    if language == "en":
        return {"available":True,"query_en":query.strip(),"language":"en",
                "matched_terms":[],"method":"Direct English query, no translation",
                "note":"English input used directly for lexical or LSA retrieval."}
    if language not in TOPIC_TERMS:
        return {"available":False,"query_en":None,"language":language,
                "matched_terms":[],"reason":"Offline topic mapping supports Spanish and French only."}
    tokens = re.findall(r"[a-z]+",_normalize(query))
    found = []
    terms = []
    seen = set()
    for token in tokens:
        translated = TOPIC_TERMS[language].get(token)
        if translated is None:
            continue
        found.append(token)
        if translated not in seen:
            terms.append(translated)
            seen.add(translated)
    if not terms:
        return {"available":False,"query_en":None,"language":language,
                "matched_terms":[],"reason":"No supported news topic keywords were found. Try technology, robotics, business, sport, politics, or film in Spanish or French."}
    ignored = [word for word in tokens if word not in TOPIC_TERMS[language] and word not in IGNORE[language]]
    return {"available":True,"query_en":" ".join(terms),"language":language,
            "matched_terms":found,"unmapped_terms":ignored[:12],
            "method":"Offline curated news-topic keyword mapping",
            "note":"Limited vocabulary lookup only. Unrecognized words and negation may be omitted; this is NOT full sentence translation, cross-language transformer search, or live news."}
