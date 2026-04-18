"""
Drachmann Trading — Value Investing Dashboard
Nasdaq Copenhagen · Jens Løgstrup philosophy

Run:
    streamlit run app.py
"""

import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

import config
from modules.database import (
    initialize_db, get_latest_scores, get_score_history, get_signal_log,
)
from modules.data_fetcher import fetch_stock_data, fetch_price_history
from modules.scorer import calculate_logstrup_score, determine_signal
from modules.telegram_notifier import test_connection
from modules.scheduler import run_update
from modules import icons

logging.basicConfig(level=logging.WARNING)
initialize_db()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drachmann Trading",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.15) !important;
}

/* ── Nav radio (icon-prefixed via CSS) ───────────────────── */
[data-testid="stRadio"] > div { gap: 0 !important; }

[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
    margin: 2px 0 !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    cursor: pointer !important;
}
[data-testid="stRadio"] label:hover {
    background: rgba(59,130,246,0.08) !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(59,130,246,0.13) !important;
    color: #3b82f6 !important;
    font-weight: 600 !important;
}
[data-testid="stRadio"] label > div:first-child { display: none !important; }

/* Icon injected via ::before — each nav item gets its own Lucide SVG */
[data-testid="stRadio"] label::before {
    content: "";
    display: inline-block;
    width: 16px; height: 16px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    margin-right: 10px;
    flex-shrink: 0;
    opacity: 0.7;
    transition: opacity 0.15s;
}
[data-testid="stRadio"] label:has(input:checked)::before { opacity: 1; }

/* 1 — Overview: bar chart */
[data-testid="stRadio"] > div > label:nth-child(1)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666666' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><line x1='18' y1='20' x2='18' y2='10'/><line x1='12' y1='20' x2='12' y2='4'/><line x1='6' y1='20' x2='6' y2='14'/></svg>");
}
[data-testid="stRadio"] > div > label:nth-child(1):has(input:checked)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><line x1='18' y1='20' x2='18' y2='10'/><line x1='12' y1='20' x2='12' y2='4'/><line x1='6' y1='20' x2='6' y2='14'/></svg>");
}

/* 2 — Stock Detail: search */
[data-testid="stRadio"] > div > label:nth-child(2)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666666' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.35-4.35'/></svg>");
}
[data-testid="stRadio"] > div > label:nth-child(2):has(input:checked)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.35-4.35'/></svg>");
}

/* 3 — Signal Log: radio waves */
[data-testid="stRadio"] > div > label:nth-child(3)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666666' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><path d='M4.9 19.1C1 15.2 1 8.8 4.9 4.9'/><path d='M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5'/><circle cx='12' cy='12' r='2'/><path d='M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5'/><path d='M19.1 4.9C23 8.8 23 15.1 19.1 19'/></svg>");
}
[data-testid="stRadio"] > div > label:nth-child(3):has(input:checked)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><path d='M4.9 19.1C1 15.2 1 8.8 4.9 4.9'/><path d='M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5'/><circle cx='12' cy='12' r='2'/><path d='M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5'/><path d='M19.1 4.9C23 8.8 23 15.1 19.1 19'/></svg>");
}

/* 4 — Settings: sliders */
[data-testid="stRadio"] > div > label:nth-child(4)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666666' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><line x1='4' y1='21' x2='4' y2='14'/><line x1='4' y1='10' x2='4' y2='3'/><line x1='12' y1='21' x2='12' y2='12'/><line x1='12' y1='8' x2='12' y2='3'/><line x1='20' y1='21' x2='20' y2='16'/><line x1='20' y1='12' x2='20' y2='3'/><line x1='1' y1='14' x2='7' y2='14'/><line x1='9' y1='8' x2='15' y2='8'/><line x1='17' y1='16' x2='23' y2='16'/></svg>");
}
[data-testid="stRadio"] > div > label:nth-child(4):has(input:checked)::before {
    background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'><line x1='4' y1='21' x2='4' y2='14'/><line x1='4' y1='10' x2='4' y2='3'/><line x1='12' y1='21' x2='12' y2='12'/><line x1='12' y1='8' x2='12' y2='3'/><line x1='20' y1='21' x2='20' y2='16'/><line x1='20' y1='12' x2='20' y2='3'/><line x1='1' y1='14' x2='7' y2='14'/><line x1='9' y1='8' x2='15' y2='8'/><line x1='17' y1='16' x2='23' y2='16'/></svg>");
}

