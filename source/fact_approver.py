import os
from dotenv import load_dotenv

from duckduckgo_search import DDGS
from link_reader import Scraper
from fault_probability_predictor import ModelProbabilityAnalyzer
from api_fact_checker import LLMFactChecker, LLMResponse


load_dotenv()

CATBOOST_MODEL = "models/catboost_model.cbm"

if os.path.exists("models/rubert"):
    RUBERT_MODEL = "models/rubert"
else:
    RUBERT_MODEL = "alcofighter/rubert"

API_KEY = os.getenv("API_KEY")


class FactChecker:
    def __init__(self):
        self.scraper = Scraper()
        self.model_prob_analyzer = ModelProbabilityAnalyzer(CATBOOST_MODEL, RUBERT_MODEL)
        self.llm_fact_checker = LLMFactChecker(API_KEY)
    
    def analyse(self, url: str):
        article = self.scraper.scrap(url)

        ml_probability = self.model_prob_analyzer.predict(article["title"])
        search_results = search_web(article["title"])
        
        llm_response = self.llm_fact_checker.check(
            article["title"],
            ml_probability,
            search_results
        )
        
        return llm_response


def search_web(query: str) -> list:
    results = []
    try:
        query = " ".join(query.split()[:6])

        with DDGS(timeout=5) as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "content": r.get("body", ""),
                        "url": r.get("href", ""),
                    }
                )
    except Exception as e:
        return []

    return results      