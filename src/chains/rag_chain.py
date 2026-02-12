from typing import Optional, Callable

from src.retrievers.base_retriever import BaseRetriever
from src.prompts.prompt_template import PromptTemplate
from src.utils.document import Document

DEFAULT_TEMPLATE = """
    Use the following context to answer the question.
    If you cannot answer based on the context, 
    say "I don't have enough information."

    Context:
    {context}

    Question: {question}

    Answer:
"""

"""
RAGChain - Complete RAG pipeline
Combines retrieval, context formatting and LLM generation into a single easy-to-use chain
"""
class RAGChain:

    """
    Initialize the RAG chain
    Args:
        retriever: Retriever for finding documents
        llm: Function that takes a prompt string and returns a response
        prompt_template: Optional custom prompt template
        k: Number of documents to retrieve
    """
    def __init__(
        self,
        retriever: BaseRetriever,
        llm: Callable[[str], str],
        prompt_template: Optional[PromptTemplate] = None,
        k: int = 4
    ):
        self.retriever = retriever
        self.llm = llm
        self.k = k
        
        if prompt_template is None:
            self.prompt_template = PromptTemplate(
                template=DEFAULT_TEMPLATE,
                input_variables=["context", "question"]
            )
        else:
            self.prompt_template = prompt_template
    
    """
    Format retrieved documents into a context string
    Args:
        documents: List of retrieved documents
    Returns:
        Formatted context string
    """
    def format_context(
        self, documents: list[Document]
    ) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(
                f"[{i}] {doc.page_content}\n(Source: {source})"
            )
        
        return "\n\n".join(context_parts)
    
    """
    Run the full RAG pipeline
    Args:
        question: The user's question
        k: Number of documents to retrieve (uses default if None)
        filter: Optional metadata filter for retrieval
    Returns:
        The LLM's response
    """
    def invoke(
        self,
        question: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> str:
        k = k or self.k
        
        """
        Step 1: Retrieve relevant documents
        """
        documents = self.retriever.retrieve(question, k=k, filter=filter)
        
        """
        Step 2: Format context
        """
        context = self.format_context(documents)
        
        """
        Step 3: Build prompt
        """
        prompt = self.prompt_template.format(
            context=context,
            question=question
        )
        
        """
        Step 4: Generate response
        """
        response = self.llm(prompt)
        
        return response
    
    """
    Run RAG and return answer with sources
    Args:
        question: The user's question
        k: Number of documents to retrieve
        filter: Optional metadata filter
    Returns:
        Dict with 'answer' and 'sources' keys
    """
    def invoke_with_sources(
        self,
        question: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> dict:
        k = k or self.k
        
        documents = self.retriever.retrieve(question, k=k, filter=filter)
        context = self.format_context(documents)
        
        prompt = self.prompt_template.format(
            context=context,
            question=question
        )
        
        response = self.llm(prompt)
        
        sources = [
            {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            for doc in documents
        ]
        
        return {
            "answer": response,
            "sources": sources
        }
