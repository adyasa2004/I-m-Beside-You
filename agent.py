# agent.py
import os
import time
from datetime import datetime
import json

# Optional OpenAI import
try:
    import openai
except ImportError:
    openai = None

from plyer import notification

# -------------------- Configuration --------------------
USE_MOCK = True  # Set True to run without hitting OpenAI API

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not USE_MOCK:
    if not OPENAI_API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY environment variable before running.")
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

LOGFILE = "logs.txt"

# -------------------- Logging --------------------
def log_interaction(entry: dict):
    """Append JSON lines to logs.txt safely."""
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except UnicodeEncodeError:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            json_str = json.dumps(entry, ensure_ascii=False, default=lambda o: str(o))
            json_str = json_str.encode('utf-8', 'surrogatepass').decode('utf-8', 'replace')
            f.write(json_str + "\n")

# -------------------- Planner --------------------
class PlannerAgent:
    def __init__(self, persona="Mom Agent"):
        self.persona = persona

    def plan_study_task(self, user_prompt: str):
        if USE_MOCK:
            plan = [
                {"id": 1, "name": "Summarize", "desc": "Create short notes (mocked)."},
                {"id": 2, "name": "Create Quiz", "desc": "Generate 5 short quiz questions (mocked)."}
            ]
        else:
            system = (
                f"You are {self.persona}. Produce a concise plan of 2-4 steps for the task."
                " Return a JSON array of steps, each as {'id': n, 'name': '...', 'desc': '...'}."
            )
            prompt = f"Task: {user_prompt}\n\nProduce the plan as JSON."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            try:
                plan = json.loads(content)
            except Exception:
                plan = [
                    {"id": 1, "name": "Summarize", "desc": "Create short notes (fallback)."},
                    {"id": 2, "name": "Create Quiz", "desc": "Make 5 short quiz questions (fallback)."}
                ]
        log_interaction({"role": "planner", "input": user_prompt, "plan": plan})
        return plan

# -------------------- Executor --------------------
class ExecutorAgent:
    def __init__(self, persona="Mom Agent"):
        self.persona = persona

    def execute_step(self, step: dict, source_text: str):
        name = step.get("name", "").lower()

        if USE_MOCK:
            if "summar" in name or "note" in name:
                notes = "- Point 1\n- Point 2\n- Point 3\n- Point 4\n- Point 5"
                log_interaction({"role": "executor", "step": step, "output_type": "notes", "output": notes})
                return {"type": "notes", "content": notes}
            elif "quiz" in name or "question" in name:
                quiz = (
                    "Q1: Mock question?\nA. Option1 B. Option2 C. Option3 D. Option4\nAnswer: A\n"
                    "Q2: Mock question?\nA. Option1 B. Option2 C. Option3 D. Option4\nAnswer: B\n"
                    "Q3: Mock question?\nA. Option1 B. Option2 C. Option3 D. Option4\nAnswer: C\n"
                    "Q4: Mock question?\nA. Option1 B. Option2 C. Option3 D. Option4\nAnswer: D\n"
                    "Q5: Mock question?\nA. Option1 B. Option2 C. Option3 D. Option4\nAnswer: A"
                )
                log_interaction({"role": "executor", "step": step, "output_type": "quiz", "output": quiz})
                return {"type": "quiz", "content": quiz}
            else:
                generic = "[MOCK EXECUTION OUTPUT]"
                log_interaction({"role": "executor", "step": step, "output_type": "generic", "output": generic})
                return {"type": "generic", "content": generic}

        else:
            # real API call
            if "summar" in name or "note" in name:
                prompt = (
                    "You are a caring mom who explains concepts simply. "
                    "From the following input, produce short notes in 5 concise bullet points, "
                    "each 8-20 words max. Keep tone encouraging.\n\n"
                    f"INPUT:\n{source_text}\n\nNOTES:"
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are Mom Agent, supportive and concise."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    temperature=0.3,
                )
                notes = resp.choices[0].message.content.strip()
                log_interaction({"role": "executor", "step": step, "output_type": "notes", "output": notes})
                return {"type": "notes", "content": notes}

            elif "quiz" in name or "question" in name:
                prompt = (
                    "You are a caring mom who helps test knowledge. From the input below, "
                    "generate 5 short quiz questions with 4 options each (A-D) and mark the correct option. "
                    "Make questions balanced (recall/comprehension). Provide answers after questions.\n\n"
                    f"INPUT:\n{source_text}\n\nQUIZ:"
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are Mom Agent, supportive and concise."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=600,
                    temperature=0.4,
                )
                quiz = resp.choices[0].message.content.strip()
                log_interaction({"role": "executor", "step": step, "output_type": "quiz", "output": quiz})
                return {"type": "quiz", "content": quiz}

            else:
                prompt = f"Execute this step: {step.get('desc','')}\nUsing source:\n{source_text}"
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                )
                out = resp.choices[0].message.content.strip()
                log_interaction({"role": "executor", "step": step, "output_type": "generic", "output": out})
                return {"type": "generic", "content": out}

# -------------------- Reminders --------------------
DEFAULT_REMINDERS = [
    {"name": "Breakfast", "time": "09:00", "message": "Breakfast time! Fuel up, baby."},
    {"name": "Lunch", "time": "13:00", "message": "Lunch time — don't skip it."},
    {"name": "Dinner", "time": "20:00", "message": "Dinner time — eat well."},
    {"name": "Drink Water", "time": "every_2h", "message": "Time to drink water — sip some now!"},
]

def fire_notification(reminder):
    notification.notify(
        title=f"Mom Agent: {reminder['name']}",
        message=reminder['message'],
        timeout=10
    )

def check_reminders_now(reminders=DEFAULT_REMINDERS):
    now = datetime.now().strftime("%H:%M")
    fired = []
    for r in reminders:
        if r["time"] == "every_2h" or r["time"] == now:
            fired.append(r)
    if not fired:
        fired = reminders
    for r in fired:
        fire_notification(r)
    log_interaction({"role": "reminder_system", "fired": fired})
    return fired

# -------------------- Full Pipeline --------------------
def run_full_pipeline(user_text: str):
    planner = PlannerAgent()
    executor = ExecutorAgent()
    plan = planner.plan_study_task(f"Create notes & quiz for: {user_text}")
    outputs = []
    for step in plan:
        out = executor.execute_step(step, user_text)
        outputs.append({"step": step, "result": out})
    return {"plan": plan, "outputs": outputs}
