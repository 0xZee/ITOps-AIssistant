import os
import cohere
import groq
import numpy as np
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class RAGEngine:
    def __init__(self, pdf_content, groq_api_key, cohere_api_key):
        """
        Initialize the RAG engine
        
        Args:
            pdf_content (list): List of strings containing the text content of each page
            groq_api_key (str): Groq API key
            cohere_api_key (str): Cohere API key
        """
        # Set API keys
        self.groq_api_key = groq_api_key
        self.cohere_api_key = cohere_api_key
        
        # Initialize clients
        self.groq_client = groq.Groq(api_key=groq_api_key)
        self.cohere_client = cohere.Client(api_key=cohere_api_key)
        
        # MongoDB connection
        mongodb_uri = os.environ.get("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
            
        self.mongodb_client = MongoClient(mongodb_uri)
        self.db_name = "pdf_chat_db"
        self.collection_name = "document_embeddings"
        self.db = self.mongodb_client[self.db_name]
        self.collection = self.db[self.collection_name]
        
        # Clear existing documents in the collection for this session
        self.collection.delete_many({})
        
        self.embedding_dim = 1024  # Default embedding dimension for Cohere
        
        # Process and store documents
        documents = self._process_documents(pdf_content)
        self.store_documents(documents)
    
    def _process_documents(self, pdf_content):
        """
        Process the PDF content into document chunks
        
        Args:
            pdf_content (list): List of strings containing the text content of each page
            
        Returns:
            list: List of Document objects
        """
        # Join all pages into a single text
        full_text = "\n".join(pdf_content)
        
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )
        
        # Create document chunks
        chunks = text_splitter.split_text(full_text)
        
        # Convert to Document objects
        documents = [Document(page_content=chunk) for chunk in chunks]
        
        return documents
    
    def _generate_embeddings(self, text):
        """
        Generate embeddings for text using Cohere
        
        Args:
            text (str): Text to generate embeddings for
            
        Returns:
            list: Embedding vector
        """
        response = self.cohere_client.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        
        return response.embeddings[0]
    
    def store_documents(self, documents):
        """
        Store documents with embeddings in our MongoDB document store
        
        Args:
            documents (list): List of Document objects
        """
        # Process each document
        for i, doc in enumerate(documents):
            # Generate embeddings
            embedding = self._generate_embeddings(doc.page_content)
            
            # Store document with embedding in MongoDB collection
            self.collection.insert_one({
                "content": doc.page_content,
                "embedding": embedding,
                "id": i
            })
    
    def _get_relevant_documents(self, question, k=3):
        """
        Get relevant documents for a question using vector similarity
        
        Args:
            question (str): Question to find relevant documents for
            k (int): Number of documents to return
            
        Returns:
            list: List of relevant document texts
        """
        # Generate embedding for the question
        question_embedding = self._generate_embeddings(question)
        
        # Find similar documents
        similar_docs = []
        
        # Get all documents from MongoDB
        all_docs = list(self.collection.find({}))
        
        # Calculate similarity scores
        for doc in all_docs:
            content = doc["content"]
            embedding = doc["embedding"]
            
            # Calculate similarity
            similarity = self._calculate_similarity(question_embedding, embedding)
            
            similar_docs.append((content, similarity))
        
        # Sort by similarity (highest first)
        similar_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k document texts
        return [doc[0] for doc in similar_docs[:k]]
    
    def _calculate_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1 (list): First vector
            vec2 (list): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        # Avoid division by zero
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0
        
        return dot_product / (norm_vec1 * norm_vec2)
    
    def query(self, question):
        """
        Query the RAG engine
        
        Args:
            question (str): Question to ask
            
        Returns:
            generator: Stream of response tokens
        """
        # Get relevant documents
        relevant_docs = self._get_relevant_documents(question)
        
        # Combine relevant documents with the question
        context = "\n\n".join(relevant_docs)
        
        # Create the prompt
        system_prompt = """You are a helpful PDF assistant. Use the provided context to answer the user's question. 
        If the answer is not in the context, say "I don't have enough information to answer that question based on the PDF content."
        Always cite the specific parts of the document you used to formulate your answer."""
        
        prompt = f"""Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        # Generate streaming response using Groq
        stream = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=True
        )
        
        return stream
