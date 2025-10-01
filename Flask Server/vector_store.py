import chromadb
from openai import OpenAI
import os
from typing import List, Dict
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    def create_collection(self, collection_name: str):
        """Create a new collection for a dataset"""
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            return collection
        except Exception as e:
            print(f"Error creating collection: {e}")
            return None
    
    def add_documents(self, collection_name: str, documents: List[Dict]):
        """
        Add documents to a collection
        documents format: [{"text": "content", "metadata": {...}}]
        """
        collection = self.client.get_or_create_collection(name=collection_name)
        
        for doc in documents:
            text = doc['text']
            metadata = doc.get('metadata', {})
            
            # Generate embedding
            embedding = self.get_embedding(text)
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[str(uuid.uuid4())]
            )
    
    def query_collection(self, collection_name: str, query_text: str, n_results: int = 5) -> List[Dict]:
        """Query a collection and return relevant documents"""
        try:
            collection = self.client.get_collection(name=collection_name)
            query_embedding = self.get_embedding(query_text)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error querying collection: {e}")
            return []
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            print(f"Error deleting collection: {e}")

