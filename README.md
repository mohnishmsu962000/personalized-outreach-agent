# Personalized Outreach Agent

AI-powered agent that generates personalized outreach messages for researchers using structured data and LLM prompt pipelines.

## What it does

Takes structured researcher data (name, institution, article, research signals) and generates a high-quality 3-sentence personalized outreach message tailored to the contact channel (email or LinkedIn).

- $0.09 per 1000 messages using GPT-4o-mini
- Channel-aware tone (formal for email, conversational for LinkedIn)
- Batch generation with cost tracking
- Cost estimation before running a batch

## Architecture
```
Structured researcher data (JSON)
        ↓
Pydantic validation
        ↓
Jinja2 channel-aware prompt template (email / linkedin)
        ↓
OpenAI GPT-4o-mini (with retry logic)
        ↓
Structured JSON response (message + tokens + cost)
```

## Tech Stack

- **FastAPI** — API framework
- **Pydantic v2** — input/output validation
- **Jinja2** — prompt templating
- **OpenAI GPT-4o-mini** — LLM
- **Tenacity** — retry logic with exponential backoff
- **SlowAPI** — rate limiting
- **Structlog** — structured JSON logging
- **Docker** — containerization

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/outreach/generate` | Generate message for a single researcher |
| POST | `/outreach/generate/batch` | Generate messages for up to 50 researchers |
| GET | `/outreach/cost-estimate` | Estimate cost before running a batch |
| GET | `/health` | Health check |

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/personalized-outreach-agent.git
cd personalized-outreach-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -e ".[dev]"
```

### 4. Configure environment
```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open Swagger docs
```
http://localhost:8000/docs
```

## Sample Request
```json
{
  "name": "Dr. Sarah Chen",
  "institution": "Stanford University",
  "article_title": "Metabolic Adaptation in Long-Term Caloric Restriction",
  "article_summary": "Explores how metabolism adapts during prolonged caloric restriction and its implications for longevity and healthspan",
  "research_signals": "longevity, metabolic health, caloric restriction",
  "channel": "email"
}
```

## Sample Response
```json
{
  "researcher_name": "Dr. Sarah Chen",
  "channel": "email",
  "message": "Dear Dr. Chen, your groundbreaking work at Stanford University on metabolic adaptation during long-term caloric restriction has profound implications for our understanding of longevity and healthspan...",
  "tokens_used": 402,
  "cost_usd": 0.000104
}
```

## Cost Efficiency

| Volume | Estimated Cost |
|--------|---------------|
| 100 messages | $0.009 |
| 1,000 messages | $0.09 |
| 10,000 messages | $0.90 |

## Running with Docker
```bash
docker-compose up --build
```

## Sample Data

See `data/sample_researchers.json` for example researcher profiles to test with.

## Project Structure
```
app/
├── config.py          # Settings and environment config
├── main.py            # FastAPI app entry point
├── schemas/
│   └── outreach.py    # Pydantic input/output models
├── services/
│   ├── generator.py   # Core LLM generation logic
│   └── cost.py        # Token cost calculation
├── prompts/
│   ├── email.j2       # Email prompt template
│   └── linkedin.j2    # LinkedIn prompt template
└── routers/
    └── outreach.py    # API route handlers
```