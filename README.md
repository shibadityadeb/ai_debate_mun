# Diplomatrix AI: Multi-Agent Diplomatic Debate Orchestrator

> An intelligent debate simulation platform powered by orchestrated AI agents. Watch diplomatic discussions unfold as autonomous agents negotiate and debate real-world topics with strategic reasoning.

---

## 🎯 Overview

Diplomatrix AI is a sophisticated **multi-agent orchestration system** that simulates realistic diplomatic debates. Five independent country agents represent different nations, while a moderator agent synthesizes positions and a judge agent scores arguments. The entire debate flow is orchestrated through a state driven system that manages agent coordination, message streaming, and real time UI updates.

### Agent Orchestra Architecture

```
                        ┌─────────────────────────┐
                        │   Orchestrator Engine   │
                        │  (Debate Flow Manager)  │
                        └──────────────┬──────────┘
                                       │
        ┌──────────────┬───────────────┼──────────────┬──────────────┐
        │              │               │              │              │
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │Country1│    │Country2│    │Country3│    │Country4│    │Country5│
    │ Agent  │    │ Agent  │    │ Agent  │    │ Agent  │    │ Agent  │
    └────┬───┘    └────┬───┘    └────┬───┘    └────┬───┘    └────┬───┘
         │             │             │             │             │
         └─────────────┼─────────────┼─────────────┼─────────────┘
                       │             │             │
                  ┌────▼─────────────▼─────────────▼────┐
                  │    Moderator Agent                  │
                  │ (Synthesize & Find Common Ground)   │
                  └────┬──────────────────────────┬─────┘
                       │                          │
                  ┌────▼──────────────────────────▼────┐
                  │    Judge Agent                     │
                  │ (Score & Declare Winner)           │
                  └────────────────────────────────────┘
```

---

## 🌐 Quick Deploy

Deploy to production in minutes:

- **Backend**: Render (FastAPI)
- **Frontend**: Vercel (React)


For local setup: `chmod +x setup.sh && ./setup.sh`

---

## ✨ Features

### AI Agents Orchestration
- **5 Autonomous Country Agents**: Each delegates independently crafts diplomatic positions with strategic stances. Token-optimized responses (60-word constraint) ensure cost efficiency.
- **1 Moderator Agent**: Synthesizes all country positions, identifies common ground, and maintains diplomatic discourse.
- **1 Judge Agent**: Evaluates debate quality, scores arguments (0-10 scale), and determines the winning delegation.
- **Debate Flow Management**: Orchestrator coordinates 5 debate phases—opening statements → rebuttal rounds → resolution → voting → judging.

### Real-Time Features
- Live message streaming with phase transitions
- Dynamic participant status tracking (waiting → speaking → active)
- Real-time verdict extraction and winner highlighting
- Responsive debate feed with internal scrolling

### Architecture
- Message-driven state management
- Async/await pipeline for concurrent agent execution
- Context injection via ChromaDB retriever
- Type-safe debate schema with Pydantic

---

## 🏗️ System Architecture

### Backend Stack
- **Framework**: FastAPI (async Python)
- **LLM Integration**: Anthropic Claude API via custom LLM client
- **Knowledge Base**: ChromaDB for vector storage + Retriever for context injection
- **State Management**: Debate orchestrator with round manager
- **Agent System**: Base agent class with specialized implementations (CountryAgent, ModeratorAgent, JudgeAgent)

### Frontend Stack
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS with custom utility classes
- **Animation**: Framer Motion for phase transitions
- **Icons**: Lucide React
- **Components**: Modular, reusable components with glass-morphism design

### Debate Flow

```
1️⃣  OPENING ROUND
    └─ All 5 country agents deliver opening statements
    └─ Each response: max 60 words, 2-3 sentences

2️⃣  REBUTTAL ROUND 1
    └─ Countries respond to opposing arguments
    └─ Moderator synthesizes positions

3️⃣  REBUTTAL ROUND 2
    └─ Final counterarguments and clarifications
    └─ Moderator updates synthesis

4️⃣  RESOLUTION
    └─ Closing statements and final positions
    └─ Moderator provides final analysis

5️⃣  VOTING & JUDGING
    └─ Judge evaluates all arguments
    └─ Judge returns: winner, scores, reasoning
    └─ UI displays winner with score bars
```

