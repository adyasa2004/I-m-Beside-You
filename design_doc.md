# Mom Agent — System Design Document

## Project
**Name:** Mom Agent  
**Author:** Adyasa  
**University:** IIT Guwahati  
**Department:** <Your Dept>

## 1. Overview
Mom Agent is a persona-driven AI assistant for students that:
- Generates concise lecture notes (5 bullets).
- Generates 5 short quiz questions with answers.
- Provides wellness reminders (meals, water).
- Demonstrates a multi-agent architecture: Planner + Executor.

## 2. Core Features (mapped to assignment)
- **Reasoning & Planning:** `PlannerAgent` produces a stepwise plan for each user input (e.g., "Summarize" then "Create Quiz").
- **Execution:** `ExecutorAgent` runs the plan by invoking LLM prompts for notes and quiz generation.
- **UI:** Streamlit web app (`app.py`) with input, results, reminders, and logs.
- **Interaction Logs:** All LLM interactions are saved to `logs.txt` in JSONL format.

## 3. Architecture
- **Frontend/UI:** Streamlit (single-page web app).
- **Agent layer:** `agent.py` containing Planner + Executor and reminder helpers.
- **LLM:** OpenAI ChatCompletion endpoint (model used: `gpt-4o-mini`).
- **Storage:** `logs.txt` (JSONL) for interaction logs; repository for source code and design doc.

(Insert simple architecture diagram if required.)

## 4. Data Flow
1. User inputs text or uploads PDF.
2. UI sends text to PlannerAgent -> gets plan (JSON).
3. ExecutorAgent executes each step -> calls LLM -> returns notes/quiz.
4. Each prompt/response written to `logs.txt`.
5. UI displays outputs and shows logs.

## 5. Tech choices & rationale
- **Python + Streamlit:** Rapid prototyping and clean UI in minimal code.
- **OpenAI LLM:** High-quality text generation for summarization & quizzes.
- **PyPDF2:** Lightweight PDF text extraction for demo.
- **JSONL logs:** Simple, shareable, and satisfies deliverable requirements.

## 6. Optional / Future improvements
- Real scheduling with background workers (Celery/Redis or APScheduler hosted).
- Push notifications or OS-level notifications.
- Adding RAG (retrieve & generate) to include course slides & external materials.
- UI for editing / approving generated plans before execution.

## 7. Deliverables
- `agent.py`, `app.py`, `design_doc.md`, `README.md`, `logs.txt`.
- Demo screenshots/video (optional).

## 8. Reproducibility / How to run
1. Clone repo
2. Create venv and install `pip install -r requirements.txt`
3. Set `OPENAI_API_KEY` environment variable
4. Run `streamlit run app.py`

