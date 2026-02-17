import streamlit as st
import pandas as pd
import requests
import dotenv
import os
dotenv.load_dotenv()

API_KEY = st.secrets["api"]["API_KEY"]
API_URL = st.secrets["api"]["API_URL"]

GOAL = 5000

SQL_QUERY = """
SELECT 
    u.id,
    u.name,
    u.phone,
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
GROUP BY u.id, u.name
ORDER BY total_spent DESC;
"""

@st.cache_data(ttl=600)
def fetch_data():
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    print(headers)
    payload = {"query": SQL_QUERY}

    res = requests.post(API_URL, json=payload, headers=headers)
    res.raise_for_status()

    return pd.DataFrame(res.json()["data"])


# UI
st.set_page_config("User Spend Dashboard", layout="wide")
st.title("💰 High Value Users Spend Dashboard")

# Comment this for testing
df = fetch_data()

# Dummy Data
# df = pd.DataFrame([
#     {"user_id": 45254, "name": "Chirag", "phone": "9876543210", "total_spent": 12450},
#     {"user_id": 45748, "name": "Amit", "phone": "9123456789", "total_spent": 3200},
#     {"user_id": 44135, "name": "Rahul", "phone": "9988776655", "total_spent": 7800},
#     {"user_id": 46073, "name": "Sneha", "phone": "9090909090", "total_spent": 450},
#     {"user_id": 44159, "name": "Pooja", "phone": "9345678901", "total_spent": 15000},
# ])
st.metric("Total Users", len(df))
st.metric("Total Revenue", f"₹{df.total_spent.sum():,.0f}")

st.divider()
st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("🎯 Progress to ₹5,000")

for _, r in df.iterrows():
    spent = r["total_spent"] or 0
    progress = min(spent / GOAL, 1.0)

    st.write(f"**{r['name']} | 📞 {r['phone']} | ₹{spent:,.0f}**")
    st.progress(progress)
