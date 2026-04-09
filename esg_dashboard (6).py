"""
ESG Dashboard — Corporate & Professional
Audience: Sustainability Team
Features: All three ESG pillars + composite score, YoY trends, target tracking
Data input: CSV/Excel upload + PDF report upload
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG Intelligence Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* ── Global reset ── */
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  /* ── Background ── */
  .stApp { background: #F5F4F0; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #1A2332;
    border-right: 1px solid #2D3F55;
  }
  [data-testid="stSidebar"] * { color: #C8D6E5 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stFileUploader label { color: #8FA8C2 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-family: 'DM Serif Display', serif !important;
  }

  /* ── Header band ── */
  .dashboard-header {
    background: #1A2332;
    color: white;
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
  }
  .dashboard-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    font-weight: 400;
    margin: 0;
    line-height: 1.1;
    color: white;
  }
  .dashboard-header .subtitle {
    color: #8FA8C2;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.35rem;
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: white;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    border-left: 4px solid #2E7D55;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  }
  .kpi-card.env  { border-left-color: #2E7D55; }
  .kpi-card.soc  { border-left-color: #1B5C9E; }
  .kpi-card.gov  { border-left-color: #7B3F9E; }
  .kpi-card.comp { border-left-color: #C17D00; }
  .kpi-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #8898AA; margin-bottom: 0.25rem; }
  .kpi-score { font-family: 'DM Serif Display', serif; font-size: 2.6rem; line-height: 1; color: #1A2332; }
  .kpi-delta { font-size: 0.78rem; margin-top: 0.3rem; }
  .kpi-delta.up   { color: #2E7D55; }
  .kpi-delta.down { color: #C0392B; }

  /* ── Section titles ── */
  .section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.35rem;
    color: #1A2332;
    margin: 1.8rem 0 0.8rem;
    border-bottom: 1px solid #DDD8CE;
    padding-bottom: 0.4rem;
  }

  /* ── Progress bar override ── */
  .stProgress > div > div > div { border-radius: 4px; }

  /* ── Metric override ── */
  [data-testid="metric-container"] {
    background: white;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 0.5rem; }
  .stTabs [data-baseweb="tab"] {
    background: white;
    border-radius: 6px 6px 0 0;
    border: 1px solid #DDD8CE;
    border-bottom: none;
    color: #556070;
    font-size: 0.85rem;
    padding: 0.5rem 1.2rem;
  }
  .stTabs [aria-selected="true"] {
    background: #1A2332 !important;
    color: white !important;
    border-color: #1A2332 !important;
  }

  /* ── Upload zone ── */
  [data-testid="stFileUploader"] {
    background: white;
    border-radius: 10px;
    padding: 0.8rem;
  }

  /* ── Divider ── */
  hr { border-color: #DDD8CE; }

  /* ── Status pill ── */
  .pill {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .pill-green  { background: #E6F4ED; color: #2E7D55; }
  .pill-yellow { background: #FEF9E6; color: #C17D00; }
  .pill-red    { background: #FDECEA; color: #C0392B; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS & CHART DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════
COLORS = {
    "env":  "#2E7D55",
    "soc":  "#1B5C9E",
    "gov":  "#7B3F9E",
    "comp": "#C17D00",
    "bg":   "#F5F4F0",
    "dark": "#1A2332",
    "grid": "#E8E4DC",
}

CHART_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans", color="#1A2332", size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["grid"], tickfont=dict(size=11)),
    yaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["grid"], tickfont=dict(size=11)),
)

def score_color(score):
    if score >= 75: return COLORS["env"]
    if score >= 50: return COLORS["comp"]
    return "#C0392B"

def status_pill(pct_of_target):
    if pct_of_target >= 90:
        return '<span class="pill pill-green">On Track</span>'
    if pct_of_target >= 60:
        return '<span class="pill pill-yellow">At Risk</span>'
    return '<span class="pill pill-red">Off Track</span>'

# ═══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA  (replaced when user uploads their own)
# ═══════════════════════════════════════════════════════════════════════════════
YEARS = [2020, 2021, 2022, 2023, 2024]

SAMPLE_ENV = pd.DataFrame({
    "Year":              YEARS,
    "CO2_Emissions_tCO2e":  [48500, 45200, 41000, 36800, 32100],
    "Energy_MWh":            [210000, 198000, 184000, 170000, 155000],
    "Renewable_Energy_pct":  [18, 24, 33, 45, 58],
    "Water_m3":              [95000, 91000, 86000, 80000, 74000],
    "Waste_Recycled_pct":    [42, 51, 59, 67, 74],
    "Score":                 [54, 59, 65, 72, 79],
    "Target":                [60, 63, 67, 72, 78],
})

SAMPLE_SOC = pd.DataFrame({
    "Year":                  YEARS,
    "Total_Employees":       [3400, 3620, 3850, 4100, 4380],
    "Women_Leadership_pct":  [28, 31, 35, 38, 42],
    "Employee_Turnover_pct": [14.2, 13.1, 11.8, 10.4, 9.2],
    "Lost_Time_Injury_Rate": [2.1, 1.7, 1.4, 1.0, 0.7],
    "Training_Hrs_per_FTE":  [22, 26, 29, 33, 38],
    "Score":                 [58, 63, 67, 73, 78],
    "Target":                [62, 65, 68, 74, 80],
})

SAMPLE_GOV = pd.DataFrame({
    "Year":                      YEARS,
    "Board_Independence_pct":    [55, 58, 62, 67, 72],
    "Women_Board_pct":           [22, 25, 28, 33, 38],
    "ESG_Linked_Comp_pct":       [10, 15, 22, 30, 38],
    "Ethics_Training_pct":       [76, 82, 88, 93, 97],
    "Data_Breaches":             [3, 2, 2, 1, 0],
    "Score":                     [52, 58, 64, 70, 76],
    "Target":                    [58, 63, 67, 72, 78],
})

def composite_score(env_s, soc_s, gov_s):
    return round(0.35 * env_s + 0.35 * soc_s + 0.30 * gov_s, 1)

SAMPLE_COMP = pd.DataFrame({
    "Year":  YEARS,
    "Score": [composite_score(e, s, g) for e, s, g in zip(
                SAMPLE_ENV["Score"], SAMPLE_SOC["Score"], SAMPLE_GOV["Score"])],
    "Target": [composite_score(e, s, g) for e, s, g in zip(
                SAMPLE_ENV["Target"], SAMPLE_SOC["Target"], SAMPLE_GOV["Target"])],
})

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌿 ESG Intelligence")
    st.markdown("---")

    company_name = st.text_input("Company Name", value="Acme Corporation")
    reporting_year = st.selectbox("Reporting Year", options=YEARS[::-1], index=0)

    st.markdown("---")
    st.markdown("### Data Upload")

    csv_file = st.file_uploader(
        "Upload ESG Data (CSV / Excel)",
        type=["csv", "xlsx", "xls"],
        help="Columns: Year, plus metrics for each pillar. See the template below."
    )

    pdf_file = st.file_uploader(
        "Upload ESG Report (PDF)",
        type=["pdf"],
        help="PDF parsing requires the 'pdfplumber' library."
    )

    weights = {}
    st.markdown("---")
    st.markdown("### Pillar Weights (%)")
    weights["env"] = st.slider("Environmental", 0, 100, 35)
    weights["soc"] = st.slider("Social",        0, 100, 35)
    weights["gov"] = st.slider("Governance",    0, 100, 30)
    total_w = weights["env"] + weights["soc"] + weights["gov"]
    if total_w != 100:
        st.warning(f"Weights sum to {total_w}% — please adjust to 100%.")

    st.markdown("---")
    st.caption("© 2024 ESG Intelligence Dashboard")

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════
# If user uploads CSV/Excel we try to parse it; otherwise use sample data.
env_df = SAMPLE_ENV.copy()
soc_df = SAMPLE_SOC.copy()
gov_df = SAMPLE_GOV.copy()

if csv_file is not None:
    try:
        if csv_file.name.endswith(".csv"):
            uploaded = pd.read_csv(csv_file)
        else:
            uploaded = pd.read_excel(csv_file)
        st.sidebar.success(f"✅ Loaded {len(uploaded)} rows")
        # Simple heuristic: if it has a 'Pillar' column, split; else show as-is
        if "Pillar" in uploaded.columns:
            env_df = uploaded[uploaded["Pillar"].str.lower() == "environmental"].reset_index(drop=True)
            soc_df = uploaded[uploaded["Pillar"].str.lower() == "social"].reset_index(drop=True)
            gov_df = uploaded[uploaded["Pillar"].str.lower() == "governance"].reset_index(drop=True)
        else:
            st.sidebar.info("Couldn't split by pillar — using uploaded data for overview only.")
    except Exception as ex:
        st.sidebar.error(f"Parse error: {ex}")

# Recalculate composite with custom weights
def recalc_comp(env_d, soc_d, gov_d, w):
    if total_w != 100:
        return SAMPLE_COMP.copy()
    years = env_d["Year"].tolist()
    scores  = [(w["env"]/100)*e + (w["soc"]/100)*s + (w["gov"]/100)*g
               for e, s, g in zip(env_d["Score"], soc_d["Score"], gov_d["Score"])]
    targets = [(w["env"]/100)*e + (w["soc"]/100)*s + (w["gov"]/100)*g
               for e, s, g in zip(env_d["Target"], soc_d["Target"], gov_d["Target"])]
    return pd.DataFrame({"Year": years, "Score": [round(x,1) for x in scores],
                         "Target": [round(x,1) for x in targets]})

comp_df = recalc_comp(env_df, soc_df, gov_df, weights)

# Latest-year helper
def latest(df, col):
    row = df[df["Year"] == reporting_year]
    if row.empty: row = df.iloc[[-1]]
    return row[col].values[0]

def prev_year_val(df, col):
    yr = reporting_year - 1
    row = df[df["Year"] == yr]
    if row.empty: return None
    return row[col].values[0]

def delta_str(curr, prev, higher_better=True):
    if prev is None: return ""
    d = curr - prev
    sign = "▲" if d > 0 else "▼"
    good = (d > 0) == higher_better
    css = "up" if good else "down"
    return f'<span class="kpi-delta {css}">{sign} {abs(d):.1f} vs prior year</span>'

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dashboard-header">
  <div>
    <div class="subtitle">ESG Intelligence Dashboard</div>
    <h1>{company_name}</h1>
  </div>
  <div style="margin-left:auto; text-align:right;">
    <div class="subtitle">Reporting Year</div>
    <span style="font-family:'DM Serif Display',serif;font-size:2rem;color:white;">{reporting_year}</span>
  </div>
</div>
""", unsafe_allow_html=True)

