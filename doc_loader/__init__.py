"""
Document loader package for processing PDF files and other documents.
"""

__all__ = ["load_document_recursive", "load_document_semantic"]

from .pdf_loader import load_document_recursive, load_document_semantic
