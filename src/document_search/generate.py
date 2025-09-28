"""
Модуль для генерации ответов на вопросы с использованием языковой модели.
Использует llm_client для получения настроенного клиента и модели.
"""
from .llm_client import get_llm_client_and_model

# Получаем клиент и имя модели при загрузке модуля
client, model_name = get_llm_client_and_model()

def ask(question, context):
    prompt = f"""
Context:
{context}
Question: {question}
Answer in a short paragraph.
"""
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    from .search import search_docs
    question = "Explain transfer learning"
    top_chunks = search_docs(question)
    context = "\n\n".join([c["text"] for c in top_chunks])
    answer = ask(question, context)
    print("💡 Answer:", answer)