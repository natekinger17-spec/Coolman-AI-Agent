# Coolman Fuels AI Agent 🔥

An intelligent customer support agent for Coolman Fuels, powered by AI to answer questions about fuel delivery, propane services, tank installations, and more.

## 🚀 Features

- **24/7 AI Support**: Answers customer questions instantly
- **Comprehensive Knowledge**: Knows all about Coolman Fuels products, services, and coverage areas
- **Session Management**: Maintains conversation context for natural interactions
- **Modern Chat Interface**: Beautiful, responsive web widget

## 📋 Services Covered

- ✅ Fuel delivery (heating oil, diesel, furnace oil)
- ✅ Propane delivery & tank sales
- ✅ Cardlock fuel access (24/7)
- ✅ Into-equipment fueling
- ✅ Tank inspections & installations
- ✅ Emergency delivery services
- ✅ Fleet card acceptance (Petro-Pass, BVD, Comdata, EFS)

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python)
- **AI Model**: GPT-4.1-mini via GitHub Models
- **Agent Framework**: Microsoft Agent Framework for Azure AI
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Render.com

## 🏗️ Setup Instructions

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token with `model` permissions ([Get one here](https://github.com/settings/tokens))

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/natekinger17-spec/Coolman-AI-Agent.git
   cd Coolman-AI-Agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt --pre
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your GitHub token: `GITHUB_TOKEN=ghp_your_token_here`

5. **Run the server**:
   ```bash
   python -m uvicorn web_api:app --reload
   ```

6. **Open the chat widget**:
   - Open `chat_widget.html` in your browser
   - Start chatting with the AI agent!

## 🌐 Deployment

### Deploy to Render

1. **Push code to GitHub** (already done)

2. **Create Render Web Service**:
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect to this GitHub repository
   - Render will auto-detect settings from `render.yaml`

3. **Add Environment Variable**:
   - In Render dashboard, go to "Environment"
   - Add: `GITHUB_TOKEN` = your GitHub token

4. **Deploy**:
   - Render will build and deploy automatically
   - Get your public URL (e.g., `https://coolman-ai-agent.onrender.com`)

5. **Update Chat Widget**:
   - Edit `chat_widget.html` line ~295
   - Change `API_URL` to your Render URL
   - Upload to your website

## 📁 Project Structure

```
coolman-fuels-agent/
├── coolman_agent.py      # AI agent logic & knowledge base
├── web_api.py            # FastAPI server with endpoints
├── chat_widget.html      # Frontend chat interface
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔌 API Endpoints

### `POST /session/new`
Create a new chat session.

**Response**:
```json
{
  "session_id": "abc123..."
}
```

### `POST /chat`
Send a message and get a response.

**Request**:
```json
{
  "message": "What fuels do you deliver?",
  "session_id": "abc123..."  // optional
}
```

**Response**:
```json
{
  "response": "We deliver heating oil, diesel...",
  "session_id": "abc123..."
}
```

### `GET /health`
Check service health status.

**Response**:
```json
{
  "status": "healthy",
  "agent_ready": true,
  "active_sessions": 5,
  "service": "Coolman Fuels AI Agent"
}
```

## 📞 Contact Information

**Coolman Fuels**
- Phone: [519-235-0853](tel:+15192350853)
- Email: [sales@coolmanfuels.ca](mailto:sales@coolmanfuels.ca)
- Website: [www.coolmanfuels.ca](https://www.coolmanfuels.ca)

## 📝 License

Proprietary - Coolman Fuels © 2025

## 🤝 Support

For technical issues or questions about the AI agent, please contact the development team or call Coolman Fuels directly.

---

**Built with ❤️ for Coolman Fuels customers**