if pdf_file:
    st.info(f"📄 PDF uploaded: **{pdf_file.name}** — narrative content noted. "
            "Install `pdfplumber` and extend this app to parse full text.", icon="ℹ️")

# ═══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ═══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, kind, label, score, prev_score, target, higher_better=True):
    pct = round(score / target * 100) if target else 0
    with col:
        st.markdown(f"""
        <div class="kpi-card {kind}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-score">{score:.0f}<span style="font-size:1rem;color:#8898AA">/100</span></div>
          {delta_str(score, prev_score, higher_better)}
          <div style="margin-top:0.5rem;font-size:0.72rem;color:#8898AA;">
            Target: {target:.0f} &nbsp;·&nbsp; {status_pill(pct)}
          </div>
        </div>
        """, unsafe_allow_html=True)

kpi_card(k1, "env",  "Environmental",  latest(env_df,  "Score"), prev_year_val(env_df,  "Score"), latest(env_df,  "Target"))
kpi_card(k2, "soc",  "Social",         latest(soc_df,  "Score"), prev_year_val(soc_df,  "Score"), latest(soc_df,  "Target"))
kpi_card(k3, "gov",  "Governance",     latest(gov_df,  "Score"), prev_year_val(gov_df,  "Score"), latest(gov_df,  "Target"))
kpi_card(k4, "comp", "Composite ESG",  latest(comp_df, "Score"), prev_year_val(comp_df, "Score"), latest(comp_df, "Target"))

