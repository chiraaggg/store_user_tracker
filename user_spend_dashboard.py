import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
import os
import dotenv
dotenv.load_dotenv()
# ================= CONFIG =================
API_KEY = os.environ.get('API_KEY')
API_URL = os.environ.get('API_URL')
GOAL = 5000

# ================= SQL QUERIES =================

PHOENIX_QUERY = """
SELECT u.id, u.name, u.phone, SUM(so.total) AS total_spent
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
ORDER BY total_spent;
"""

FRAZER_QUERY = f"""
SELECT u.id, u.name, u.phone, SUM(so.total) AS total_spent
FROM store_orders so
JOIN users u ON u.id = so.user_id
WHERE u.id IN (
38419,44568,44603,42295,41912,39522,41313,41906,39468,44559,
41901,43091,38794,39545,39535,43525,4837,42248,45836,37893,
45543,33291,46455,45568,44522,40842,41746,46307,41816,42184,
44974,44690,40504,42408,44341,42317,42153,46544,827,42155,
41979,43795,41479,41514,39570,39539,40119,39476,42050,43361,
39566,44577,39490,40896,39462,43621,44561,42614,39519,43870,
39859,40871,46459,40395,45466,39591,39498,45644,44307,43136,
46653,42705,46159,41533,40992,44720,45567,39632,41075,41539,
45300,38522,40251,43766,43618,41454,44693,41770,42044,42437,
40654,46749,45297,41825,42480,45809,41828,42791,43762,44772,
41496,40498,40539,42188,41359,39915,45124,42315,40391,46644,
39667,39775,44497,37612,43601,44106,42632,38586,41502,39692,
44294,42129,44794,45105,43216,44494,42183,39518,40915,42229,
44797,44606,44871,44014,39116,44604,46205,43721,39678,40815,
43352,45036,40680,26374,42092,39970,44502,43845,41197,40997,
45395,43768,44862,42414,45362,42206,39784,44213,33283,40727,
41981,46619,44731,39885,42212,42097,39554,46648,41485,45738,
32333,39484,41379,41175,46263,45375,43777,45517,44485,42316,
45441,42605,43878,40687,41501,32507,44979,41523,42225,42011,
44921,46393,42543,45474,37227,44576,42550,45152,42327,41796,
45630,43912,42552,41690,42395,43844,39494,41590,39620,43622,
45647,42357,42282,45999,39961,42880,42772,42250,46346,42185,
42065,46347,39939,43910,41371,40339,44475,40794,45508,42009,
46323,44551,42639,45525,43648,41079,43363,41526,46237,45882,
26793,41483,42702,45539,45367,44524,42220,44059,43917,42707
)
GROUP BY u.id, u.name, u.phone
ORDER BY total_spent;
"""

# ================= API FETCH =================
@st.cache_data(ttl=600)
def fetch_data(query):
    headers = {"Content-Type": "application/json", "X-API-KEY": API_KEY}
    res = requests.post(API_URL, json={"query": query}, headers=headers)
    res.raise_for_status()
    return pd.DataFrame(res.json()["data"])

# ================= UI STYLING =================
st.set_page_config("Store Spend Dashboard", layout="wide")
st.title("🏆 High Value User Spend Leaderboard")

css = """
<style>
.card {
    background:#0f172a;
    padding:14px;
    border-radius:14px;
    margin-bottom:10px;
    border:1px solid #1e293b;
    color:white;
}
.bar-bg {
    width:100%;
    height:16px;
    background:#111827;
    border-radius:10px;
    overflow:hidden;
}
.bar-fill {
    height:100%;
    border-radius:10px;
}
.small {
    font-size:12px;
    color:#9ca3af;
}
</style>
"""
components.html(css, height=0)

# ================= LEADERBOARD FUNCTION =================
def render_leaderboard(df):
    df = df.sort_values("total_spent")  # ascending

    for rank, row in enumerate(df.itertuples(), start=1):
        percent = min(row.total_spent / GOAL * 100, 100)

        if percent < 50:
            color = "#f97316"
        elif percent < 100:
            color = "#3b82f6"
        else:
            color = "#22c55e"

        html = f"""
        <div class="card">
            <b>#{rank} {row.name}</b> | 📞 {row.phone}<br>
            <b>₹{row.total_spent:,.0f}</b>

            <div class="bar-bg">
                <div class="bar-fill" style="width:{percent}%; background:{color};"></div>
            </div>

            <div class="small" style="text-align:right;">
                {percent:.1f}% of ₹{GOAL:,}
            </div>
        </div>
        """
        components.html(html, height=120)

# ================= TABS =================
tab1, tab2 = st.tabs(["🏬 Phoenix Store", "🏬 Frazer Town Store"])

# -------- Phoenix --------
with tab1:
    st.subheader("Phoenix Store Users")
    df_phoenix = fetch_data(PHOENIX_QUERY)
    st.metric("Total Users", len(df_phoenix))
    st.metric("Total Revenue", f"₹{df_phoenix.total_spent.sum():,.0f}")
    render_leaderboard(df_phoenix)

# -------- Frazer Town --------
with tab2:
    st.subheader("Frazer Town Store Users")
    df_frazer = fetch_data(FRAZER_QUERY)
    st.metric("Total Users", len(df_frazer))
    st.metric("Total Revenue", f"₹{df_frazer.total_spent.sum():,.0f}")
    render_leaderboard(df_frazer)
