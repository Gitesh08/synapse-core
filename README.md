# Project Synapse | The AI Memory Engine

**Scale your AI memory without the noise. Project Synapse brings dynamic context pruning and neural plasticity to your data infrastructure.**

This repository is a full-stack monorepo combining a high-performance Python (FastAPI) cognitive backend powered by Cognee with a minimalist Next.js frontend (Linear-style UI).

## Project Structure

- `apps/frontend`: Next.js App Router providing a highly responsive, Linear-inspired UI.
- `apps/backend`: FastAPI integration with Cognee for advanced context retrieval and cognitive architecture.
- `packages/shared`: Shared types and business logic.

## Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://python.org/) (3.10+)
- [Docker](https://www.docker.com/) (Optional, for containerized deployment)

### 1. Environment Setup

Copy the example environment configuration at the root level:
```bash
cp .env.example .env
```

### 2. Running Locally

**Backend**
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
*The API will be available at http://localhost:8000*

**Frontend**
```bash
cd apps/frontend
npm install
npm run dev
```
*The Web UI will be available at http://localhost:3000*

### 3. Running via Docker

To bring up the entire stack seamlessly:
```bash
docker-compose up --build
```

## License
MIT
