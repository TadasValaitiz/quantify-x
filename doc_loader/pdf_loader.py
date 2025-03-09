from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from database import VectorDB
from doc_loader.paragraph_splitter import paragraphs_text_splitter


db = VectorDB()
transformer = SentenceTransformer("all-MiniLM-L6-v2")


def load_pdf(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path)
    return loader.load_and_split()


def load_document_semantic(resource: str, percentile: float):
    documents = load_pdf(resource)
    print(f"Loaded {len(documents)} pages")
    texts = semantic_text_splitter(documents, percentile=percentile)
    print(f"Semantic Splitter texts size:{len(texts)}")
    for text in texts:
        # print(f"Processing {text.page_content}\n")
        embeddings = transformer.encode(text.page_content)
        collection = db.get_theory_collection()
        collection.add(
            ids=f"{hash(text.page_content)}_{percentile}_{texts.index(text)}",
            embeddings=embeddings,
            documents=text.page_content,
            metadatas={
                **text.metadata,
                "type": "book",
                "theme": "theory",
                "chunk_size": percentile,
                "text_index": texts.index(text),
                "splitter": "semantic",
                "length": len(text.page_content),
            },
        )


def load_document_recursive(resource: str, chunk_size: int):
    documents = load_pdf(resource)
    print(f"Loaded {len(documents)} pages")
    texts = recursive_text_splitter(documents, chunk_size)
    print(f"Recursive Splitter texts size:{len(texts)}")
    for text in texts:
        embeddings = transformer.encode(text.page_content)
        collection = db.get_theory_collection()
        collection.add(
            ids=f"{hash(text.page_content)}_{chunk_size}_{texts.index(text)}",
            embeddings=embeddings,
            documents=text.page_content,
            metadatas={
                **text.metadata,
                "type": "book",
                "theme": "theory",
                "chunk_size": chunk_size,
                "text_index": texts.index(text),
                "splitter": "recursive",
                "length": len(text.page_content),
            },
        )


def load_document_by_paragraph(resource: str):
    texts = paragraphs_text_splitter(resource)
    print(f"Paragraph text Splitter texts size:{len(texts)}")
    for text in texts:
        embeddings = transformer.encode(text.page_content)
        collection = db.get_theory_collection()
        collection.add(
            ids=f"{hash(text.page_content)}_paragraph_{texts.index(text)}",
            embeddings=embeddings,
            documents=text.page_content,
            metadatas={
                "page": text.metadata["page"],
                "page_paragraph": text.metadata["page_paragraph"],
                "source": text.metadata["source"],
                "font": text.metadata["font"],
                "size": text.metadata["size"],
                "type": "book",
                "theme": "theory",
                "text_index": texts.index(text),
                "splitter": "paragraph",
                "length": len(text.page_content),
            },
        )


def recursive_text_splitter(
    documents: list[Document], chunk_size=1000
) -> list[Document]:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_size / 5,
        length_function=len,
        is_separator_regex=False,
    ).split_documents(documents)


def semantic_text_splitter(
    documents: list[Document], percentile: float
) -> list[Document]:
    return SemanticChunker(
        embeddings=OpenAIEmbeddings(),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=percentile,
    ).split_documents(documents)


def main():
    import os
    import glob

    pdf_files = glob.glob(
        os.path.join("resources", "books", "trading_strategies", "*.pdf")
    )

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}")
        load_document_by_paragraph(pdf_file)
        load_document_recursive(pdf_file, 1500)
        load_document_recursive(pdf_file, 500)

    print("Done")


if __name__ == "__main__":
    main()