st.markdown("")

# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE SCORE TREND  +  RADAR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Overall ESG Performance</div>', unsafe_allow_html=True)

c_trend, c_radar = st.columns([3, 2])

with c_trend:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=comp_df["Year"], y=comp_df["Target"],
        mode="lines", name="Target",
        line=dict(color="#DDD8CE", width=2, dash="dash"),
        fill=None,
    ))
    fig.add_trace(go.Scatter(
        x=comp_df["Year"], y=comp_df["Score"],
        mode="lines+markers", name="Composite Score",
        line=dict(color=COLORS["comp"], width=3),
        marker=dict(size=8, color=COLORS["comp"]),
        fill="tonexty", fillcolor="rgba(193,125,0,0.08)",
    ))
    fig.update_layout(**CHART_LAYOUT, title="Composite ESG Score vs Target",
                      legend=dict(orientation="h", y=-0.15),
                      yaxis=dict(**CHART_LAYOUT["yaxis"], range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

with c_radar:
    cats   = ["Environmental", "Social", "Governance"]
    scores = [latest(env_df, "Score"), latest(soc_df, "Score"), latest(gov_df, "Score")]
    targets= [latest(env_df, "Target"), latest(soc_df, "Target"), latest(gov_df, "Target")]

    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=targets + [targets[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(221,216,206,0.3)",
        line=dict(color="#DDD8CE", dash="dash"), name="Target"
    ))
    fig_r.add_trace(go.Scatterpolar(
        r=scores + [scores[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(193,125,0,0.18)",
        line=dict(color=COLORS["comp"], width=2.5), name="Actual",
        marker=dict(size=7, color=COLORS["comp"])
    ))
    fig_r.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10), gridcolor=COLORS["grid"]),
            angularaxis=dict(tickfont=dict(size=12, color=COLORS["dark"])),
            bgcolor="white",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12),
        margin=dict(l=16, r=16, t=36, b=16),
        title="Pillar Balance",
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_r, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Pillar Deep-Dive</div>', unsafe_allow_html=True)

tab_e, tab_s, tab_g = st.tabs(["🌱  Environmental", "👥  Social", "🏛️  Governance"])

# ──────────────────────────────────────────────────────────────────────────────
# ENVIRONMENTAL
# ──────────────────────────────────────────────────────────────────────────────
with tab_e:
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_bar(x=env_df["Year"], y=env_df["CO2_Emissions_tCO2e"],
                    name="CO₂ Emissions (tCO₂e)", marker_color=COLORS["env"],
                    opacity=0.85)
        fig.update_layout(**CHART_LAYOUT, title="Scope 1+2 CO₂ Emissions")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=env_df["Year"], y=env_df["Renewable_Energy_pct"],
                                  mode="lines+markers", name="Renewable Energy %",
                                  line=dict(color=COLORS["env"], width=3),
                                  marker=dict(size=8)))
        fig2.update_layout(**CHART_LAYOUT, title="Renewable Energy Mix (%)",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%", range=[0,100]))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        fig3.add_bar(x=env_df["Year"], y=env_df["Water_m3"],
                     marker_color="#5AA9C2", name="Water Consumption (m³)")
        fig3.update_layout(**CHART_LAYOUT, title="Water Consumption (m³)")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=env_df["Year"], y=env_df["Waste_Recycled_pct"],
                                  mode="lines+markers", name="Waste Recycled %",
                                  line=dict(color="#8BC34A", width=3),
                                  fill="tozeroy", fillcolor="rgba(139,195,74,0.12)",
                                  marker=dict(size=8)))
        fig4.update_layout(**CHART_LAYOUT, title="Waste Recycled (%)",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%", range=[0,100]))
        st.plotly_chart(fig4, use_container_width=True)

    # Target tracker
    st.markdown("#### Environmental Target Tracker")
    env_targets = {
        "CO₂ Emissions":      (latest(env_df, "CO2_Emissions_tCO2e"), 25000, False),
        "Renewable Energy %": (latest(env_df, "Renewable_Energy_pct"), 75, True),
        "Water Consumption":  (latest(env_df, "Water_m3"), 60000, False),
        "Waste Recycled %":   (latest(env_df, "Waste_Recycled_pct"), 85, True),
    }
    for metric, (val, tgt, higher) in env_targets.items():
        pct = min(val / tgt, 1.0) if higher else min(tgt / val, 1.0)
        pct = round(pct * 100)
        pill = status_pill(pct)
        cols = st.columns([2, 3, 1, 1])
        cols[0].write(metric)
        cols[1].progress(pct / 100)
        cols[2].write(f"{val:,.0f}")
        cols[3].markdown(f"Target: {tgt:,.0f}", unsafe_allow_html=False)

# ──────────────────────────────────────────────────────────────────────────────
# SOCIAL
# ──────────────────────────────────────────────────────────────────────────────
with tab_s:
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_bar(x=soc_df["Year"], y=soc_df["Total_Employees"],
                    marker_color=COLORS["soc"], name="Total Employees")
        fig.update_layout(**CHART_LAYOUT, title="Workforce Size")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=soc_df["Year"], y=soc_df["Women_Leadership_pct"],
                                  mode="lines+markers", name="Women in Leadership %",
                                  line=dict(color=COLORS["soc"], width=3),
                                  marker=dict(size=8)))
        fig2.update_layout(**CHART_LAYOUT, title="Women in Leadership (%)",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%", range=[0,60]))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Bar(x=soc_df["Year"], y=soc_df["Training_Hrs_per_FTE"],
                              name="Training Hrs/FTE", marker_color="#64B5F6"), secondary_y=False)
        fig3.add_trace(go.Scatter(x=soc_df["Year"], y=soc_df["Employee_Turnover_pct"],
                                  mode="lines+markers", name="Turnover %",
                                  line=dict(color="#EF5350", width=2.5), marker=dict(size=7)),
                       secondary_y=True)
        fig3.update_layout(**CHART_LAYOUT, title="Training vs Employee Turnover")
        fig3.update_yaxes(title_text="Hrs/FTE", secondary_y=False, gridcolor=COLORS["grid"])
        fig3.update_yaxes(title_text="Turnover %", secondary_y=True, showgrid=False,
                          ticksuffix="%")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=soc_df["Year"], y=soc_df["Lost_Time_Injury_Rate"],
                                  mode="lines+markers", name="LTIR",
                                  line=dict(color="#FF8A65", width=3),
                                  fill="tozeroy", fillcolor="rgba(255,138,101,0.12)",
                                  marker=dict(size=8)))
        fig4.update_layout(**CHART_LAYOUT, title="Lost Time Injury Rate (per 200k hrs)")
        st.plotly_chart(fig4, use_container_width=True)

    # Target tracker
    st.markdown("#### Social Target Tracker")
    soc_targets = {
        "Women in Leadership %":    (latest(soc_df, "Women_Leadership_pct"), 50, True),
        "Employee Turnover %":      (latest(soc_df, "Employee_Turnover_pct"), 8,  False),
        "Lost Time Injury Rate":    (latest(soc_df, "Lost_Time_Injury_Rate"), 0.5, False),
        "Training Hrs per FTE":     (latest(soc_df, "Training_Hrs_per_FTE"), 45,  True),
    }
    for metric, (val, tgt, higher) in soc_targets.items():
        pct = min(val / tgt, 1.0) if higher else min(tgt / val, 1.0)
        pct = round(pct * 100)
        cols = st.columns([2, 3, 1, 1])
        cols[0].write(metric)
        cols[1].progress(min(pct/100, 1.0))
        cols[2].write(f"{val}")
        cols[3].write(f"Target: {tgt}")

