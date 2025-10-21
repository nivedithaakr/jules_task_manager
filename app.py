import streamlit as st
import json, os, requests

API_BASE = "http://localhost:8000"
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_tasks():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

st.set_page_config(page_title="Jules Task Manager", page_icon="🧠", layout="wide")
st.title("🧠 Jules Task Manager")

tab1, tab2, tab3 = st.tabs(["My Tasks", "Send to Jules", "Track Jules"])

# --- My Tasks ---
with tab1:
    st.subheader("📋 Local Tasks")
    tasks = load_tasks()

    with st.form("add_task"):
        desc = st.text_input("Task Description", placeholder="e.g., Add animations to UI")
        submitted = st.form_submit_button("Add Task")
        if submitted and desc.strip():
            tasks.append({"task": desc, "status": "Pending"})
            save_tasks(tasks)
            st.success("Task added!")
            st.rerun()

    if not tasks:
        st.info("No tasks yet.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([6, 2, 2])
            col1.write(f"**{i+1}. {t['task']}**")
            col2.write("🟡 Pending" if t["status"] == "Pending" else "🟢 Done")
            if col3.button("Mark Done", key=f"done_{i}"):
                tasks[i]["status"] = "Done"
                save_tasks(tasks)
                st.rerun()

# --- Send to Jules ---
with tab2:
    st.subheader("🤖 Send Task to Jules")
    with st.form("jules_task"):
        title = st.text_input("Title", placeholder="e.g., Add dark mode")
        body = st.text_area("Details", height=150)
        go = st.form_submit_button("Create GitHub Issue for Jules")
        if go:
            if not title.strip():
                st.warning("Title is required")
            else:
                r = requests.post(f"{API_BASE}/jules/issues", json={"title": title, "body": body})
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"Issue #{data['number']} created: {data['url']}")
                else:
                    st.error(f"Error: {r.text}")

# --- Track Jules ---
with tab3:
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 🛰 Jules Issues")
        try:
            r = requests.get(f"{API_BASE}/jules/issues")
            if r.status_code == 200:
                for it in r.json():
                    st.write(f"- **#{it['number']}** [{it['title']}]({it['url']}) — {it['state']}")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(e)

    with colB:
        st.markdown("### 🔁 Jules Pull Requests")
        try:
            r = requests.get(f"{API_BASE}/jules/prs")
            if r.status_code == 200:
                for pr in r.json():
                    st.write(f"- **PR #{pr['number']}** [{pr['title']}]({pr['url']}) — {pr['state']}  \n `branch`: {pr.get('head_ref')}")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(e)