/* ── Metric cards ────────────────────────────────────────── */
[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,0.15) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"] {
    background: #3b82f6 !important;
    border: none !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2563eb !important;
}

/* ── DataFrame ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(128,128,128,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Expander ─────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid rgba(128,128,128,0.15) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ── Divider ──────────────────────────────────────────────── */
hr {
    margin: 18px 0 !important;
}

/* ── Alerts ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* ── Selectbox / slider ───────────────────────────────────── */
[data-testid="stSelectbox"] select,
[data-testid="stSlider"] {
    font-size: 13px !important;
}

/* ── Tabs (score breakdown) ───────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
}

/* ── Caption / small text ─────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    font-size: 12px !important;
    color: #64748b !important;
}

/* ── Code blocks ──────────────────────────────────────────── */
code {
    background: #1a2235 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    padding: 1px 6px !important;
    color: #7dd3fc !important;
}
pre code {
    display: block !important;
    padding: 12px !important;
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Formatters ────────────────────────────────────────────────────────────────
def _pct(v, d=1):
    return f"{v * 100:.{d}f} %" if v is not None else "—"

def _num(v, d=2, suffix=""):
    return f"{v:.{d}f}{suffix}" if v is not None else "—"

def _large(v):
    if v is None: return "—"
    if v >= 1e12: return f"{v/1e12:.2f} T"
    if v >= 1e9:  return f"{v/1e9:.2f} B"
    if v >= 1e6:  return f"{v/1e6:.2f} M"
    return f"{v:.0f}"

def _score_chip(s):
    if s is None or pd.isna(s): return "—"
    if s >= 70: color = "#22c55e"
    elif s >= 45: color = "#f59e0b"
    else: color = "#ef4444"
    return f'<span style="font-weight:700;color:{color};">{s:.0f}</span>'


# ── Cached loaders ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_all_scores():
    return get_latest_scores()

@st.cache_data(ttl=3600)
def load_detail(ticker):
    return fetch_stock_data(ticker)

@st.cache_data(ttl=3600)
def load_price_hist(ticker, period):
    return fetch_price_history(ticker, period)

@st.cache_data(ttl=3600)
def load_score_hist(ticker):
    return get_score_history(ticker, days=90)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:4px 0 12px;">'
        '<span style="font-size:20px;font-weight:800;color:#f1f5f9;'
        'letter-spacing:-0.5px;">Drachmann</span>'
        '<span style="font-size:20px;font-weight:300;color:#3b82f6;"> Trading</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "nav",
        ["Overview", "Stock Detail", "Signal Log", "Settings"],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("Refresh All Data", use_container_width=True):
        with st.spinner("Fetching fresh data … (~2 min)"):
            sigs = run_update(send_telegram=False)
        st.success(f"Done — {len(sigs)} signal(s).")
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown(
        f'<p style="font-size:11px;color:#374151;">'
        f'{icons.clock_icon(11,"#374151")} '
        f'{datetime.now().strftime("%d %b %Y · %H:%M")}<br>'
        f'Buy ≥ {config.BUY_THRESHOLD} &nbsp;·&nbsp; Sell ≤ {config.SELL_THRESHOLD}'
        f'</p>',
        unsafe_allow_html=True,
    )


# ── Load overview data ────────────────────────────────────────────────────────
df = load_all_scores()

# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown(icons.page_header(
        icons.bar_chart(22, "#3b82f6"),
        "Value Investing Overview",
        "Score (0–100): P/E · P/B · ROE · FCF Yield · Dividend · Debt/Equity",
    ), unsafe_allow_html=True)

    if df.empty:
        st.warning("No data yet — click **Refresh All Data** in the sidebar to begin.")
        st.stop()

    # ── Filters ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        min_score = st.slider("Min score", 0, 100, 0, 5)
    with c2:
        sector_opts = ["All"] + sorted(df["sector"].dropna().unique().tolist())
        sector_sel = st.selectbox("Sector", sector_opts)
    with c3:
        index_sel = st.selectbox("Index", ["All", "C25", "MidCap"])
    with c4:
        sig_sel = st.selectbox("Signal", ["All", "STRONG BUY", "BUY", "HOLD", "SELL"])

    filt = df.copy()
    filt["score"] = pd.to_numeric(filt["score"], errors="coerce").fillna(0)
    if min_score:
        filt = filt[filt["score"] >= min_score]
    if sector_sel != "All":
        filt = filt[filt["sector"] == sector_sel]
    if index_sel == "C25":
        filt = filt[filt["ticker"].isin(config.C25_TICKERS)]
    elif index_sel == "MidCap":
        filt = filt[filt["ticker"].isin(config.MIDCAP_TICKERS)]
    if sig_sel != "All":
        filt = filt[filt["signal"] == sig_sel]

    # ── KPI strip ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Stocks tracked",  len(df))
    k2.metric("Strong Buy",      int((df["signal"] == "STRONG BUY").sum()))
    k3.metric("Buy",             int((df["signal"] == "BUY").sum()))
    k4.metric("Sell",            int((df["signal"] == "SELL").sum()))
    k5.metric("Average Score",   f"{df['score'].mean():.1f}")

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    ch1, ch2 = st.columns([3, 1])

    with ch1:
        top = filt.sort_values("score", ascending=False).head(20)
        fig = px.bar(
            top, x="ticker", y="score",
            color="score",
            color_continuous_scale=[
                (0.00, "#ef4444"), (0.45, "#f59e0b"),
                (0.70, "#86efac"), (1.00, "#22c55e"),
            ],
            text="score",
            labels={"score": "Score", "ticker": ""},
            title=f"Top {len(top)} — Score",
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside",
                          marker_line_width=0)
        fig.update_layout(
            height=340, coloraxis_showscale=False,
            yaxis=dict(range=[0, 115], gridcolor="#1e2535"),
            xaxis=dict(tickfont=dict(size=11)),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            title=dict(font=dict(size=14, color="#e2e8f0")),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        sig_counts = df["signal"].value_counts()
        fig_pie = px.pie(
            values=sig_counts.values,
            names=sig_counts.index,
            title="Signal Mix",
            color=sig_counts.index,
            color_discrete_map={
                "STRONG BUY": "#22c55e",
                "BUY":        "#86efac",
                "HOLD":       "#f59e0b",
                "SELL":       "#ef4444",
            },
            hole=0.55,
        )
        fig_pie.update_layout(
            height=340, paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            title=dict(font=dict(size=14, color="#e2e8f0")),
            legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:13px;color:#64748b;margin:4px 0 8px;">'
        f'{icons.layers(14,"#64748b")} Showing {len(filt)} stocks</p>',
        unsafe_allow_html=True,
    )

    display = filt[[
        "ticker", "company_name", "score", "signal",
        "pe", "pb", "roe", "fcf_yield", "div_yield", "de_ratio",
        "current_price", "sector", "date",
    ]].copy()

    display["roe"]       = display["roe"].apply(lambda x: x * 100 if pd.notna(x) else None)
    display["fcf_yield"] = display["fcf_yield"].apply(lambda x: x * 100 if pd.notna(x) else None)
    display["div_yield"] = display["div_yield"].apply(lambda x: x * 100 if pd.notna(x) else None)

    display.rename(columns={
        "ticker": "Ticker", "company_name": "Company", "score": "Score",
        "signal": "Signal", "pe": "P/E (x)", "pb": "P/B (x)",
        "roe": "ROE (%)", "fcf_yield": "FCF Yield (%)", "div_yield": "Div Yield (%)",
        "de_ratio": "D/E (%)", "current_price": "Price",
        "sector": "Sector", "date": "Updated",
    }, inplace=True)

    st.dataframe(
        display,
        use_container_width=True,
        height=520,
        column_config={
            "Score":        st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.0f"),
            "P/E (x)":      st.column_config.NumberColumn(format="%.1f x"),
            "P/B (x)":      st.column_config.NumberColumn(format="%.2f x"),
            "ROE (%)":      st.column_config.NumberColumn(format="%.1f %%"),
            "FCF Yield (%)":st.column_config.NumberColumn(format="%.1f %%"),
            "Div Yield (%)":st.column_config.NumberColumn(format="%.1f %%"),
            "D/E (%)":      st.column_config.NumberColumn(format="%.0f %%"),
            "Price":        st.column_config.NumberColumn(format="%.2f"),
        },
        hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# STOCK DETAIL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Stock Detail":
    st.markdown(icons.page_header(
        icons.search(22, "#3b82f6"),
        "Stock Detail",
        "Live fundamentals, price history, and score breakdown for any Danish ticker",
    ), unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        selected = st.selectbox("Ticker", sorted(config.ALL_TICKERS))
    with col_b:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    if not selected:
        st.stop()

    with st.spinner(f"Loading {selected} …"):
        detail = load_detail(selected)

    if detail is None:
        st.error(f"No data returned for **{selected}** — the ticker may be delisted or temporarily unavailable.")
        st.stop()

    score_result = calculate_logstrup_score(detail)
    score        = score_result["total"]
    components   = score_result["components"]
    signal       = determine_signal(score)
    company      = detail.get("company_name", selected)
    sector       = detail.get("sector") or config.SECTOR_MAP.get(selected, "Unknown")
    currency     = detail.get("currency", "DKK")

    # ── Company header ─────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="margin:12px 0 20px;">'
        f'<h2 style="margin:0;font-size:22px;font-weight:700;">{company}</h2>'
        f'<div style="display:flex;align-items:center;gap:8px;margin-top:6px;">'
        f'<code style="font-size:12px;">{selected}</code>'
        f'<span style="color:#374151;">·</span>'
        f'<span style="font-size:13px;color:#64748b;">{sector}</span>'
        f'<span style="color:#374151;">·</span>'
        f'{icons.signal_badge(signal)}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── KPI strip ─────────────────────────────────────────────────────────────
    kk = st.columns(7)
    kk[0].metric("Score", f"{score:.0f} / 100")
    kk[1].metric("P/E",           _num(detail.get("pe"), 1, " x"))
    kk[2].metric("P/B",           _num(detail.get("pb"), 2, " x"))
    kk[3].metric("ROE",           _pct(detail.get("roe")))
    kk[4].metric("FCF Yield",     _pct(detail.get("fcf_yield")))
    kk[5].metric("Div Yield",     _pct(detail.get("div_yield")))
    kk[6].metric("D/E",          f'{detail["de_ratio"]:.0f} %' if detail.get("de_ratio") is not None else "—")

    st.divider()

    left, right = st.columns([3, 2])

    # ── Left: charts ──────────────────────────────────────────────────────────
    with left:
        st.markdown(
            f'<p style="font-size:13px;font-weight:600;margin-bottom:8px;">'
            f'{icons.activity(14,"#3b82f6")} Price History</p>',
            unsafe_allow_html=True,
        )
        hist = load_price_hist(selected, period)

        if hist is not None and not hist.empty:
            hist["MA50"]  = hist["Close"].rolling(50).mean()
            hist["MA200"] = hist["Close"].rolling(200).mean()

            fig_c = go.Figure()
            fig_c.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"], high=hist["High"],
                low=hist["Low"],   close=hist["Close"],
                name="OHLC",
                increasing_line_color="#22c55e",
                decreasing_line_color="#ef4444",
                increasing_fillcolor="rgba(34,197,94,0.7)",
                decreasing_fillcolor="rgba(239,68,68,0.7)",
            ))
            fig_c.add_trace(go.Scatter(
                x=hist.index, y=hist["MA50"], name="MA 50",
                line=dict(color="#3b82f6", width=1.5, dash="dash"),
            ))
            fig_c.add_trace(go.Scatter(
                x=hist.index, y=hist["MA200"], name="MA 200",
                line=dict(color="#a855f7", width=1.5, dash="dot"),
            ))
            fig_c.update_layout(
                height=380, xaxis_rangeslider_visible=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", size=11),
                legend=dict(orientation="h", y=1.04, font=dict(size=11)),
                xaxis=dict(gridcolor="#1e2535", zeroline=False),
                yaxis=dict(gridcolor="#1e2535", zeroline=False),
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(fig_c, use_container_width=True)

            fig_v = go.Figure(go.Bar(
                x=hist.index, y=hist["Volume"],
                marker_color="rgba(59,130,246,0.3)",
                marker_line_width=0,
            ))
            fig_v.update_layout(
                height=90, showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False),
            )
            st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.warning("Price history unavailable for this ticker.")

        # ── Score history ───────────────────────────────────────────────────
        st.markdown(
            f'<p style="font-size:13px;font-weight:600;margin:12px 0 8px;">'
            f'{icons.award(14,"#3b82f6")} Score — 90-day History</p>',
            unsafe_allow_html=True,
        )
        sh = load_score_hist(selected)
        if not sh.empty:
            fig_sh = go.Figure()
            fig_sh.add_trace(go.Scatter(
                x=sh["date"], y=sh["score"],
                fill="tozeroy",
                fillcolor="rgba(59,130,246,0.08)",
                line=dict(color="#3b82f6", width=2),
                name="Score",
            ))
            fig_sh.add_hline(y=config.BUY_THRESHOLD,  line_dash="dash",
                              line_color="#22c55e", line_width=1,
                              annotation_text="Buy", annotation_font_color="#22c55e")
            fig_sh.add_hline(y=config.SELL_THRESHOLD, line_dash="dash",
                              line_color="#ef4444", line_width=1,
                              annotation_text="Sell", annotation_font_color="#ef4444")
            fig_sh.update_layout(
                height=200, yaxis=dict(range=[0, 105], gridcolor="#1e2535"),
                xaxis=dict(gridcolor="#1e2535"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", size=11), showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig_sh, use_container_width=True)
        else:
            st.info("Score history builds up after multiple daily refreshes.")

    # ── Right: score breakdown + fundamentals ─────────────────────────────────
    with right:
        st.markdown(
            f'<p style="font-size:13px;font-weight:600;margin-bottom:8px;">'
            f'{icons.target(14,"#3b82f6")} Score Breakdown</p>',
            unsafe_allow_html=True,
        )

        # Radar chart
        labels = list(components.keys())
        pcts   = [v["score"] / v["max"] * 100 for v in components.values()]
        fig_r  = go.Figure(go.Scatterpolar(
            r=pcts + [pcts[0]],
            theta=labels + [labels[0]],
            fill="toself",
            line=dict(color="#3b82f6", width=2),
            fillcolor="rgba(59,130,246,0.12)",
            name="Score",
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100],
                                gridcolor="#1e2535", tickfont=dict(color="#64748b", size=10)),
                angularaxis=dict(gridcolor="#1e2535", tickfont=dict(color="#94a3b8", size=11)),
            ),
            showlegend=False, height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Component bars
        for name, comp in components.items():
            pts  = comp["score"]
            maxp = comp["max"]
            val  = comp["value"]
            unit = comp["unit"]

            if val is None:
                disp = "N/A"
            elif unit == "x":
                disp = f"{val:.2f} x"
            elif unit == "pct_raw":
                disp = f"{val:.0f} %"
            else:
                disp = f"{val:.1f} %"

            pct_filled = pts / maxp
            bar_color  = "#22c55e" if pct_filled >= 0.7 else "#f59e0b" if pct_filled >= 0.4 else "#ef4444"

            st.markdown(
                f'<div style="margin:8px 0;">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:12px;color:#94a3b8;margin-bottom:4px;">'
                f'<span>{name}</span>'
                f'<span style="font-weight:600;">{disp} '
                f'<span style="color:{bar_color};">{pts:.0f}</span>/{maxp}</span>'
                f'</div>'
                f'<div style="background:#1e2535;border-radius:4px;height:5px;">'
                f'<div style="background:{bar_color};width:{pct_filled*100:.0f}%;'
                f'height:5px;border-radius:4px;transition:width 0.3s;"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # Fundamentals
        st.markdown(
            f'<p style="font-size:13px;font-weight:600;margin-bottom:8px;">'
            f'{icons.info_icon(14,"#3b82f6")} Key Fundamentals</p>',
            unsafe_allow_html=True,
        )
        rows = [
            ("Price",         f"{detail.get('current_price', '—')} {currency}"),
            ("Market Cap",    _large(detail.get("market_cap"))),
            ("EPS (TTM)",     _num(detail.get("trailing_eps"), 2)),
            ("Book Value",    _num(detail.get("book_value"), 2)),
            ("52W High",      _num(detail.get("week52_high"), 2)),
            ("52W Low",       _num(detail.get("week52_low"), 2)),
            ("Beta",          _num(detail.get("beta"), 2)),
            ("Gross Margin",  _pct(detail.get("gross_margins"))),
            ("Op. Margin",    _pct(detail.get("operating_margins"))),
            ("Net Margin",    _pct(detail.get("profit_margins"))),
            ("Rev. Growth",   _pct(detail.get("revenue_growth"))),
            ("Current Ratio", _num(detail.get("current_ratio"), 2)),
            ("Total Debt",    _large(detail.get("total_debt"))),
            ("Cash",          _large(detail.get("total_cash"))),
        ]
        for label, value in rows:
            la, va = st.columns([1.6, 1])
            la.markdown(f'<span style="font-size:12px;color:#64748b;">{label}</span>', unsafe_allow_html=True)
            va.markdown(f'<span style="font-size:12px;">{value}</span>', unsafe_allow_html=True)

        if detail.get("description"):
            with st.expander("Business description"):
                desc = str(detail["description"])
                st.write(desc[:700] + " …" if len(desc) > 700 else desc)


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL LOG
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Signal Log":
    st.markdown(icons.page_header(
        icons.radio_tower(22, "#3b82f6"),
        "Signal Log",
        "Buy / Sell events generated by the Løgstrup scoring engine",
    ), unsafe_allow_html=True)

    sigs_df = get_signal_log(limit=200)

    if sigs_df.empty:
        st.info(
            f"No signals yet. Events are recorded when a score crosses "
            f"Buy (≥ {config.BUY_THRESHOLD}) or Sell (≤ {config.SELL_THRESHOLD})."
        )
        st.stop()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total signals",    len(sigs_df))
    k2.metric("Buy / Strong Buy", int(sigs_df["signal_type"].isin(["BUY","STRONG BUY"]).sum()))
    k3.metric("Sell",             int((sigs_df["signal_type"] == "SELL").sum()))
    k4.metric("Sent to Telegram", int((sigs_df["sent_to_telegram"] == 1).sum()))

    st.divider()

    type_filter = st.multiselect(
        "Filter",
        ["STRONG BUY", "BUY", "HOLD", "SELL"],
        default=["STRONG BUY", "BUY", "SELL"],
    )
    shown = sigs_df[sigs_df["signal_type"].isin(type_filter)] if type_filter else sigs_df

    for _, row in shown.iterrows():
        sig   = row["signal_type"]
        prev  = row.get("previous_score")
        delta = f"{row['score'] - prev:+.1f}" if (prev and not pd.isna(prev)) else "—"
        sent  = row["sent_to_telegram"]

        tg_html = (
            f'{icons.check_circle(13, "#22c55e")} Sent to Telegram'
            if sent else
            f'{icons.clock_icon(13, "#64748b")} Not sent'
        )

        with st.expander(
            f"{row['company_name']} ({row['ticker']})  ·  "
            f"Score {row['score']:.0f}  ·  {row['timestamp']}"
        ):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
                f'{icons.signal_badge(sig)}'
                f'<span style="font-size:12px;color:#64748b;">{tg_html}</span>'
                f'<span style="font-size:12px;color:#64748b;">Score delta: {delta}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(row["message"])


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Settings":
    st.markdown(icons.page_header(
        icons.settings_gear(22, "#3b82f6"),
        "Settings & Alerts",
        "Telegram configuration, score thresholds, and scheduling",
    ), unsafe_allow_html=True)

    # ── Telegram ─────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:14px;font-weight:600;margin-bottom:10px;">'
        f'{icons.send_icon(14,"#3b82f6")} Telegram Bot</p>',
        unsafe_allow_html=True,
    )

    token_ok = bool(config.TELEGRAM_TOKEN)
    chat_ok  = bool(config.TELEGRAM_CHAT_ID)

    c1, c2 = st.columns(2)
    c1.info(f"Token:    {'Configured' if token_ok else 'Not set'}")
    c2.info(f"Chat ID:  {'Configured' if chat_ok  else 'Not set'}")

    st.markdown("""
Create a `.env` file in the project root:
```
TELEGRAM_TOKEN=110201543:AAHdqTcvCH1vGWJxfSeofSs4tDqQLz...
TELEGRAM_CHAT_ID=123456789
```
**Get your credentials:**
1. Search **@BotFather** on Telegram → `/newbot` → copy the token
2. Message your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates`
   and copy the `chat.id` value
""")

    if st.button("Test Telegram Connection", type="primary"):
        with st.spinner("Sending test message …"):
            ok, msg = test_connection()
        if ok:
            st.success(f"Connection successful — check your Telegram.")
        else:
            st.error(f"Failed: {msg}")

    st.divider()

    # ── Thresholds ────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:14px;font-weight:600;margin-bottom:10px;">'
        f'{icons.target(14,"#3b82f6")} Score Thresholds</p>',
        unsafe_allow_html=True,
    )
    t1, t2, t3 = st.columns(3)
    t1.metric("Strong Buy", config.STRONG_BUY_THRESHOLD, help="STRONG_BUY_THRESHOLD in .env")
    t2.metric("Buy",        config.BUY_THRESHOLD,        help="BUY_THRESHOLD in .env")
    t3.metric("Sell",       config.SELL_THRESHOLD,       help="SELL_THRESHOLD in .env")

    st.divider()

    # ── Manual update ─────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:14px;font-weight:600;margin-bottom:10px;">'
        f'{icons.refresh_cw(14,"#3b82f6")} Manual Update</p>',
        unsafe_allow_html=True,
    )
    m1, m2 = st.columns(2)
    with m1:
        if st.button("Update data — no alerts", use_container_width=True):
            with st.spinner("Fetching all tickers …"):
                sigs = run_update(send_telegram=False)
            st.success(f"Done — {len(sigs)} signal(s).")
            st.cache_data.clear()
    with m2:
        if st.button("Update + Send Telegram alerts", type="primary", use_container_width=True):
            with st.spinner("Fetching and alerting …"):
                sigs = run_update(send_telegram=True)
            st.success(f"Done — {len(sigs)} alert(s) sent.")
            st.cache_data.clear()

    st.divider()

    # ── Cron ──────────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:14px;font-weight:600;margin-bottom:10px;">'
        f'{icons.clock_icon(14,"#3b82f6")} Automated Scheduling</p>',
        unsafe_allow_html=True,
    )
    st.markdown("""
Run every weekday at 08:00 (Copenhagen market opens at 09:00 CET):
```bash
crontab -e
# paste:
0 8 * * 1-5 cd /full/path/to/drachmann-trading && /usr/bin/python3 modules/scheduler.py >> logs/cron.log 2>&1
```
Find your Python path: `which python3`
""")

    st.divider()

    # ── Tickers ───────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:14px;font-weight:600;margin-bottom:10px;">'
        f'{icons.layers(14,"#3b82f6")} Configured Tickers</p>',
        unsafe_allow_html=True,
    )
    col_c25, col_mid = st.columns(2)
    with col_c25:
        st.caption(f"C25 — {len(config.C25_TICKERS)} stocks")
        st.dataframe(pd.DataFrame({"Ticker": config.C25_TICKERS}), height=300, hide_index=True)
    with col_mid:
        st.caption(f"MidCap — {len(config.MIDCAP_TICKERS)} stocks")
        st.dataframe(pd.DataFrame({"Ticker": config.MIDCAP_TICKERS}), height=300, hide_index=True)
    st.caption("Edit config.py to add or remove tickers, then click Refresh All Data.")
