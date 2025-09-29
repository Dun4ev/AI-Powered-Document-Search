# **Заголовок:** Создаем с нуля "умный" поиск по PDF-документам: практическое руководство на Python

**Подзаголовок (Дек):** Пошаговое руководство по созданию RAG-системы для локального поиска по документам, с решением реальной проблемы очистки "грязных" данных.

**TL;DR:**
*   Построим полноценный RAG-пайплайн для семантического поиска по вашим PDF-файлам.
*   Реализуем "умный" механизм очистки документов от повторяющихся шапок и подвалов.
*   Настроим весь процесс: от извлечения текста до запуска веб-интерфейса на Streamlit.
*   Разберем типичные ошибки и способы их решения на основе реального опыта.
*   Все компоненты будут работать локально на вашем компьютере.

---

## 1. Боль, знакомая каждому: почему Ctrl+F больше не работает
**Проблема:** У вас десятки PDF-файлов — технических отчетов, договоров, инструкций. Найти в них нужную информацию — мучение. Стандартный поиск ищет только точное совпадение и не понимает контекста.

**Решение:** Мы построим систему, которая понимает *смысл* вашего запроса. Это называется семантический поиск, и в его основе лежит архитектура RAG (Retrieval-Augmented Generation).


## 2. Архитектура нашего поисковика (RAG-пайплайн)
Краткое объяснение, что такое RAG.
RAG (Retrieval-Augmented Generation) — это подход, при котором ИИ сначала ищет нужную информацию в базе документов, а потом использует её для генерации ответа. Проще: модель не «всё знает сама», а умеет быстро находить и использовать нужные куски текста из ваших файлов.

**Визуальная рекомендация:** Здесь идеально подойдет диаграмма, показывающая 6 шагов:

1.  **Ingest (Извлечение):** Читаем "сырой" текст из PDF.
2.  **Clean (Очистка):** *<-- Наш секретный ингредиент!* Удаляем повторяющиеся шапки, чтобы не "засорять" модель.
3.  **Chunk (Разбиение):** Делим текст на небольшие, осмысленные фрагменты (чанки).
4.  **Embed (Векторизация):** Превращаем каждый чанк в числовой вектор с помощью AI-модели.
5.  **Index (Индексация):** Сохраняем векторы в специальной базе данных (FAISS) для молниеносного поиска.
6.  **Search & Generate (Поиск и Генерация):** Находим по запросу самые близкие по смыслу векторы и отдаем их текстовое содержимое языковой модели (LLM) для генерации ответа.

### 2.1 Ingest + Clean
Ключ: извлечь текст и убрать повторяющиеся шапки со 2-й страницы и далее по шаблонам из `header_templates.json`.

