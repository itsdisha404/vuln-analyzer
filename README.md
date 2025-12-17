# Vulnerability Analyzer

An AI-powered code vulnerability analyzer using Pinecone vector database, sentence transformers, and LLaMA.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download the LLaMA model:
- Download `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` from [HuggingFace](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
- Place in `models/` directory

3. Configure environment:
- Get your Pinecone API key from [pinecone.io](https://www.pinecone.io/)
- Update `.env` with your credentials

4. Initialize database:
```bash
python setup_pinecone.py
```

## Usage

Run the analyzer:
```bash
python main.py
```

The tool will analyze code for vulnerabilities and generate a JSON report with:
- Vulnerability type
- Severity level
- Description
- Potential impact
- Remediation steps

Reports are saved to `vulnerability_report.json`

## Architecture

- **Pinecone**: Vector database for vulnerability knowledge base
- **Sentence Transformers**: Embeddings for semantic search
- **LLaMA**: Local LLM for analysis and report generation
