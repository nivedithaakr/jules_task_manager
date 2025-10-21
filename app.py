import streamlit as st
import json, os, requests

API_BASE = "http://localhost:8000"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_tasks():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def get_weather(city):
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        st.sidebar.warning("Weather API key not set. Please set it in your environment variables.")
        return None

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Error fetching weather: {e}")
        return None

st.set_page_config(page_title="Jules Task Manager", page_icon="🧠", layout="wide")
st.title("🧠 Jules Task Manager")

st.sidebar.header("Weather")
city = st.sidebar.text_input("Enter a city", "London")
if st.sidebar.button("Get Weather"):
    weather_data = get_weather(city)
    if weather_data:
        st.sidebar.write(f"**{weather_data['location']['name']}**")
        st.sidebar.write(f"Temperature: {weather_data['current']['temp_c']}°C / {weather_data['current']['temp_f']}°F")
        st.sidebar.write(f"Condition: {weather_data['current']['condition']['text']}")
        st.sidebar.image(f"http:{weather_data['current']['condition']['icon']}")

tab1, tab2, tab3 = st.tabs(["My Tasks", "Send to Jules", "Track Jules"])

# --- My Tasks ---
with tab1:
    st.subheader("📋 Local Tasks")
    tasks = load_tasks()

    search_query = st.text_input("Search tasks by title", "")

    with st.form("add_task"):
        desc = st.text_input("Task Description", placeholder="e.g., Add animations to UI")
        submitted = st.form_submit_button("Add Task")
        if submitted and desc.strip():
            tasks.append({"task": desc, "status": "Pending"})
            save_tasks(tasks)
            st.success("Task added!")
            st.rerun()

    if search_query:
        tasks = [task for task in tasks if search_query.lower() in task['task'].lower()]

    if not tasks:
        st.info("No tasks yet." if not search_query else "No tasks found matching your search.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([6, 2, 2])
            col1.write(f"**{i+1}. {t['task']}**")
            col2.write("🟡 Pending" if t["status"] == "Pending" else "🟢 Done")
            if col3.button("Mark Done", key=f"done_{i}"):
                original_tasks = load_tasks()
                for task in original_tasks:
                    if task['task'] == t['task'] and task['status'] == t['status']:
                        task['status'] = "Done"
                        break
                save_tasks(original_tasks)
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
