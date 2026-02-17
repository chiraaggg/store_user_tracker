import streamlit as st
import pandas as pd
import requests
import dotenv
import os

dotenv.load_dotenv()

# ================= CONFIG ================= #
API_KEY = st.secrets["api"]["API_KEY"]
API_URL = st.secrets["api"]["API_URL"]

GOAL = 5000

# ================= SQL QUERY ================= #
SQL_QUERY = """
SELECT 
    u.id AS user_id,
    u.name AS name,
    u.phone AS phone,
    SUM(so.total) AS total_spent
FROM store_orders so
JOIN users u ON u.id = so.user_id
WHERE u.id IN (
45254,45748,44135,46073,44159,44491,45742,45941,43756,42708,40901,
45949,39869,39864,45711,45802,45985,45740,45102,45762,42712,45821,
46071,45980,45746,45942,46216,46155,46065,45916,45096,45513,43782,
46235,45801,40827,46273,45874,44492,45940,46464,45027,45879,45800,
45759,44551,46341,46738,45884,45873,44469,39834,39836,39850,45833,
46103,45970,39086,45767,46293,46492,46010,45979,45798,45758,45796,
45747,40800,46290,43758,45768,45854,46671,45986,46148,46460,45589,
46731,40839,45825,45789,46395,46149,46222,45841,45792,45945,46061,
46384,45783,46432,45750,46267,46532,45981
)
GROUP BY u.id, u.name, u.phone
ORDER BY total_spent DESC;
"""

# ================= API FETCH ================= #
@st.cache_data(ttl=600)
def fetch_data():
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    payload = {"query": SQL_QUERY}

    res = requests.post(API_URL, json=payload, headers=headers)
    res.raise_for_status()
    raw = res.json()

    # normalize JSON
    if isinstance(raw, dict) and "data" in raw:
        df = pd.DataFrame(raw["data"])
    else:
        df = pd.DataFrame(raw)

    # normalize column names
    df.columns = [c.lower() for c in df.columns]

    return df


# ================= PREMIUM UI CSS ================= #
st.markdown("""
<style>
body { background-color: #020617; }
.card {
    padding: 14px;
    border-radius: 14px;
    background: #0f172a;
    border: 1px solid #1e293b;
    margin-bottom: 12px;
}
.bar-bg {
    background: #1e293b;
    border-radius: 10px;
    height: 12px;
}
.bar-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg,#22c55e,#4ade80);
}
.small-text {
    color:#94a3b8;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)


# ================= PROGRESS UI FUNCTION ================= #
def fancy_progress(name, phone, spent, goal=5000):
    percent = min(spent / goal * 100, 100)

    # Color logic
    if spent >= goal:
        color = "linear-gradient(90deg,#22c55e,#16a34a)"
    elif spent >= goal * 0.5:
        color = "linear-gradient(90deg,#facc15,#f97316)"
    else:
        color = "linear-gradient(90deg,#ef4444,#b91c1c)"

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;justify-content:space-between;">
            <b style="color:white;">{name} | 📞 {phone}</b>
            <span style="color:#38bdf8;">₹{spent:,.0f}</span>
        </div>

        <div class="bar-bg" style="margin-top:8px;">
            <div class="bar-fill" style="width:{percent}%;background:{color};"></div>
        </div>

        <div class="small-text" style="text-align:right;margin-top:4px;">
            {percent:.1f}% of ₹{goal:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================= STREAMLIT UI ================= #
st.set_page_config(page_title="User Spend Dashboard", layout="wide")
st.title("💰 High Value Users Spend Dashboard")

# Fetch data
df = fetch_data()

# Debug panel
with st.expander("🔍 Debug"):
    st.write(df.head())
    st.write(df.columns)

# Safety check
if "total_spent" not in df.columns:
    st.error(f"Column total_spent missing. Found: {df.columns.tolist()}")
    st.stop()

# Convert spend to numeric
df["total_spent"] = pd.to_numeric(df["total_spent"], errors="coerce").fillna(0)

# Metrics
st.metric("Total Users", len(df))
st.metric("Total Revenue", f"₹{df['total_spent'].sum():,.0f}")

st.divider()

# Table
st.subheader("📊 User Spend Table")
st.dataframe(df.sort_values("total_spent", ascending=False), use_container_width=True)

st.divider()

# Leaderboard Progress UI
st.subheader("🏆 Progress to ₹5,000 Goal (Leaderboard)")

df = df.sort_values("total_spent", ascending=False).reset_index(drop=True)

for i, r in df.iterrows():
    rank = i + 1
    fancy_progress(f"#{rank} {r['name']}", r.get("phone", "NA"), r["total_spent"])
