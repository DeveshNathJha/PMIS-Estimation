# Slide 09: Proposed Scalability Strategy
## Infrastructure prerequisites for enterprise-grade multi-user deployment

---

### Slide Content
- **Containerisation: Docker for Environment Parity:** The application and API runtimes will be packaged into Docker containers with explicit base image pinning (e.g., `python:3.11-slim`). A Docker Compose configuration will orchestrate the Streamlit frontend container, FastAPI backend container, PostgreSQL database container, and Redis queue container as an integrated, reproducible stack. This provides a direct path to cloud hosting on AWS ECS or Azure AKS.
- **State Persistence: PostgreSQL Migration:** The current system uses in-memory Streamlit `session_state` and local CSV files for all data persistence. A server restart wipes all active session data. The next infrastructure phase migrates to a managed PostgreSQL relational schema storing project records, task breakdowns, prediction history, and session tokens.
- **Asynchronous Task Processing: Celery + Redis:** Heavy computations - specifically the 500-node Monte Carlo CPM network simulations - currently block the main application thread. These will be offloaded to Celery worker processes backed by a Redis message broker. The UI submits a computation job to the queue and immediately gets a 'processing' acknowledgement, polling for results asynchronously. This preserves UI responsiveness under heavy computational load.
- **Current State: Zero Production Infrastructure:** The system runs entirely on local filesystem and in-process memory. There is no database, no queue, no container, and no persistent storage layer. All of this is Phase 3 scope - after the Phase 2 API decoupling is complete.

**Note:** Application currently runs entirely on local memory and CSV files - no persistent database, no container, no task queue. A server restart wipes all active session data.

**Key Insight:** Containerisation via Docker de-risks the cloud deployment decision entirely - whether the deployment is AWS, Azure, or on-premise, the same Docker image runs identically across all environments.

### Speaker Notes
"To eventually prepare this tool for wider access, the infrastructure strategy revolves around state persistence and decoupling. Currently, the system uses CSVs for data and local memory for state tracking - meaning a server restart wipes active sessions. The plan is to transition to PostgreSQL for relational state management. Docker containerization is proposed to enforce environment parity between local development and staging - think of it as a shipping container for software: it works identically everywhere. Offloading the computationally heavy network path calculations to asynchronous Celery workers is also required to preserve UI responsiveness - like ordering food and getting a buzzer rather than standing at the counter. All of this is Phase 3 scope, after the Phase 2 API layer is in place first."

### Possible Questions and Safe Answers
**Question:** "Are you planning to deploy this on premises or in the cloud?"
**Safe Answer:** "Deployment to cloud infrastructure, such as AWS or Azure, is planned, subject to our internal security and infrastructure alignments. Dockerizing the application ensures it remains environment-agnostic regardless of the final hosting decision."
