from langchain_openai import OpenAIEmbeddings
import os

def get_embeddings():
    print("Info:- Creating Embeddings.")
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return embeddings
