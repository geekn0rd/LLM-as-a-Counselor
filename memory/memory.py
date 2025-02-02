import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

model_name = "Yibin-Lei/ReContriever"

huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key=os.getenv("HF_API_KEY"),
    model_name=model_name
)

client = chromadb.Client()

collection = client.create_collection(
    name="my_collection", embedding_function=huggingface_ef)
collection = client.get_collection(
    name="my_collection", embedding_function=huggingface_ef)

collection.upsert(
    ids=["id1", "id2", "id3"],
    embeddings=[huggingface_ef("doc1"), huggingface_ef(
        "doc2"), huggingface_ef("doc3")],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3",
                                                 "verse": "5"}, {"chapter": "29", "verse": "11"}],
    documents=["doc1", "doc2", "doc3"],
)

print(collection.peek(), collection.count())
