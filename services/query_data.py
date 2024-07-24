from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from utils.get_embedding_function import get_embedding_function
import json

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="llama3.1")

    response_text = ""
    sources = [{"id": doc.metadata.get("id", None), "score": score} for doc, score in results]

    for chunk in model.stream(prompt):
        response_text += chunk
        formatted_response = {
            "response": response_text,
            "sources": sources,
            "context": context_text
        }
        yield f"data: {json.dumps(formatted_response)}\n\n"

    final_response = {
        "response": response_text,
        "sources": sources,
        "context": context_text
    }
    yield f"data: {json.dumps(final_response)}\n\n"
