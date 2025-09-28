"""
Скрипт для выполнения полного цикла индексации документов.

Этот скрипт объединяет все шаги, необходимые для обработки PDF-файлов
и создания поискового индекса:
1. Извлечение текста из PDF-файлов в указанной папке.
2. Разбиение извлеченного текста на чанки.
3. Преобразование текстовых чанков в векторные эмбеддинги.
4. Построение и сохранение индекса FAISS для быстрого поиска.
5. Сохранение метаданных (чанков) для сопоставления с результатами поиска.

Для запуска необходимо поместить PDF-файлы в папку 'pdfs' и выполнить:
`python run_indexing.py`
"""
import os
import pickle
import faiss
import numpy as np
import sys

# Добавляем корневую папку проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.document_search.ingest import extract_text_from_pdfs
from src.document_search.chunk import chunk_document
from src.document_search.embed import embed_chunks
from src.document_search.index import build_faiss_index

PDFS_FOLDER = "pdfs"
CHUNKS_FILE = "chunks.pkl"
INDEX_FILE = "docs.index"

def main():
    """Основная функция для запуска процесса индексации."""
    print("🚀 Starting indexing process...")

    # Проверяем, существует ли папка pdfs и есть ли в ней файлы
    if not os.path.isdir(PDFS_FOLDER) or not os.listdir(PDFS_FOLDER):
        print(f"❌ Error: The '{PDFS_FOLDER}' folder does not exist or is empty.")
        print("Please create it and add your PDF files.")
        # Создаем папку, если она не существует
        if not os.path.isdir(PDFS_FOLDER):
            os.makedirs(PDFS_FOLDER)
            print(f"📁 Created '{PDFS_FOLDER}' directory.")
        return

    # 1. Извлечение текста из PDF
    print("\n[Step 1/4] Extracting text from PDFs...")
    docs = extract_text_from_pdfs(PDFS_FOLDER)
    if not docs:
        print("No PDF documents found. Exiting.")
        return
    print(f"✅ Found {len(docs)} documents.")

    # 2. Разбиение на чанки
    print("\n[Step 2/4] Chunking documents...")
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    print(f"✅ Created {len(all_chunks)} chunks.")

    # 3. Создание эмбеддингов
    print("\n[Step 3/4] Embedding chunks...")
    vectors = embed_chunks(all_chunks)
    print(f"✅ Created embeddings with shape: {vectors.shape}")

    # 4. Построение и сохранение индекса и чанков
    print("\n[Step 4/4] Building and saving index...")
    index = build_faiss_index(vectors)
    
    # Сохраняем индекс FAISS
    faiss.write_index(index, INDEX_FILE)
    print(f"💾 Index saved to '{INDEX_FILE}'")
    
    # Сохраняем чанки, так как они нужны для отображения результатов поиска
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(all_chunks, f)
    print(f"💾 Chunks saved to '{CHUNKS_FILE}'")

    print("\n🎉 Indexing complete! The application is ready to search.")

if __name__ == "__main__":
    main()
