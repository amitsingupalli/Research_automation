# Autonomous AI Research Agent

Hey there! Welcome to the **Research Automation** project. This project is built to handle topic research without having to dig through multiple browser tabs manually. It uses an AI multi-agent setup powered by **CrewAI**, **Groq LLM (LLaMA 3.3)**, and **Serper API** to gather web results, process information, and present well-organized summaries.

---

## 🌟 How It Works

The system operates with two specialized AI agents:

1. **Research Analyst**: Searches the web for current, accurate information on your requested topic and filters out unnecessary noise.
2. **Content Writer**: Takes raw research findings, organizes the insights clearly under structured categories or genres, and puts all source links in a neat `Sources & References` section at the end.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/amitsingupalli/Research_automation.git
cd Research_automation
```

### 2. Set Up a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables Setup

To keep your credentials safe, API keys are loaded via a local `.env` file that is excluded from version control.

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your API credentials:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

> ⚠️ **Important Security Note**: Never push your actual `.env` file or hardcode secret keys into the codebase.

---

## 💻 Running the Application

### Option A: Web Interface (Streamlit)
Launch the interactive web UI:
```bash
streamlit run app.py
```

### Option B: Terminal CLI Mode
Run directly in your command line:
```bash
python crew_research.py
```

---

## 🛠 Tech Stack

- **Framework**: CrewAI
- **LLM Engine**: Groq (LLaMA 3.3 / LLaMA 3.1)
- **Web Search**: SerperDevTool
- **Frontend**: Streamlit
- **Environment Management**: python-dotenv

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
