# Regulatory Change Analyzer

An AI-powered tool for comparing regulatory documents and analyzing changes using local LLMs (Mistral via Ollama).

## Features

- **Document Comparison**: Identifies added, deleted, and modified sections between document versions
- **AI Analysis**: Provides summaries and impact assessment for each change
- **Responsive UI**: Clean React interface with Bootstrap styling
- **Local Processing**: Runs entirely on local infrastructure (no cloud dependencies)

## Technology Stack

| Component       | Technology               |
|----------------|-------------------------|
| Backend        | Python Flask            |
| Frontend       | React + Bootstrap       |
| AI Engine      | Mistral via Ollama      |
| Document Processing | difflib + hashlib |

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (with Mistral model)

### System Architecture
                                      Frontend (React) → Backend (Flask) → Ollama (Mistral)
                                                               ↓
                                                       Document Comparison

### Key Approach

1.Document Processing:

->Files are split into logical sections using heading patterns (1., 2., Section, CHAPTER)

->MD5 hashing identifies identical sections

->Uses Python's difflib for line-by-line comparison of modified sections

->Generates unified diffs for changed content

2.AI Analysis:

->Structured prompts ensure consistent JSON output:
Analyze this regulatory change and return JSON with:
- change_summary (1-sentence)
- change_type (New Requirement/Clarification/Deletion/Minor Edit)
- potential_impact (1-2 sentences)

3.Backend Architecture
->Flask API:

    -Asynchronous processing with ThreadPoolExecutor

    -Chunked file handling (16MB limit)

    -REST endpoints:

                    -POST /analyze → Initiate analysis

                    -GET /results → Poll for completion

->Error Handling:

    -Timeout management (120s for LLM calls)

    -Graceful fallbacks when Ollama is unavailable

4.Frontend Design
->React Components:

    -File upload with FormData

    -Polling mechanism for async results

    -Bootstrap-styled cards for change visualization

->User Flow:    

                            ![image alt](https://github.com/UmangSinghal0504/regulatory-change-analyzer/blob/2cf1a5d0dc06c6e5ddff421a0aeaea6b7a710a87/Screenshot%202025-06-08%20020121.png)
                                                          

5.Performance Optimizations:

->Memory Management:

    -Stream-based file processing

    -Section-wise analysis (avoids whole-document LLM calls)

->Parallelism:

    -Background thread for CPU-intensive comparisons

    -Sequential LLM calls to prevent GPU overload
    
    
### Key Innovations
->Hybrid Comparison: Combines hashing (for section matching) + difflib (for content changes)

->Local-First AI: Avoids cloud dependencies using Ollama

->Structured Outputs: Enforces consistent JSON schema from LLM



---

### Key Features:

1. **Structured Layout**: Clear sections for easy navigation
2. **Visual Elements**: Tables for tech stack and endpoints
3. **Architecture Diagram**: Simple ASCII flow diagram

                                                       
