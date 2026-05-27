import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap');

    /* ── Base ─────────────────────────────────────────────── */
    html, body, .main, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Page header ──────────────────────────────────────── */
    .page-header {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #1A3A5C;
        margin-bottom: 0.15rem;
    }
    .page-sub {
        color: #5A7A9A;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #2563A8;
        margin-top: 1.75rem;
        margin-bottom: 0.75rem;
    }

    /* ── Cards ─────────────────────────────────────────────── */
    .card {
        background: #FFFFFF;
        border: 1px solid #C5D8EC;
        border-radius: 14px;
        padding: 1.1rem 1.35rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(91,155,213,0.07);
        transition: box-shadow 0.2s;
    }
    .card:hover { box-shadow: 0 6px 20px rgba(91,155,213,0.15); }

    /* ── Metric card ────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF, #EAF4FB);
        border: 1px solid #C5D8EC;
        border-left: 4px solid #5B9BD5;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #1A3A5C;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #5A7A9A;
        margin-top: 0.3rem;
        font-weight: 500;
    }

    /* ── Status badges ──────────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-blue   { background: #DBEAFE; color: #1D4ED8; }
    .badge-green  { background: #D1FAE5; color: #065F46; }
    .badge-yellow { background: #FEF9C3; color: #92400E; }
    .badge-orange { background: #FFEDD5; color: #9A3412; }
    .badge-red    { background: #FEE2E2; color: #B91C1C; }
    .badge-gray   { background: #E0EAF4; color: #4A6080; }

    /* ── Status inline ──────────────────────────────────────── */
    .status-pending  { background: #FEF9C3; color: #92400E;
                       padding: 3px 12px; border-radius: 999px;
                       font-size: 0.76rem; font-weight: 600; }
    .status-progress { background: #FFEDD5; color: #9A3412;
                       padding: 3px 12px; border-radius: 999px;
                       font-size: 0.76rem; font-weight: 600; }
    .status-done     { background: #D1FAE5; color: #065F46;
                       padding: 3px 12px; border-radius: 999px;
                       font-size: 0.76rem; font-weight: 600; }
    .status-overdue  { background: #FEE2E2; color: #B91C1C;
                       padding: 3px 12px; border-radius: 999px;
                       font-size: 0.76rem; font-weight: 600; }

    /* ── Divider ────────────────────────────────────────────── */
    .divider { border: none; border-top: 1px solid #C5D8EC; margin: 1rem 0; }

    /* ── Streamlit button overrides ─────────────────────────── */
    div.stButton > button {
        border-radius: 10px !important;
        border: 1px solid #A8C8E8 !important;
        background: #FFFFFF !important;
        color: #1A3A5C !important;
        font-weight: 500 !important;
        transition: all 0.18s !important;
    }
    div.stButton > button:hover {
        background: #D6EAF8 !important;
        border-color: #5B9BD5 !important;
        color: #1A3A5C !important;
    }
    div.stButton > button[kind="primary"] {
        background: #5B9BD5 !important;
        color: #FFFFFF !important;
        border-color: #5B9BD5 !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #3A7BBF !important;
        border-color: #3A7BBF !important;
    }

    /* ── Download button ────────────────────────────────────── */
    div.stDownloadButton > button {
        border-radius: 10px !important;
        background: #EAF4FB !important;
        border: 1px solid #5B9BD5 !important;
        color: #1A3A5C !important;
        font-weight: 500 !important;
    }
    div.stDownloadButton > button:hover {
        background: #5B9BD5 !important;
        color: #FFFFFF !important;
    }

    /* ── Sidebar ────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #D6EAF8 !important;
        border-right: 1px solid #A8C8E8;
    }

    /* ── Input fields ───────────────────────────────────────── */
    input, textarea, select {
        border-radius: 8px !important;
    }

    /* ── Expander ───────────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid #C5D8EC !important;
        border-radius: 12px !important;
    }

    /* ── Tabs ───────────────────────────────────────────────── */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 500;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        color: #1A3A5C !important;
        border-bottom: 3px solid #5B9BD5 !important;
    }
    </style>
    """, unsafe_allow_html=True)
