"""
Модуль для конфигурации и предоставления клиента для языковой модели.
"""
import openai
import os

def get_llm_client_and_model():
    """
    Конфигурирует и возвращает клиент для языковой модели и имя модели
    в зависимости от переменных окружения.

    Поддерживаемые провайдеры (LLM_PROVIDER):
    - 'openai' (по умолчанию): Использует API OpenAI. Требует OPENAI_API_KEY.
    - 'local': Использует локальный сервер, совместимый с API OpenAI (например, LM Studio).

    Переменные окружения:
    - LLM_PROVIDER: 'openai' или 'local'.
    - OPENAI_API_KEY: Ключ для API OpenAI.
    - LOCAL_LLM_MODEL: Имя модели для локального сервера (например, 'openai/gpt-oss-20b').
    - LOCAL_LLM_BASE_URL: URL для локального сервера (по умолчанию 'http://localhost:1234/v1').
    """
    llm_provider = os.getenv("LLM_PROVIDER", "local").lower()

    if llm_provider == "local":
        base_url = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
        # Для LM Studio модель часто указывается в самом сервере, но мы можем передавать ее
        model_name = os.getenv("LOCAL_LLM_MODEL", "local-model") 
        client = openai.OpenAI(base_url=base_url, api_key="not-needed")
        print("🤖 Using local LLM via LM Studio")
    else: # openai
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for OpenAI provider.")
        client = openai.OpenAI(api_key=api_key)
        model_name = "gpt-4o-mini"
        print("☁️ Using OpenAI API")

    return client, model_name
