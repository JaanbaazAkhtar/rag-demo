import os
import openai
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from .get_embedding_function import get_embeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

PROMPT_TEMPLATE = """
**
Assume that you are a robot who has no knowledge of the world. You have been specifically trained on the {context}, to respond to questions that has answers within the context only.
But you are an expert conversationalist, who has been trained such that you give answers in the language and tone of the questions. 
Answer the users questions based on the context given below, making sure that the answers are crisp, concise and to the point.
**
**Context:** {context}
---
**User Question:** {question}
**Objective:**
1. Analyze the provided context to identify relevant information related to the user's question.
2. Generate a response that:
    * Directly addresses the user's question and maintains the language and tone used by the user.
    * If the answer is found within the context and requires a paragraph format, provide it as a paragraph.
    * If the answer is found within the context and requires a bulleted list format, provide it as a bulleted list.
    * If no relevant information is found, respond with: "I am sorry, I could not get an answer for your query, please contact your POC."
    * In cases, where it is possible to quote references from the context. Use the reference guide mentioned in the output format.

    
**Constraints:**

* Do not access or reference any information outside of the provided context.
* Do not generate responses that are not directly supported by the conversation history.
* Do not add extra information, description or details.
* Give the output strictly according to the output format given, without adding any extra details or information about the response.


**Expected Output Format**


1. The response to the user's question, formatted appropriately based on its structure (numbered list, table, or paragraph).
2. If no relevant information is found, respond with a simple string: "I am sorry, I could not get an answer for your query, please contact your POC."
3. If relevant information is found then qoute the relevant reference using  using  *[reference-number]. In the end of the response; add this [reference number] - and quote the reference. Make sure to qoute maximum of 4 most relevant refernces.
"""

# Store chat histories in a dictionary keyed by session ID
chat_histories = {}

def query_rag(session_id: str, query_text: str):
    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError(f"Database at {CHROMA_PATH} does not exist.")

    embedding_function = get_embeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Get the previous chat history for this session, if any
    history = chat_histories.get(session_id, [])

    # Add the new prompt to the chat history
    history.append({"role": "user", "content": prompt})
    
    response = openai.completions.create(model="gpt-3.5-turbo-instruct",
                                         prompt=prompt,
                                         max_tokens=1000,
                                         temperature=0.1,
                                         stream=False
    )

    response_text = response.choices[0].text.strip()

    # Add the response to the chat history
    history.append({"role": "assistant", "content": response_text})

    # Save the updated chat history
    chat_histories[session_id] = history

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    answer_without_instructions = response_text.split("\n", 1)[1].strip() if "\n" in response_text else response_text
    print(formatted_response)
    return answer_without_instructions