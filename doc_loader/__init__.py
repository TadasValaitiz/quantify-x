"""
Document loader package for processing PDF files and other documents.
"""

from .pdf_loader import load_document_recursive, load_document_semantic

__all__ = ["load_document_recursive", "load_document_semantic"]
