import streamlit as st
from search import search_docs
from generate import ask

st.title("📚 AI Document Search")
query = st.text_input("Ask a question:")
if query:
    with st.spinner("Searching..."):
        top_chunks = search_docs(query)
        context = "\n\n".join([c["text"] for c in top_chunks])
        answer = ask(query, context)
        st.write("**Answer:**")
        st.write(answer)