# ──────────────────────────────────────────────────────────────────────────────
# GOVERNANCE
# ──────────────────────────────────────────────────────────────────────────────
with tab_g:
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gov_df["Year"], y=gov_df["Board_Independence_pct"],
                                 mode="lines+markers", name="Board Independence %",
                                 line=dict(color=COLORS["gov"], width=3),
                                 marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=gov_df["Year"], y=gov_df["Women_Board_pct"],
                                 mode="lines+markers", name="Women on Board %",
                                 line=dict(color="#AB47BC", width=3, dash="dot"),
                                 marker=dict(size=8)))
        fig.update_layout(**CHART_LAYOUT, title="Board Composition (%)",
                          yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%", range=[0,100]),
                          legend=dict(orientation="h", y=-0.18))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_bar(x=gov_df["Year"], y=gov_df["ESG_Linked_Comp_pct"],
                     marker_color=COLORS["gov"], name="ESG-Linked Comp %")
        fig2.update_layout(**CHART_LAYOUT, title="ESG-Linked Executive Compensation (%)",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%"))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=gov_df["Year"], y=gov_df["Ethics_Training_pct"],
                                  mode="lines+markers", name="Ethics Training Coverage %",
                                  line=dict(color="#66BB6A", width=3),
                                  marker=dict(size=8),
                                  fill="tozeroy", fillcolor="rgba(102,187,106,0.12)"))
        fig3.update_layout(**CHART_LAYOUT, title="Ethics & Compliance Training Coverage (%)",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], ticksuffix="%", range=[60,105]))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure()
        fig4.add_bar(x=gov_df["Year"], y=gov_df["Data_Breaches"],
                     marker_color="#EF5350", name="Data Breaches")
        fig4.update_layout(**CHART_LAYOUT, title="Reported Data Breaches",
                           yaxis=dict(**CHART_LAYOUT["yaxis"], dtick=1))
        st.plotly_chart(fig4, use_container_width=True)

    # Target tracker
    st.markdown("#### Governance Target Tracker")
    gov_targets = {
        "Board Independence %":    (latest(gov_df, "Board_Independence_pct"), 80,  True),
        "Women on Board %":        (latest(gov_df, "Women_Board_pct"),        40,  True),
        "ESG-Linked Comp %":       (latest(gov_df, "ESG_Linked_Comp_pct"),    50,  True),
        "Ethics Training Coverage":(latest(gov_df, "Ethics_Training_pct"),    100, True),
    }
    for metric, (val, tgt, higher) in gov_targets.items():
        pct = min(val / tgt, 1.0) if higher else min(tgt / val, 1.0)
        pct = round(pct * 100)
        cols = st.columns([2, 3, 1, 1])
        cols[0].write(metric)
        cols[1].progress(min(pct/100, 1.0))
        cols[2].write(f"{val}")
        cols[3].write(f"Target: {tgt}")

