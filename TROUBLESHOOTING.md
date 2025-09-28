# Устранение неполадок

## Ошибка: `ValueError: OPENAI_API_KEY environment variable not set`

### Проблема

При запуске приложения возникала следующая ошибка:

```
ValueError: OPENAI_API_KEY environment variable not set for OpenAI provider.
```

Это происходило потому, что приложение по умолчанию пыталось использовать API от OpenAI, для которого требуется ключ `OPENAI_API_KEY`. Однако, целью была работа с локальной языковой моделью.

### Решение

Проблема была решена изменением провайдера по умолчанию с `"openai"` на `"local"` в файле `src/document_search/llm_client.py`.

**Изменение в коде:**

Была изменена строка:
```python
llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
```
на:
```python
llm_provider = os.getenv("LLM_PROVIDER", "local").lower()
```

Это изменение гарантирует, что приложение по умолчанию использует локальный сервер, совместимый с API OpenAI (например, LM Studio), и не требует наличия ключа `OPENAI_API_KEY` для запуска в режиме локальной разработки.
