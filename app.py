"""
Основное приложение Streamlit для поиска по документам с использованием ИИ.

Это приложение предоставляет пользовательский интерфейс для ввода поискового запроса.
Оно использует функции из других модулей для выполнения поиска по документам,
генерации ответа на основе найденного контекста и отображения результата.
"""
import streamlit as st
from src.document_search.search import search_docs
from src.document_search.generate import ask

st.title("📚 AI Document Search")
query = st.text_input("Ask a question:")
if query:
    with st.spinner("Searching..."):
        top_chunks = search_docs(query)
        context = "\n\n".join([c["text"] for c in top_chunks])
        answer = ask(query, context)
        st.write("**Answer:**")
        st.write(answer)