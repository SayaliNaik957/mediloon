## Architecture & Meaningful Use of Agents
Decoupling the system into specialized, autonomous agents ensures modularity and high safety standards:

*   **Separation of Concerns:** Instead of a single massive LLM call, the workflow separates conversational assistance (**OrderingAgent**) from safety auditing (**SafetyAgent**). The Safety Agent acts as an immutable supervisor; its decisions cannot be overridden by conversational prompts.
*   **Background Intelligence:** The **ForecastAgent** and **ProcurementAgent** run asynchronously. The Forecast Agent operates as a predictive model checking patient intervals, while the Procurement Agent monitors real-time database stock thresholds during transactional dispatches.

---

## 4. Clever Tool Use & Model Context Protocol (MCP) Integration
*   **Unified Tool Interface:** We implemented a custom **Model Context Protocol (MCP)** server via `FastMCP`. Rather than coding static APIs, all inventory queries, safety checkups, cart adjustments, and supplier invoice dispatch commands are registered as standardized MCP tools.
*   **Interoperability:** This design ensures that if we swap the LLM or migrate to an enterprise framework, the agents can continue using the exact same tool registry via the MCP gateway without modifying the underlying business logic.

---

## 5. Code Quality & Inline Documentation
The codebase is designed with production-grade engineering principles:

*   **Robust Exception Handling:** Local execution fallback simulators are configured inside `backend/agents/agent_system.py` to prevent crashes if API keys are missing.
*   **Verbose Log Traces:** Every tool action publishes structured terminal traces back to the frontend console, allowing developers and pharmacists to view which agent executed which tool in real-time.
*   **Extensive Code Comments:** Detailed docstrings and behavior comments are embedded across all files:
    *   `backend/database.py` — details schema creation and chronic seeding rules.
    *   `backend/mcp/tools.py` — maps exact tool parameters, stock calculations, and supplier integrations.
    *   `backend/agents/agent_system.py` — documents agent prompts, routing pipelines, and local simulation fallbacks.

---

## 6. Local Setup & Reproduction Guide
To run and verify the system locally, follow these steps:

### Prerequisites:
*   Python 3.11+
*   Node.js (for npx tools, if applicable)
*   A modern browser

### Setup & Run:
1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd KaggleProject
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  **Initialize the SQLite Database:**
    ```bash
    python backend/database.py
    ```
4.  **Boot the FastAPI Server:**
    ```bash
    python backend/app.py
    ```
5.  **Access the Application:**
    Open a browser and navigate to: `http://127.0.0.1:8000/index.html`

---

## 7. Walkthrough Video & Repository Links
*   **GitHub Repository:** [https://github.com/SayaliNaik957/mediloon/tree/main]
*   **Walkthrough Demo Video:** [https://www.youtube.com/watch?v=WWDdUkr15rI]