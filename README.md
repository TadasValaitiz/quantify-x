# Trading Strategy AI System

A RAG-based system for creating and evaluating trading strategies. Uses SQLite for structured data storage and ChromaDB for vector embeddings. Implements RAG-fusion and RAG decomposition techniques for strategy comparison and evaluation.

## Demo
Visit https://awesome-strategy-builder.streamlit.app/

## Introduction

```markdown
# Welcome to the Trading Strategy Builder

Your AI-powered assistant for developing and evaluating trading strategies.

## What You Can Do:

* **Build Trading Strategies** - Create custom strategies with specific entry/exit conditions
* **Research Technical Indicators** - Learn about indicators and how to apply them effectively
* **Evaluate Performance** - Get AI-powered feedback on your strategy's strengths and weaknesses
* **Compare with Existing Approaches** - See how your ideas stack up against established methods

Start by describing your trading idea or asking about specific indicators!
```

## Architecture

```
├── app/               # Main application code
│   ├── app.py         # Streamlit application entry point
│   ├── auth/          # Authentication functionality
│   ├── database/      # Database implementations
│   ├── services/      # Business logic services
│   ├── ui/            # UI components
├── data/              # Database binary files
├── doc_loader/        # Document processing, data preparation
├── scraper/           # Data collection, discord scraping
├── resources/         # Reference data, for data preparation
├── .streamlit/        # Streamlit configuration
├── requirements.txt   # Project dependencies
└── README.md
```

### Chains

The chatbot application uses a sophisticated chain-based architecture powered by LangChain to process user inputs and generate appropriate responses:

1. **Routing Chain**: Analyzes user input to determine the type of request (instruction, question, evaluation, or follow-up) and routes it to the appropriate specialized chain.

2. **General Message Chain**: Handles general queries that don't require specific context or specialized processing.

3. **Question with Context Chain**: Processes questions by incorporating relevant context from the vector database to provide informed answers.

4. **Trading Idea Chain**: Processes user inputs related to trading strategies, extracts structured information, and generates follow-up questions to refine the strategy.

5. **RAG Fusion Strategy Chain**: Implements Retrieval Augmented Generation with fusion techniques to retrieve and combine relevant trading strategies from the vector database, enabling more accurate and comprehensive responses.

6. **Evaluation Chain**: Analyzes and evaluates trading strategies based on various criteria, providing structured feedback and improvement suggestions.

The system uses a branching architecture that:
- Identifies the intent of user messages
- Routes requests to specialized processing chains
- Maintains conversation context across interactions
- Streams responses in real-time for better user experience
- Integrates with vector and relational databases for knowledge retrieval

## Setup

### Requirements
- Python 3.12+
- pip

### Installation
```bash
git clone git@github.com:TuringCollegeSubmissions/tvalai-AE.2.5.git
cd tvalai-AE.2.5
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Tech Stack
- LangChain for RAG architecture
- Streamlit for UI
- SQLite and ChromaDB for storage
- Discord API for data collection