```1:92:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/ingest.py
"""
Модуль для извлечения текста из PDF-файлов.

Функция `extract_text_from_pdfs` сканирует указанную папку, находит все
файлы с расширением .pdf, открывает их с помощью библиотеки PyMuPDF (fitz)
и извлекает текстовое содержимое со всех страниц.

Для всех страниц, кроме первой, применяется очистка от повторяющихся шапок.
Логика очистки использует шаблоны из файла `header_templates.json`.
"""
import fitz
import os
import json

def _clean_page_text(page_text: str, header_labels: list[str]) -> str:
    """
    Очищает текст одной страницы от шапки.

    Алгоритм находит последнюю строку, которая похожа на метку из шапки,
    и удаляет весь текст до этой строки, включая небольшой запас, 
    чтобы захватить строки со значениями.
    """
    lines = page_text.split('\n')
    last_header_line_index = -1

    # Находим индекс последней строки, которая начинается с одной из меток
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if any(stripped_line.startswith(label) for label in header_labels):
            last_header_line_index = i

    # Если метки шапки вообще не найдены, возвращаем исходный текст
    if last_header_line_index == -1:
        return page_text

    # Определяем, где начинается основной контент.
    # Берем индекс последней метки + небольшой запас (например, 5 строк),
    # чтобы покрыть многострочные значения и пустые строки.
    content_start_index = last_header_line_index + 5

    # Собираем очищенные строки
    cleaned_lines = lines[content_start_index:]
    
    return '\n'.join(cleaned_lines)


def extract_text_from_pdfs(folder: str) -> list[dict]:
    """
    Извлекает текст из всех PDF-файлов в папке, очищая шапки.
    """
    try:
        with open('header_templates.json', 'r', encoding='utf-8') as f:
            templates = json.load(f)
        # Используем первый шаблон из файла
        header_labels = templates['templates'][0]['header_labels']
    except FileNotFoundError:
        print("⚠️  Файл 'header_templates.json' не найден. Очистка шапок не будет производиться.")
        header_labels = []
    except (json.JSONDecodeError, IndexError, KeyError):
        print("⚠️  Ошибка чтения 'header_templates.json'. Файл поврежден или имеет неверную структуру.")
        header_labels = []


    documents = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            full_text = ""
            try:
                pdf = fitz.open(path)
                for i, page in enumerate(pdf):
                    page_text = page.get_text()
                    if i == 0 or not header_labels:
                        # Оставляем первую страницу как есть или если нет меток
                        full_text += page_text
                    else:
                        # Очищаем все последующие страницы
                        cleaned_text = _clean_page_text(page_text, header_labels)
                        full_text += cleaned_text
                pdf.close()
                documents.append({"filename": file, "text": full_text})
                print(f"✅ {file} - {len(full_text)} chars")
            except Exception as e:
                print(f"❌ Не удалось обработать файл {file}: {e}")

    return documents

if __name__ == "__main__":
    # Пример использования
    docs = extract_text_from_pdfs("pdfs")
```

### 2.2 Chunk
Разбиваем текст на перекрывающиеся чанки.

```1:25:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/chunk.py
"""
Модуль для разбиения текста документов на более мелкие части (чанки).

Функция `chunk_document` принимает документ и делит его на перекрывающиеся
фрагменты текста заданного размера. Это необходимо для того, чтобы большие
документы можно было эффективно обрабатывать и индексировать.
"""
def chunk_document(doc, size=1000, overlap=200):
    text = doc["text"]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append({"filename": doc["filename"], "text": chunk})
        start += size - overlap
    return chunks

if __name__ == "__main__":
    from .ingest import extract_text_from_pdfs
    docs = extract_text_from_pdfs("./pdfs")
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    print(f"🔹 Created {len(all_chunks)} chunks")
```

### 2.3 Embed
Создаём эмбеддинги с помощью `sentence-transformers`.

```1:23:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/embed.py
"""
Модуль для преобразования текстовых чанков в векторные представления (эмбеддинги).

Использует модель `all-MiniLM-L6-v2` из библиотеки sentence-transformers
для кодирования текстовых фрагментов в числовые векторы, которые затем
могут быть использованы для семантического поиска.
"""
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts)
    return np.array(vectors)

if __name__ == "__main__":
    import pickle
    with open("chunks.pkl", "rb") as f:
        all_chunks = pickle.load(f)
    vectors = embed_chunks(all_chunks)
    print(f"✅ Embedded shape: {vectors.shape}")
```

### 2.4 Index
Строим и сохраняем FAISS-индекс.

```1:27:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/index.py
"""
Модуль для создания и сохранения поискового индекса FAISS.

Функция `build_faiss_index` строит индекс на основе векторных представлений
текстовых чанков. Главный скрипт загружает векторы и чанки,
создает индекс и сохраняет его вместе с метаданными (чанками) на диск.
"""
import faiss
import pickle
import numpy as np

def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

if __name__ == "__main__":
    with open("vectors.npy", "rb") as f:
        vectors = np.load(f)
    with open("chunks.pkl", "rb") as f:
        all_chunks = pickle.load(f)
    index = build_faiss_index(vectors)
    faiss.write_index(index, "docs.index")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)
    print("📦 Index and metadata saved")
```

### 2.5 Search
Выполняем поиск `top_k` релевантных чанков.

