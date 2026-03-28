# app.py
import streamlit as st
from metrics import recommend_funds
from explainer import explain_recommendations, explain_tradeoffs
from rag import get_vectorstore, answer_question

st.set_page_config(page_title="Mutual Fund Advisor", page_icon="📊", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0f1117; }
.block-container { max-width: 800px; padding-top: 2rem; padding-bottom: 3rem; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Section container styling using Streamlit's container ── */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}

/* ── App Header ── */
.app-header { text-align: center; padding: 1rem 0 1.5rem 0; }
.app-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #e2e8f0;
    margin: 0.5rem 0 0.3rem 0;
}
.app-header p { color: #64748b; font-size: 0.88rem; margin: 0; }
.logo-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px; height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    margin-bottom: 0.5rem;
}
.logo-box svg { width: 28px; height: 28px; stroke: white; fill: none; stroke-width: 2; }

/* ── Section header inside box ── */
.box-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #2a2d3e;
    margin-bottom: 1.2rem;
}
.box-icon {
    width: 36px; height: 36px;
    border-radius: 9px;
    background: #1e3a5f;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.box-icon svg { width: 18px; height: 18px; stroke: #60a5fa; fill: none; stroke-width: 2; }
.box-title { font-size: 0.98rem; font-weight: 700; color: #e2e8f0; margin: 0; }
.box-sub { font-size: 0.76rem; color: #64748b; margin: 0; }

/* ── Risk Banner ── */
.risk-low {
    background: #0a2200; border: 1px solid #22c55e30;
    border-radius: 8px; padding: 0.7rem 1rem;
    color: #4ade80; font-size: 0.82rem; margin-top: 0.5rem;
}
.risk-medium {
    background: #001a3d; border: 1px solid #3b82f630;
    border-radius: 8px; padding: 0.7rem 1rem;
    color: #60a5fa; font-size: 0.82rem; margin-top: 0.5rem;
}
.risk-high {
    background: #200a00; border: 1px solid #f9731630;
    border-radius: 8px; padding: 0.7rem 1rem;
    color: #fb923c; font-size: 0.82rem; margin-top: 0.5rem;
}

/* ── Fund Card ── */
.fund-card {
    background: #12151f;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.rank-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 7px;
    font-weight: 700; font-size: 0.8rem; margin-right: 0.6rem;
}
.r1 { background: #2d2000; color: #f59e0b; border: 1px solid #f59e0b40; }
.r2 { background: #001a2d; color: #3b82f6; border: 1px solid #3b82f640; }
.r3 { background: #0a2200; color: #22c55e; border: 1px solid #22c55e40; }
.fund-name { font-weight: 600; color: #e2e8f0; font-size: 0.92rem; }
.fund-cat { color: #475569; font-size: 0.76rem; margin: 0.3rem 0 0.8rem 2rem; }

.metrics-row { display: flex; gap: 0.6rem; }
.metric-box {
    flex: 1; background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 8px; padding: 0.6rem 0.8rem;
}
.metric-label { font-size: 0.65rem; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.metric-value { font-size: 1.05rem; font-weight: 700; margin-top: 0.15rem; }
.mv-cagr { color: #818cf8; }
.mv-vol { color: #34d399; }
.mv-sha { color: #fb923c; }

/* ── Source note ── */
.source-note {
    background: #12151f; border: 1px solid #1e3a5f;
    border-radius: 8px; padding: 0.6rem 1rem;
    color: #475569; font-size: 0.75rem; margin-top: 0.5rem;
}

/* ── Inner box for insights ── */
.inner-box {
    background: #12151f; border: 1px solid #2a2d3e;
    border-radius: 12px; padding: 1.1rem; height: 100%;
}
.inner-label {
    font-size: 0.75rem; font-weight: 600; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem;
}
.insight-text { font-size: 0.82rem; color: #94a3b8; line-height: 1.7; }
.metric-explain { margin-bottom: 0.7rem; }
.metric-explain b { color: #e2e8f0; font-size: 0.82rem; display: block; margin-bottom: 0.1rem; }
.metric-explain span { color: #64748b; font-size: 0.8rem; }

/* ── Tradeoff ── */
.tradeoff-box {
    background: #1c1500; border: 1px solid #f59e0b30;
    border-left: 3px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem; color: #d4b896;
    font-size: 0.85rem; line-height: 1.7; margin-top: 1rem;
}

/* ── RAG answer ── */
.rag-answer {
    background: #001a3d; border: 1px solid #1e3a5f;
    border-radius: 10px; padding: 1.1rem;
    color: #93c5fd; font-size: 0.85rem; line-height: 1.7; margin-top: 0.8rem;
}

/* ── Streamlit widget overrides ── */
.stNumberInput input {
    background: #12151f !important; border: 1px solid #2a2d3e !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
}
.stSelectbox > div > div {
    background: #12151f !important; border: 1px solid #2a2d3e !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
}
.stTextInput input {
    background: #12151f !important; border: 1px solid #2a2d3e !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
}
.stSelectbox label, .stNumberInput label, .stTextInput label {
    color: #64748b !important; font-size: 0.82rem !important; font-weight: 500 !important;
}
.stCaption { color: #475569 !important; font-size: 0.75rem !important; }
div[data-baseweb="select"] { background: #12151f !important; }
div[data-baseweb="select"] > div { background: #12151f !important; border-color: #2a2d3e !important; color: #e2e8f0 !important; }

.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #2563eb) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.7rem 1.5rem !important;
    font-size: 0.92rem !important; font-weight: 600 !important;
    width: 100% !important; letter-spacing: 0.02em !important;
}
.stButton > button:hover { opacity: 0.9 !important; }

.app-footer {
    text-align: center; color: #334155; font-size: 0.75rem; padding: 2rem 0 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Vectorstore ──
@st.cache_resource
def load_vectorstore():
    return get_vectorstore()
vectorstore = load_vectorstore()

# ════════════════════════════════
# HEADER
# ════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="logo-box">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>
    </div>
    <h1>Mutual Fund Advisor</h1>
    <p>Personalized recommendations powered by AMFI data & SEBI guidelines</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════
# BOX 1 — Investment Profile
# ════════════════════════════════
with st.container(border=True):
    st.markdown("""
    <div class="box-header">
        <div class="box-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
        </div>
        <div>
            <div class="box-title">Your Investment Profile</div>
            <div class="box-sub">Let us understand your financial goals and preferences</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Investment Amount (₹)", min_value=1000, max_value=10000000, value=100000, step=None)
        st.caption(f"₹{amount:,.0f}")
    with col2:
        age = st.number_input("Your Age", min_value=18, max_value=80, value=30,step=None)
        st.caption(f"{age} years old")

    risk_level = st.selectbox(
        "Risk Tolerance Level",
        options=["low", "medium", "high"],
        format_func=lambda x: {
            "low": "Low Risk — Capital Preservation",
            "medium": "Medium Risk — Balanced Growth",
            "high": "High Risk — Maximum Growth"
        }[x],
        index=1
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    get_rec = st.button("Get Personalized Recommendations")

# ════════════════════════════════
# RESULTS
# ════════════════════════════════
if get_rec:
    with st.spinner("Fetching real fund data from AMFI..."):
        results = recommend_funds(risk_level=risk_level, top_n=3)

    if results.empty:
        st.error("Could not fetch fund data. Please try again.")
    else:
        # ── BOX 2 — Top 3 Funds ──
        with st.container(border=True):
            st.markdown("""
            <div class="box-header">
                <div class="box-icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M10 14.66V17M14 14.66V17M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>
                </div>
                <div>
                    <div class="box-title">Top 3 Recommended Funds</div>
                    <div class="box-sub">Ranked by Sharpe ratio — best risk-adjusted return from real AMFI data</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            rank_classes = ["r1", "r2", "r3"]
            for i, (_, row) in enumerate(results.iterrows()):
                st.markdown(f"""
                <div class="fund-card">
                    <div style="display:flex;align-items:center;margin-bottom:0.2rem">
                        <span class="rank-badge {rank_classes[i]}">{i+1}</span>
                        <span class="fund-name">{row['fund_name']}</span>
                    </div>
                    <div class="fund-cat">{row['category']}</div>
                    <div class="metrics-row">
                        <div class="metric-box">
                            <div class="metric-label">CAGR (3Y)</div>
                            <div class="metric-value mv-cagr">{row['cagr_%']}%</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Volatility</div>
                            <div class="metric-value mv-vol">{row['volatility_%']}%</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Sharpe Ratio</div>
                            <div class="metric-value mv-sha">{row['sharpe_ratio']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="source-note">
                Data sourced from AMFI. Past performance does not guarantee future results.
                Consult a financial advisor before investing.
            </div>
            """, unsafe_allow_html=True)

        # ── BOX 3 — Insights ──
        with st.container(border=True):
            st.markdown("""
            <div class="box-header">
                <div class="box-icon">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1.3.5 2.6 1.5 3.5.8.8 1.3 1.5 1.5 2.5M9 18h6M10 22h4"/></svg>
                </div>
                <div>
                    <div class="box-title">Insights & Analysis</div>
                    <div class="box-sub">Personalized explanation based on your profile and real metrics</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Generating insights..."):
                explanation = explain_recommendations(results, risk_level, amount, age)
                tradeoffs = explain_tradeoffs(results, age)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="inner-box">
                    <div class="inner-label">Your Investment Journey</div>
                    <div class="insight-text">{explanation}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown("""
                <div class="inner-box">
                    <div class="inner-label">Key Metrics Explained</div>
                    <div class="metric-explain">
                        <b>CAGR (3Y)</b>
                        <span>Average annual growth over 3 years. Higher is generally better.</span>
                    </div>
                    <div class="metric-explain">
                        <b>Volatility</b>
                        <span>Measures price fluctuations. Lower means more stability.</span>
                    </div>
                    <div class="metric-explain">
                        <b>Sharpe Ratio</b>
                        <span>Risk-adjusted returns. Higher means better return for risk taken.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="tradeoff-box">
                <b style="color:#f59e0b">Trade-off Analysis</b><br><br>{tradeoffs}
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════
# BOX 4 — Knowledge Hub
# ════════════════════════════════
with st.container(border=True):
    st.markdown("""
    <div class="box-header">
        <div class="box-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div>
            <div class="box-title">Knowledge Hub</div>
            <div class="box-sub">Ask anything about mutual funds — answers from official SEBI documents</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input("", placeholder="e.g. What is SIP? What is NAV? What is expense ratio?")

    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching SEBI documents..."):
                answer = answer_question(question, vectorstore)
            st.markdown(f"""
            <div class="rag-answer">
                <b style="color:#60a5fa">Answer:</b><br><br>{answer}<br><br>
                <span style="font-size:0.72rem;color:#334155">
                    Source: SEBI Mutual Fund FAQ · AMFI Methodology Document
                </span>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="app-footer">
    This is an educational tool. Always consult a registered financial advisor before making investment decisions.<br>
    © 2024 Mutual Fund Advisor. All rights reserved.
</div>
""", unsafe_allow_html=True)