"""
RAG from Scratch - Python Implementation

A comprehensive library for building Retrieval-Augmented Generation systems.
"""

from src.utils.document import Document
from src.embeddings import EmbeddingModel, EmbeddingCache
from src.vector_stores import InMemoryVectorStore
from src.loaders import TextLoader, PDFLoader, DirectoryLoader
from src.text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from src.retrievers import VectorStoreRetriever
from src.chains import RAGChain
from src.prompts import PromptTemplate

__version__ = "0.1.0"

__all__ = [
    "Document",
    "EmbeddingModel",
    "EmbeddingCache",
    "InMemoryVectorStore",
    "TextLoader",
    "PDFLoader",
    "DirectoryLoader",
    "CharacterTextSplitter",
    "RecursiveCharacterTextSplitter",
    "VectorStoreRetriever",
    "RAGChain",
    "PromptTemplate",
]