```1:26:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/search.py
"""
Модуль для выполнения семантического поиска по проиндексированным документам.

Загружает предварительно созданный индекс FAISS и метаданные чанков.
Функция `search_docs` принимает текстовый запрос, кодирует его в вектор
и использует индекс для поиска `top_k` наиболее релевантных чанков.
"""
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("docs.index")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

def search_docs(query, top_k=3):
    q_vector = model.encode([query])
    distances, indices = index.search(np.array(q_vector), top_k)
    return [chunks[i] for i in indices[0]]

if __name__ == "__main__":
    results = search_docs("Explain transfer learning")
    for r in results:
        print(f"{r['filename']} :\n{r['text'][:300]}...\n")
```

### 2.6 Generate
Генерируем финальный ответ на основе найденного контекста через LLM-клиент.

```1:30:/Users/j15/Documents/Code_and_Scripts_local/AI-Powered Document Search/src/document_search/generate.py
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
```

## 3. Как это повторить: пошаговая инструкция
**Настройка окружения:**
- Установите Python 3.10+ и создайте виртуальное окружение
- Установите зависимости: `pip install -r requirements.txt`
- Поместите PDF-файлы в папку `pdfs/`

**Индексация (единым скриптом):**
- Выполните: `python scripts/run_indexing.py`
  - Скрипт пройдет 4 шага: Extract → Chunk → Embed → Index

**Запуск веб-интерфейса:**
- Выполните: `streamlit run app.py`
- Откройте `http://localhost:8501`
**Визуальная рекомендация:** Скриншот работающего веб-приложения.

## 4. Глубокое погружение: боремся с "шумом" в реальных документах
Это ключевая, практическая часть статьи.

**Проблема:** Показать пример "сырого" текста со второй страницы PDF, где видна шапка. Объяснить, почему это плохо: искажает смысл чанков, тратит драгоценный контекст LLM.

**Решение:** Рассказать о нашем подходе с настраиваемым файлом `header_templates.json`.

**Показать код:**
*   Привести содержимое `header_templates.json` и объяснить, что сюда нужно вносить только "метки" шапки.
*   Показать фрагмент кода из `src/document_search/ingest.py` (например, цикл обработки страниц), чтобы продемонстрировать, как он используется.

**Вывод:** Этот шаг показывает, как превратить "игрушечный" проект в инструмент, готовый к работе с реальными, несовершенными документами.

## 5. Что-то пошло не так? Разбор типичных проблем (Траблшутинг)
(Этот раздел основан на нашем файле `TROUBLESHOOTING.md`).

*   **Проблема 1: "Я запустил индексацию, но шапки все равно видны в поиске!"**
    *   *Решения:* Проверьте точность меток в JSON; убедитесь, что вы *перезапустили* индексацию после изменений.
*   **Проблема 2: "Из результатов поиска пропадает полезный текст с начала страниц!"**
    *   *Решения:* Проверьте, не слишком ли общие у вас метки в JSON; покажите, где в коде `ingest.py` можно изменить "запас" удаляемых строк.
*   **Проблема 3: "Ошибка про `OPENAI_API_KEY` при запуске"**
    *   *Решение:* Рассказать, как переключиться на локальную модель в `llm_client.py`.

## 6. Что дальше? Пути для улучшения
(Взять из `agents.md` "Возможные улучшения").

Кратко перечислить 3-4 идеи:
*   Переход на облачную векторную базу данных (Pinecone, Qdrant).
*   Реализация гибридного поиска (векторный + по ключевым словам).
*   Добавление re-ranking'а для повышения точности.

---
**Заключение:**
Краткий итог: "Мы не просто создали поисковик, а решили реальную проблему подготовки данных, что является 80% работы в любом AI-проекте".

**Призыв к действию (CTA):** "Если это руководство было полезным, поставьте звезду на GitHub! Если у вас есть идеи или вы нашли ошибку, создавайте issue. Удачи в ваших проектах!"

---
**Теги для Medium:**
`Python`, `Artificial Intelligence`, `LLM`, `RAG`, `Data Science`