import json
from pydantic import BaseModel, Field
from openai import OpenAI


class LLMResponse(BaseModel):
    verdict: str = Field(
        description="Вердикт: Факт подтвержден, факт опровергнут или недостаточно данных"
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
    def __init__(self, api_key, model="llama-3.1-70b-versatile"):
        self.client = OpenAI(api_key=api_key,
                             base_url="https://api.groq.com/openai/v1"
                             )
        self.model = model
    
    def check(self, title: str, ml_score: float, search_result: str) -> LLMResponse:
        system_prompt = """
        Твоя задача проанализировать предоставленную новость. Ты получишь заголовок и факты из статьи,
        оценку вероятности истинности этой статьи от ML-модели. Необходимо на основании этого и похожих
        новостей в сети подтвердить описанный факт или отклонить его.
        В поле search_result добавь найденные в сети похожие сведения. Если статей нет, верни пустой список.
        Отвечай строго в заданном формате и используй только реальные факты
        """
        
        user_prompt = f"""
        Заголовок статьи: {title},
        оценка ии-модели: {ml_score},
        похожии статьи в сети: {search_result}
        """
        
        response = self.client.beta.chat.completions.parse(
            model = self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format = LLMResponse,
            temperature=0.2
        )
        
        return response.choices[0].message.parsed