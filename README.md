# Emailer

A simple emailer for sending emails with vector database integration.

## Features

- Load data from SQLite source database
- Transform data to vectors using Google GenAI
- Store vectors in Weaviate target database
- Simple and readable code structure

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Configure your settings in `config.toml`:
```toml
[database]
original_path = "path/to/your/source/database.db"

[genai]
api_key = "your_google_genai_api_key"
```

3. Ensure Weaviate is running (default: http://localhost:8080)

## Usage

### Data Transformation Script

Run the main data transformation pipeline:

```bash
python store.py
```

This script will:
1. Load company data from the source SQLite database
2. Generate embeddings using Google GenAI
3. Store the vectors in Weaviate

### Components

- **`store.py`**: Main transformation script
- **`emailer/utils/settings.py`**: Configuration management
- **`emailer/store/weaviate_store.py`**: Weaviate vector database operations

## Requirements

- Python 3.11+
- Poetry for dependency management
- Google GenAI API key
- Weaviate instance running
- Source SQLite database with company data

## Project Structure

```
emailer/
├── store.py                 # Main transformation script
├── config.toml             # Configuration file
├── emailer/
│   ├── utils/
│   │   └── settings.py     # Settings management
│   └── store/
│       └── weaviate_store.py # Weaviate operations
└── pyproject.toml          # Poetry configuration
```
