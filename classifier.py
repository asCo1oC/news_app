# classifier.py
import re
from typing import Optional, Dict, List

REGION_KEYWORDS = {
    "Asia": {
        "countries": [
            "china", "japan", "india", "south korea", "north korea", "korea",
            "thailand", "vietnam", "indonesia", "malaysia", "singapore",
            "philippines", "myanmar", "cambodia", "laos", "bangladesh",
            "pakistan", "sri lanka", "nepal", "mongolia", "taiwan",
            "kazakhstan", "uzbekistan", "kyrgyzstan", "tajikistan",
            "turkmenistan", "afghanistan"
        ],
        "cities": [
            "beijing", "tokyo", "new delhi", "seoul", "jakarta", "bangkok",
            "manila", "kathmandu", "hanoi", "kuala lumpur"
        ],
        "geo_markers": [
            "east asia", "southeast asia", "south asia", "central asia",
            "asia-pacific", "indo-pacific", "tibet", "himalaya",
            "south china sea", "east china sea", "korean peninsula"
        ],
        "context": ["asian", "yuan", "yen", "rupee", "won", "asean", "apec"]
    },

    "Middle East": {
        "countries": [
            "iran", "israel", "saudi arabia", "uae", "united arab emirates",
            "qatar", "kuwait", "bahrain", "oman", "yemen", "iraq", "syria",
            "lebanon", "jordan", "palestine", "palestinian", "egypt",
            "turkey", "türkiye", "gaza", "west bank"
        ],
        "cities": [
            "tehran", "jerusalem", "riyadh", "dubai", "doha", "baghdad",
            "damascus", "beirut", "amman", "cairo", "ankara"
        ],
        "geo_markers": [
            "middle east", "gulf", "persian gulf", "red sea", "levant",
            "arabian peninsula", "strait of hormuz", "suez canal", "gaza strip"
        ],
        "organizations": ["gcc", "opec", "arab league", "hamas", "hezbollah", "houthis", "isis"],
        "context": [
            "iran war", "israel-hamas", "iran-israel", "oil prices", "barrel",
            "supreme leader", "pro-iran", "middle-east"
        ]
    },

    "USA": {
        "institutions": [
            "white house", "congress", "senate", "house of representatives",
            "supreme court", "pentagon", "state department", "capitol",
            "federal reserve", "fed", "sec", "fbi", "cia", "nsa",
            "homeland security", "justice department", "tsa", "air force"
        ],
        "politics": [
            "president", "vice president", "senator", "congressman",
            "governor", "democrat", "republican", "biden", "trump",
            "vance", "rubio", "noem", "election", "campaign", "aipac"
        ],
        "locations": [
            "washington dc", "new york", "california", "texas", "florida",
            "michigan", "virginia", "ohio", "georgia", "nebraska",
            "rhode island", "illinois", "wall street"
        ],
        "culture_sports": [
            "march madness", "ncaa", "big east", "big 12",
            "world baseball classic", "wbc", "players championship",
            "oscars", "razzies", "disney", "buzzfeed"
        ],
        "context": [
            "us ", "usa", "american", "us economy", "us dollar", "usd",
            "nasdaq", "dow jones", "americans", "us air force"
        ]
    },

    "Europe": {
        "countries": [
            "germany", "france", "united kingdom", "uk", "britain",
            "italy", "spain", "poland", "netherlands", "belgium",
            "sweden", "norway", "denmark", "finland", "switzerland",
            "austria", "portugal", "greece", "czech", "romania",
            "hungary", "bulgaria", "croatia", "slovakia", "slovenia",
            "ireland", "luxembourg", "estonia", "latvia", "lithuania",
            "ukraine", "russia", "belarus", "moldova", "serbia", "bosnia"
        ],
        "cities": [
            "berlin", "paris", "london", "rome", "madrid", "warsaw",
            "brussels", "amsterdam", "kyiv", "moscow", "vienna",
            "dublin", "lisbon", "athens", "budapest", "bucharest"
        ],
        "geo_markers": [
            "europe", "eastern europe", "western europe", "northern europe",
            "southern europe", "balkans", "scandinavia", "baltic", "eu", "eurozone"
        ],
        "organizations": [
            "european union", "eu", "eurozone", "nato", "council of europe",
            "osce", "schengen", "ecb", "european central bank"
        ],
        "context": [
            "ukraine war", "ukraine worries", "eu sanctions",
            "russia sanctions", "brexit", "euro", "eur", "british"
        ]
    }
}


def classify_news_region(title: str, description: str = "") -> str:
    """
    Классифицирует новость по региону на основе ключевых слов.

    Args:
        title: Заголовок новости
        description: Описание новости (опционально)

    Returns:
        Название региона или 'International' если не удалось классифицировать
    """
    text = f"{title} {description}".lower()

    scores: Dict[str, int] = {}

    for region, keyword_dict in REGION_KEYWORDS.items():
        score = 0
        for keyword_list in keyword_dict.values():
            for keyword in keyword_list:
                if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                    score += 1
        if score > 0:
            scores[region] = score

    if scores:
        max_score = max(scores.values())
        candidates = [r for r, s in scores.items() if s == max_score]

        # Приоритет при равенстве
        priority = ["Middle East", "USA", "Europe", "Asia"]
        for region in priority:
            if region in candidates:
                return region

    return "International"


def classify_articles(articles: List[dict]) -> List[dict]:
    """
    Классифицирует массив статей по регионам.

    Args:
        articles: Список словарей с новостями

    Returns:
        Список словарей с добавленным полем category
    """
    for article in articles:
        article['category'] = classify_news_region(
            article.get('title', ''),
            article.get('description', '')
        )
    return articles