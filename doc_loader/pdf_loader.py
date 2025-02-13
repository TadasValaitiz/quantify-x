from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from database import ChromaDB
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


db = ChromaDB()
transformer = SentenceTransformer("all-MiniLM-L6-v2")


def load_pdf(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path)
    return loader.load_and_split()


def load_document(resource: str):
    documents = load_pdf(resource)
    print(f"Loaded {len(documents)} pages")
    chunk_size = 1000
    texts = relative_text_splitter(documents, chunk_size)
    print(f"Split into {len(texts)} texts")
    for text in texts:
        embeddings = transformer.encode(text.page_content)
        collection = db.get_theory_collection()
        collection.add(
            ids=[f"{hash(text.page_content)}_{texts.index(text)}"],
            embeddings=embeddings,
            documents=text.page_content,
            metadatas={
                **text.metadata,
                "type": "book",
                "theme": "theory",
                "chunk_size": chunk_size,
                "text_index": texts.index(text),
            },
        )
    results = collection.query(
        query_texts=["out-of-sample performance"],
        n_results=3,
        where={"type": "book"},
    )
    print(f"Results: {results}")


def relative_text_splitter(
    documents: list[Document], chunk_size=1000
) -> list[Document]:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_size / 5,
        length_function=len,
        is_separator_regex=False,
    ).split_documents(documents)


def main():
    import os
    import glob

    pdf_files = glob.glob(
        os.path.join("resources", "books", "trading_strategies", "*.pdf")
    )
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}")
        load_document(pdf_file)


if __name__ == "__main__":
    main()
