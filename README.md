# Trading Strategy AI System

A RAG-based system for creating and evaluating trading strategies. Uses SQLite for structured data storage and ChromaDB for vector embeddings. Implements RAG-fusion and RAG decomposition techniques for strategy comparison and evaluation.

## Architecture

```
├── database/          # Database implementations
│   ├── database.py    # SQLite implementation
│   └── vector_db.py   # ChromaDB implementation
├── doc_loader/        # Document processing
├── scraper/           # Data collection
├── resources/         # Reference data
├── shared/            # Shared utilities
├── frontend/          # Streamlit UI
├── requirements.txt
└── README.md
```

## Components

### Frontend
- Streamlit interface for strategy creation and evaluation
- Displays comparison results and component-level feedback

### Data Layer
- **SQLite**: Stores structured strategy data and metadata
- **ChromaDB**: Vector store supporting RAG operations
  - Enables fusion-based retrieval across strategy components
  - Supports decomposition for component-level analysis

## Setup

### Requirements
- Python 3.10+
- pip

### Installation
```bash
git clone https://github.com/yourusername/tvalai-AE.2.5.git
cd tvalai-AE.2.5
pip install -r requirements.txt
streamlit run frontend/app.py
```

## Tech Stack
- LangChain for RAG architecture
- Streamlit for UI
- SQLite and ChromaDB for storage
- Discord API for data collection

