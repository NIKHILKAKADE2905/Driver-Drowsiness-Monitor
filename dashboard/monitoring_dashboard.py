import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime
import bcrypt
from urllib.parse import quote_plus

# ------------------------------
# ⚙️ MongoDB Setup
# ------------------------------
def connect_to_cloud_db():
    # if your username or password contains any special character then use the quote_plus for percent encoding
    user_name = st.secrets["MONGO"]["USER"]
    password = quote_plus(st.secrets["MONGO"]["PASS"])
    project_name = st.secrets["MONGO"]["PROJECT_NAME"]
    uri = f"mongodb+srv://{user_name}:{password}@cluster0.6saqqje.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Load URI securely from environment
    # uri = "YOUR_MONGODB_URI" you can paste your own database uri
    client = MongoClient(uri)
    db = client[project_name]
    return db["users"], db["sessions"]

users_col, sessions_col = connect_to_cloud_db()

# ------------------------------
# 🔒 User Authentication
# ------------------------------
def authenticate_user(username, password):
    user = users_col.find_one({"username": username})
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user["pw_hash"])

# ------------------------------
# 📦 Session Fetching & Sorting
# ------------------------------
def get_user_sessions(username, sort_mode):
    sessions = list(sessions_col.find({"username": username}))
    sessions.sort(
        key=lambda s: datetime.fromisoformat(s["timestamp"]),
        reverse=(sort_mode == "Latest First")
    )
    return sessions

def get_session_df(session_doc):
    return pd.DataFrame(session_doc["metrics"])

# ------------------------------
# 📈 Graphing Functions
# ------------------------------
def plot_blink_yawn(df):
    fig = px.line(df, x="timestamp",
                  y=["blink_count", "avg_blink_duration", "yawn_count"],
                  markers=True,
                  title="Blink, Duration, Yawn Trends",
                  color_discrete_map={"blink_count": "#636EFA", "avg_blink_duration": "#EF553B", "yawn_count": "#00CC96"})
    st.plotly_chart(fig, use_container_width=True)

def plot_eye_closure(df):
    fig = px.area(df, x="timestamp", y="total_eye_closure_duration",
                  title="Eye Closure Duration Over Time",
                  line_shape="spline", color_discrete_sequence=["#AB63FA"])
    st.plotly_chart(fig, use_container_width=True)

def plot_drowsiness_state(df):
    count_df = df["drowsiness_state"].value_counts().reset_index()
    count_df.columns = ["State", "Count"]
    fig = px.bar(count_df, x="State", y="Count",
                 color="State",
                 title="Drowsiness Intensity Distribution",
                 color_discrete_sequence=px.colors.qualitative.Vivid)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 🚀 Streamlit App
# ------------------------------
st.set_page_config(page_title="Driver Monitoring Dashboard", layout="wide")

# Sidebar Login
with st.sidebar:
    st.title("🔐 Driver Login")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in!")
            else:
                st.error("Incorrect credentials.")

# ------------------------------
# 💻 Main Dashboard
# ------------------------------
if st.session_state.logged_in:
    st.markdown(f"## Welcome, **{st.session_state.username}** 👋")
    st.markdown("---")

    sort_option = st.selectbox("🗂 Sort Sessions", ["Latest First", "Oldest First"])
    sessions = get_user_sessions(st.session_state.username, sort_option)

    if not sessions:
        st.warning("No sessions found.")
    else:
        session_ids = [s["session_id"] for s in sessions]
        selected_id = st.selectbox("📄 Choose a Session", session_ids)

        selected_session = next(s for s in sessions if s["session_id"] == selected_id)
        df = get_session_df(selected_session)

        st.markdown(f"### 📊 Metrics for `{selected_id}`")
        col1, col2, col3 = st.columns(3)
        col1.metric("🕒 Start Time", selected_session["timestamp"])
        col2.metric("📦 Total Frames", len(df))
        col3.metric("🚧 Reroutes", int((df["reroute_triggered"] == "Yes").sum()))

        st.markdown("---")
        plot_blink_yawn(df)
        plot_eye_closure(df)
        plot_drowsiness_state(df)

        st.markdown("---")
        st.markdown("### 🚧 Rerouting Events")
        rerouted = df[df["reroute_triggered"] == "Yes"]
        if not rerouted.empty:
            st.dataframe(rerouted)
        else:
            st.info("No rerouting triggered during this session.")