# ═══════════════════════════════════════════════════════════════════════════════
# SCORE PROGRESSION  (all pillars)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Score Trends — All Pillars</div>', unsafe_allow_html=True)

fig_all = go.Figure()
for df, label, color in [
    (env_df, "Environmental", COLORS["env"]),
    (soc_df, "Social",        COLORS["soc"]),
    (gov_df, "Governance",    COLORS["gov"]),
    (comp_df,"Composite",     COLORS["comp"]),
]:
    fig_all.add_trace(go.Scatter(
        x=df["Year"], y=df["Score"],
        mode="lines+markers", name=label,
        line=dict(color=color, width=2.5 if label != "Composite" else 3.5),
        marker=dict(size=7 if label != "Composite" else 10),
    ))
    fig_all.add_trace(go.Scatter(
        x=df["Year"], y=df["Target"],
        mode="lines", name=f"{label} Target",
        line=dict(color=color, width=1.5, dash="dot"),
        showlegend=False, opacity=0.5,
    ))

fig_all.update_layout(
    **CHART_LAYOUT,
    title="ESG Score vs Target — All Pillars",
    yaxis=dict(**CHART_LAYOUT["yaxis"], range=[0, 100]),
    legend=dict(orientation="h", y=-0.15),
    height=380,
)
st.plotly_chart(fig_all, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RAW DATA EXPANDER
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📊 View / Download Raw Data"):
    tabs = st.tabs(["Environmental", "Social", "Governance", "Composite"])
    for tab, df, name in zip(tabs,
                             [env_df, soc_df, gov_df, comp_df],
                             ["Environmental", "Social", "Governance", "Composite"]):
        with tab:
            st.dataframe(df, use_container_width=True)
            csv_bytes = df.to_csv(index=False).encode()
            st.download_button(f"⬇ Download {name} CSV", data=csv_bytes,
                               file_name=f"esg_{name.lower()}_{reporting_year}.csv",
                               mime="text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#8898AA;font-size:0.78rem;'>"
    f"ESG Intelligence Dashboard &nbsp;·&nbsp; {company_name} &nbsp;·&nbsp; "
    f"Reporting Year {reporting_year} &nbsp;·&nbsp; Built with Streamlit"
    f"</div>",
    unsafe_allow_html=True
)
