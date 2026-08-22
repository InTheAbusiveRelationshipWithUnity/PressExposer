import trafilatura

from typing import Dict, Optional


class Scraper:
    def __init__(self) -> None:
        self.header = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def scrap(self, url: str) -> Optional[Dict[str, str]]:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                meta = trafilatura.extract_metadata(downloaded)

                if text:
                    return {
                        "title" : meta.title if meta.title else "",
                        "text" : text,
                        "date" : meta.date if meta.date else "",
                        "url" : url
                    }
        
        except Exception as e:
            print(f"Программа остановлена с ошибкой {e}")
