import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask(question, context):
    prompt = f"""
Context:
{context}
Question: {question}
Answer in a short paragraph.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

if __name__ == "__main__":
    from search import search_docs
    question = "Explain transfer learning"
    top_chunks = search_docs(question)
    context = "\n\n".join([c["text"] for c in top_chunks])
    answer = ask(question, context)
    print("💡 Answer:", answer)
