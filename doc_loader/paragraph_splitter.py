from typing import List, Generator
import fitz
from langchain_core.documents import Document
from pydantic import BaseModel, Field
import pymupdf


class ParagraphMetadata(BaseModel):
    """Metadata model for PDF paragraphs"""

    page: int = Field(..., description="Source page number")
    page_paragraph: int = Field(..., description="Paragraph number on the page")
    source: str = Field(..., description="PDF file path")
    bbox: tuple[float, float, float, float] = Field(
        default_factory=tuple,
        description="Paragraph bounding box coordinates (x0,y0,x1,y1)",
    )
    font: str = Field("unknown", description="Dominant font in paragraph")
    size: float = Field(0.0, description="Dominant font size in paragraph")


def extract_paragraphs(
    path: str,
) -> Generator[tuple[str, ParagraphMetadata], None, None]:
    """
    Extract paragraphs from PDF with layout preservation using PyMuPDF

    Args:
        path: Path to PDF file

    Yields:
        Tuple of (paragraph_text, metadata) for each detected paragraph
    """
    doc = pymupdf.open(path)

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)  # Get ordered text blocks
        current_para = []
        current_meta = {"fonts": {}, "sizes": {}, "bboxes": []}
        page_paragraph = 0

        def _finalize_para():
            """Helper to yield completed paragraph"""
            if not current_para:
                return

            # Calculate dominant font/size
            dominant_font = max(current_meta["fonts"], key=current_meta["fonts"].get)
            dominant_size = max(current_meta["sizes"], key=current_meta["sizes"].get)

            # Calculate merged bounding box
            x0 = min(b[0] for b in current_meta["bboxes"])
            y0 = min(b[1] for b in current_meta["bboxes"])
            x1 = max(b[2] for b in current_meta["bboxes"])
            y1 = max(b[3] for b in current_meta["bboxes"])

            nonlocal page_paragraph
            page_paragraph += 1
            yield (
                "\n".join(current_para).strip(),
                ParagraphMetadata(
                    page=page_num + 1,
                    page_paragraph=page_paragraph,
                    source=path,
                    bbox=(x0, y0, x1, y1),
                    font=dominant_font,
                    size=dominant_size,
                ),
            )

        for block in blocks:
            text = block[4].strip()
            if not text:
                continue

            # Check vertical spacing between blocks
            if current_meta["bboxes"]:
                last_bbox = current_meta["bboxes"][-1]
                spacing = block[1] - last_bbox[1]  # Current y0 - last y1
                line_height = last_bbox[3] - last_bbox[1]  # Last block height

                # Consider same paragraph if vertical spacing < 1.5x line height
                if spacing > line_height * 1.5:
                    yield from _finalize_para()
                    current_para.clear()
                    current_meta = {"fonts": {}, "sizes": {}, "bboxes": []}

            current_para.append(text)
            current_meta["bboxes"].append(block[:4])

            # Extract font information
            spans = page.get_text("dict", flags=fitz.TEXT_PRESERVE_IMAGES)["blocks"]
            for span in spans:
                if "lines" in span:
                    for line in span["lines"]:
                        for sp in line["spans"]:
                            font = sp["font"]
                            size = sp["size"]
                            current_meta["fonts"][font] = (
                                current_meta["fonts"].get(font, 0) + 1
                            )
                            current_meta["sizes"][size] = (
                                current_meta["sizes"].get(size, 0) + 1
                            )

        # Yield remaining content after page processing
        yield from _finalize_para()


def paragraphs_text_splitter(path: str) -> List[Document]:
    """
    Process PDF into LangChain Documents with paragraph preservation

    Args:
        path: Path to PDF file

    Returns:
        List of LangChain Document objects with paragraph chunks
    """
    documents = []

    for text, metadata in extract_paragraphs(path):
        documents.append(Document(page_content=text, metadata=metadata.model_dump()))

    return documents
