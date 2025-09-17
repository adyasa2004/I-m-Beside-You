import streamlit as st
from agent import run_full_pipeline, check_reminders_now, DEFAULT_REMINDERS, LOGFILE
import os
import threading
import PyPDF2
from datetime import datetime

st.set_page_config(page_title="Mom Agent", layout="wide")
st.title("👩‍👧 Mom Agent — Notes, Quiz & Care")
st.markdown("A caring agent that makes short notes, quiz questions — and reminds you to eat & drink water.")

# Sidebar for user metadata
with st.sidebar:
    st.header("Your Info (for README)")
    name = st.text_input("Your name", value="Adyasa")
    university = st.text_input("University", value="IIT Guwahati")
    department = st.text_input("Department", value="Your Dept")
    st.markdown("---")
    st.markdown("API Key must be set in environment variable `OPENAI_API_KEY` on the machine running this app.")

# --- Background reminder thread ---
def reminder_loop():
    while True:
        check_reminders_now()
        time.sleep(60)  # check every minute

threading.Thread(target=reminder_loop, daemon=True).start()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Study with Mom", "Care with Mom (Reminders)", "Logs & Submit"])

with tab1:
    st.header("Study with Mom")
    uploaded_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
    text_input = st.text_area("Or paste lecture text here", height=250)

    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            extracted = [p.extract_text() or "" for p in reader.pages]
            text_input = "\n".join(extracted)
            st.success("PDF text extracted.")
        except Exception as e:
            st.error(f"PDF read error: {e}")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Generate Notes & Quiz"):
            if not text_input.strip():
                st.warning("Please paste some text or upload a PDF.")
            else:
                with st.spinner("Mom is thinking..."):
                    result = run_full_pipeline(text_input)
                st.subheader("Plan (Mom's steps)")
                for s in result["plan"]:
                    st.write(f"**{s.get('id')} - {s.get('name')}**: {s.get('desc')}")
                st.subheader("Results")
                for out in result["outputs"]:
                    t = out["result"]["type"]
                    st.markdown(f"**{out['step']['name']} — ({t})**")
                    st.write(out["result"]["content"])

    with col2:
        st.subheader("Quick Examples")
        if st.button("Load Example: Thermodynamics"):
            st.session_state["example_text"] = ("First law of thermodynamics: energy conservation. "
                                                "Work and heat are transfer modes. Enthalpy, internal energy, PV work.")
            st.experimental_rerun()
        if "example_text" in st.session_state:
            st.info(st.session_state["example_text"])

with tab2:
    st.header("Care with Mom — Reminders")
    st.markdown("Reminders are automatically checked every minute in the background. You will see desktop notifications at the scheduled times.")
    st.markdown("---")
    st.write("Default reminders (editable in agent.py):")
    for r in DEFAULT_REMINDERS:
        st.write(f"- **{r['name']}** at `{r['time']}` — {r['message']}")

with tab3:
    st.header("Interaction Logs & Submission")
    if os.path.exists(LOGFILE):
        st.write("Recent logs (last 30 lines):")
        with open(LOGFILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-30:]
            for ln in lines:
                st.code(ln.strip())
    else:
        st.info("No logs yet. Interact with the agent to produce logs.")

    st.markdown("---")
    st.subheader("Prepare GitHub URL")
    repo_url = st.text_input("Paste your GitHub repo URL (for submission)")
    if repo_url and st.button("Mark as ready to submit"):
        st.success("Marked ready. Copy this URL and email it to the addresses in the assignment.")
        st.write(repo_url)
