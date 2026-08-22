import json
from pydantic import BaseModel, Field
from gigachat import GigaChat


class LLMResponse(BaseModel):
    verdict: str = Field(
        description="Вердикт: ФАКТ ПОДТВЕРЖДЕН, ФАКТ ОПРОВЕРГНУТ или НЕДОСТАТОЧНО ДАННЫХ"
    )
    confidence_level: int = Field(
        description="Оценка доверия от 0 до 100 на основе ответа модели"
    )
    explanation: str = Field(
        description="Пояснение по вердикту"
    )
    search_result: list[str] = Field(
        description="Список из 2-3 найденных похожих статей"
    )


class LLMFactChecker:
    def __init__(self, api_key, model="GigaChat-2-Pro"):
        self.client = GigaChat(
            credentials=api_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False
        )
        
        self.model = model
    
    def check(self, title: str, ml_score: float, search_result: str) -> LLMResponse:
        system_prompt = """
        Твоя задача проанализировать предоставленную новость. Ты получишь заголовок и факты из статьи,
        оценку вероятности истинности этой статьи от ML-модели. Необходимо на основании этого и похожих
        новостей в сети подтвердить описанный факт или отклонить его.
        В поле search_result добавь найденные в сети похожие сведения. Если статей нет, верни пустой список.
        Отвечай строго в заданном формате и используй только реальные факты. Выставляй вердикт исключительно в формате Факт подтвержден,
        Факт опровергнут или Недостаточно данных.
        Если в интернете не получилось найти похожие статьи, но оценка модели велика (>80), то подтверждай факт
        """
        
        user_prompt = f"""
        Заголовок статьи: {title},
        оценка ии-модели: {ml_score},
        похожии статьи в сети: {search_result}
        """
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "model": self.model,
            "temperature": 0.2,
        }
        
        try:
            response = self.client.chat.parse(
                payload=payload,
                response_format=LLMResponse
            )
            
            return response[1]

        except Exception as e:
            print(f"Произошла ошибка {e}")