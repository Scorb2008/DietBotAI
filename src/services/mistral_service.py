import httpx
from typing import Optional, Dict
from src.config.settings import settings


class MistralService:
    """Service for interacting with Mistral AI API"""
    
    def __init__(self):
        """Initialize Mistral service"""
        self.api_key = settings.MISTRAL_API_KEY
        self.model = settings.MISTRAL_MODEL
        self.max_tokens = settings.MISTRAL_MAX_TOKENS
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
    
    async def get_diet_advice(self, question: str, user_data: Optional[Dict] = None) -> str:
        """
        Get diet advice from Mistral AI
        
        Args:
            question: User's question
            user_data: Optional user data for context (weight, height, age, goal, etc.)
        
        Returns:
            AI response text
        """
        # Build context from user data
        context = self._build_context(user_data)
        
        # Build system prompt
        system_prompt = (
            "Ты профессиональный диетолог и специалист по питанию. "
            "Твоя задача - давать краткие, точные и полезные рекомендации по питанию и диете. "
            "Отвечай на русском языке. Будь конкретным и практичным. "
            "Учитывай данные пользователя при формировании рекомендаций."
        )
        
        # Build user message
        user_message = question
        if context:
            user_message = f"{context}\n\nВопрос: {question}"
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.7
        }
        
        # Make API request
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception("Некорректный ответ от API")
        
        except httpx.TimeoutException:
            raise Exception("Превышено время ожидания ответа от сервера")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Ошибка авторизации API")
            elif e.response.status_code == 429:
                raise Exception("Превышен лимит запросов к API")
            else:
                raise Exception(f"Ошибка API: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Ошибка при обращении к ИИ: {str(e)}")
    
    def _build_context(self, user_data: Optional[Dict]) -> str:
        """
        Build context string from user data
        
        Args:
            user_data: User data dictionary
        
        Returns:
            Context string
        """
        if not user_data:
            return ""
        
        context_parts = []
        
        if user_data.get('weight'):
            context_parts.append(f"Текущий вес: {user_data['weight']} кг")
        
        if user_data.get('height'):
            context_parts.append(f"Рост: {user_data['height']} см")
        
        if user_data.get('age'):
            context_parts.append(f"Возраст: {user_data['age']} лет")
        
        if user_data.get('goal'):
            context_parts.append(f"Цель: {user_data['goal']}")
        
        if user_data.get('target_weight'):
            context_parts.append(f"Целевой вес: {user_data['target_weight']} кг")
        
        if context_parts:
            return "Данные пользователя:\n" + "\n".join(context_parts)
        
        return ""