## 📚 Documentation

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation with examples
- **[LICENSE](./LICENSE)** - MIT License

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Anthropic API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL in .env
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Run Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then visit `http://localhost:5173` to start a debate.

---

## 📡 API Usage

Start a debate and stream all agent responses via Server-Sent Events:

**Endpoint**: `POST /api/debate/run`

**Quick Example**:
```bash
curl -X POST http://localhost:8000/api/debate/run \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should AI development be regulated globally?",
    "countries": ["USA", "China", "India", "EU", "Brazil"]
  }'
```

**Response** (streaming): Each agent message arrives as an event:
```json
{
  "phase": "opening",
  "speaker": "USA",
  "message": "We believe thought-provoking regulation is essential...",
  "timestamp": "2026-03-22T10:30:00Z"
}
```

**For complete API documentation** including JavaScript, Python examples, error handling, and all endpoints → See [API_REFERENCE.md](./API_REFERENCE.md)

---

## 📁 Project Structure

```
ai_debate_mun/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI Agent implementations
│   │   │   ├── base_agent.py    # Abstract base class
│   │   │   ├── country_agent.py # Country delegate logic
│   │   │   ├── moderator_agent.py
│   │   │   └── judge_agent.py
│   │   ├── core/
│   │   │   ├── orchestrator.py  # Main debate orchestrator
│   │   │   ├── round_manager.py # Phase management
│   │   │   └── config.py
│   │   ├── llm/
│   │   │   └── llm_client.py    # LLM API wrapper
│   │   ├── mcp/
│   │   │   ├── retriever.py     # Context retrieval
│   │   │   ├── embedder.py
│   │   │   └── vector_store.py
│   │   ├── memory/
│   │   │   ├── context_builder.py
│   │   │   └── state_store.py
│   │   ├── routes/
│   │   │   └── debate.py        # API endpoints
│   │   └── main.py              # FastAPI app
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/          # React components
    │   │   ├── Dashboard.jsx    # Main orchestration UI
    │   │   ├── DebateFeed.jsx   # Message stream display
    │   │   ├── InsightPanel.jsx # Judge verdicts
    │   │   └── ...
    │   ├── pages/
    │   └── Landing.jsx
    └── package.json
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` in `backend/` folder:

```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
CHROMA_DB_PATH=./chroma_data
DEBUG=false
```

---

## 🧠 How Agents Work

### Country Agent
Each country agent maintains:
- **Stance**: Initial position on the topic
- **Memory**: Previous arguments and rebuttals
- **Brief**: Context from knowledge base

The agent synthesizes a response in **max 60 words** to minimize token costs while maintaining diplomatic substance.

### Moderator Agent
After each round, the moderator:
1. Reads all country positions
2. Identifies points of agreement
3. Highlights areas of contention
4. Suggests compromises or paths forward

### Judge Agent
The judge evaluates:
- **Logic Score** (0-10): Quality of argumentation
- **Evidence** (0-10): How well-supported is the position
- **Diplomacy** (0-10): Respectfulness and cooperation tone
- **Winner**: Highest average score

---

## 📊 Performance & Optimization

- **Token Efficiency**: Country agents limited to 60 words per response (~180 tokens)
- **Concurrent Execution**: FastAPI async handles multiple agents in parallel
- **Context Injection**: ChromaDB retriever provides relevant background per agent
- **UI Stability**: Fixed container heights prevent layout shifting

---

## 🛠️ Development

### Run Tests

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python tests/test_country_agent.py
```

### Hot Reload

Both backend and frontend support hot reload during development:
- Backend: Uvicorn `--reload` flag
- Frontend: Vite HMR enabled by default

---

## 📝 License

MIT License © 2026 - See [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Support for > 5 country agents
- Custom debate formats (parliamentary, informal)
- Persistence layer for debate logs
- Advanced analytics dashboard
- Model fine-tuning for diplomatic language

---

> **Built with precision orchestration for authentic diplomatic simulations.**
