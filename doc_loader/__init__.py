"""
Document loader package for processing PDF files and other documents.
"""

__all__ = ['load_documents', 'load_pdf']

# Only import if someone explicitly imports these names
def __getattr__(name):
    if name in __all__:
        from .pdf_loader import load_document, load_pdf
        return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")