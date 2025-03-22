# Dora Insight

Below is a WIP Application I am working on, not all details are implemented as I am building it out. Please run at your own risk.

## Explore Your Advertising Data with Precision and Intelligence

Dora Insight is an intelligent RAG (Retrieval Augmented Generation) AI agent that allows users to explore advertising / market data through natural language queries while ensuring exact, precise metrics for business decision-making.

## 🔍 Features

- **Natural Language Queries**: Ask questions about your advertising data in plain English
- **Multi-API Integration**: Automatically queries relevant advertising APIs based on your question
- **Exact Data Retrieval**: Unlike typical RAG systems, Dora Insight provides exact values, not approximations
- **Interactive Visualizations**: Explore data through intuitive D3.js charts with drill-down capabilities
- **Scheduled Data Collection**: Periodically fetches and indexes data to reduce API dependencies
- **Context-Aware Follow-ups**: Ask follow-up questions naturally as you explore your data

## 🛠️ Technology Stack

### Frontend
- React for UI components
- D3.js for interactive data visualizations
- React Router for navigation
- Axios / MCP for API communication

### Backend
- FastAPI for high-performance API endpoints
- LLM integration for natural language understanding
- PostgreSQL for storing exact advertising / vector embeddings metrics (currently transfering from Qdrant)
- Redis for performance caching

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.9+
- Docker and Docker Compose (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dora-insight.git
cd dora-insight
```

2. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

4. Set up environment variables:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
Edit the .env files with your API keys and configuration settings.

5. Start the development environment:
```bash
docker-compose up -d  # Starts PostgreSQL, Qdrant, and Redis
cd backend
python main.py  # Starts the FastAPI server
cd ../frontend
npm start  # Starts the React development server
```

6. Open your browser to `http://localhost:3000`

## 💡 Query Examples

Dora Insight understands natural language queries such as:

- "How many ads were launched in Q3 this year?"
- "Compare Facebook and Google ad performance last month"
- "Show me underperforming campaigns across all platforms"
- "What's the trend in CPC for our video ads this quarter?"
- "Which demographics have the highest CTR in our recent campaigns?"

## 🔄 Data Flow

1. User submits a natural language query
2. LLM analyzes the query to determine intent and required data sources
3. System checks vector database for similar queries or cached results
4. If needed, precise queries are sent to the structured database for exact values
5. Results are transformed into appropriate visualizations
6. User can interact with visualizations and ask follow-up questions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please open an issue on GitHub or contact support@dora-insight.com.

---

Dora Insight - Because exact advertising metrics matter.