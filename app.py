"""
Indian Roads Accident Data Analysis Dashboard
================================================
A single-page Streamlit dashboard for exploring the Indian Roads accident
dataset — built with Python, Pandas, NumPy and Plotly only, using native
Streamlit components (no custom CSS/HTML).

Run with:
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Indian Roads Accident Analysis Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "indian_roads_dataset.csv"


# --------------------------------------------------------------------------
# DATA LOADING
# --------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading accident records...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = df["date"].dt.month_name()
        df["month_num"] = df["date"].dt.month
        df["year"] = df["date"].dt.year

    # Fill categorical-style blank/NaN fields with a readable label instead
    # of dropping rows, so a record without a festival tag is still counted.
    if "festival" in df.columns:
        df["festival"] = df["festival"].fillna("No Festival")

    return df


try:
    raw_df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find `{DATA_PATH}`. Place the dataset CSV in the same "
        "folder as app.py and reload."
    )
    st.stop()

# Detect columns that exist, so the dashboard adapts gracefully if the
# dataset schema changes.
COLS = raw_df.columns.tolist()


def has(col: str) -> bool:
    return col in COLS


# --------------------------------------------------------------------------
# SIDEBAR — FILTERS
# --------------------------------------------------------------------------
def reset_filters():
    for key in list(st.session_state.keys()):
        if key.startswith("f_"):
            del st.session_state[key]


with st.sidebar:
    st.title("🚦 Control Panel")
    st.caption("Indian Roads Accident Dataset")
    st.divider()

    st.subheader("📦 Dataset Summary")
    st.write(f"**Total Records:** {len(raw_df):,}")
    if has("date"):
        st.write(
            f"**Date Range:** {raw_df['date'].min().date()} → "
            f"{raw_df['date'].max().date()}"
        )
    if has("state"):
        st.write(f"**States Covered:** {raw_df['state'].nunique()}")
    if has("city"):
        st.write(f"**Cities Covered:** {raw_df['city'].nunique()}")

    st.divider()
    st.subheader("🔍 Advanced Filters")

    def multiselect_filter(label, col, key):
        if has(col):
            options = sorted(raw_df[col].dropna().unique().tolist())
            return st.multiselect(label, options, default=[], key=key)
        return []

    sel_state = multiselect_filter("State", "state", "f_state")
    sel_city = multiselect_filter("City", "city", "f_city")
    sel_road = multiselect_filter("Road Type", "road_type", "f_road")
    sel_weather = multiselect_filter("Weather", "weather", "f_weather")
    sel_severity = multiselect_filter("Severity", "accident_severity", "f_sev")
    sel_cause = multiselect_filter("Cause", "cause", "f_cause")
    sel_day = multiselect_filter("Day of Week", "day_of_week", "f_day")
    sel_festival = multiselect_filter("Festival", "festival", "f_fest")

    date_range = None
    if has("date"):
        min_d, max_d = raw_df["date"].min().date(), raw_df["date"].max().date()
        date_range = st.date_input(
            "Date Range", value=(min_d, max_d), min_value=min_d,
            max_value=max_d, key="f_date"
        )

    st.divider()
    st.button("♻️ Reset All Filters", on_click=reset_filters, use_container_width=True)


# --------------------------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if sel_state and has("state"):
        out = out[out["state"].isin(sel_state)]
    if sel_city and has("city"):
        out = out[out["city"].isin(sel_city)]
    if sel_road and has("road_type"):
        out = out[out["road_type"].isin(sel_road)]
    if sel_weather and has("weather"):
        out = out[out["weather"].isin(sel_weather)]
    if sel_severity and has("accident_severity"):
        out = out[out["accident_severity"].isin(sel_severity)]
    if sel_cause and has("cause"):
        out = out[out["cause"].isin(sel_cause)]
    if sel_day and has("day_of_week"):
        out = out[out["day_of_week"].isin(sel_day)]
    if sel_festival and has("festival"):
        out = out[out["festival"].isin(sel_festival)]
    if date_range and has("date") and isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        out = out[(out["date"] >= pd.Timestamp(start)) & (out["date"] <= pd.Timestamp(end))]
    return out


df = apply_filters(raw_df)

with st.sidebar:
    st.subheader("⚡ Quick Statistics (Filtered)")
    st.metric("Records in View", f"{len(df):,}")
    if has("accident_severity") and len(df):
        st.metric("Fatal Accidents", f"{(df['accident_severity']=='fatal').sum():,}")

if df.empty:
    st.warning("No records match the selected filters. Adjust filters in the sidebar.")
    st.stop()


# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------
# UNIVERSITY HEADER
col1, col2 = st.columns([0.7, 5], gap="small")

with col1:
    st.image("sbbsu_logo.png", width=85)

with col2:
    st.markdown("""
        <div style="padding-top: 12px; margin-left: -15px;">
            <h2 style="
                color: #FFD700;
                font-size: 27px;
                margin: 0;
                padding: 0;
                white-space: nowrap;">
                SANT BABA BHAG SINGH UNIVERSITY
            </h2>
            <p style="color: #CCCCCC; margin-top: 5px;">
                Khiala, Jalandhar, Punjab
            </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

st.divider()
st.title("🚦 Indian Roads Accident Analysis Dashboard")
st.caption("Data-driven exploration of road accident patterns, severity, causes and risk factors across India.")

badge_cols = st.columns(4)
badge_cols[0].markdown("👤 **Mandeep Kumar**")
badge_cols[1].markdown("🎓 **B.Tech CSE (AI & ML)**")
badge_cols[2].markdown("🆔 **Roll No. 24801042**")
badge_cols[3].markdown("🏫 **Sant Baba Bhag Singh University,Khiala,Distt. Jalandhar**")

st.divider()


# --------------------------------------------------------------------------
# KPI CARDS (native st.metric inside bordered containers)
# --------------------------------------------------------------------------
st.header("📊 Key Performance Indicators")

total_records = len(df)
total_fatal = (df["accident_severity"] == "fatal").sum() if has("accident_severity") else 0
total_major = (df["accident_severity"] == "major").sum() if has("accident_severity") else 0
total_minor = (df["accident_severity"] == "minor").sum() if has("accident_severity") else 0
states_covered = df["state"].nunique() if has("state") else 0
road_types_covered = df["road_type"].nunique() if has("road_type") else 0
peak_month = df["month"].value_counts().idxmax() if has("month") and len(df) else "N/A"
most_dangerous_state = (
    df[df["accident_severity"] == "fatal"]["state"].value_counts().idxmax()
    if has("state") and has("accident_severity") and total_fatal > 0
    else "N/A"
)
most_common_road = df["road_type"].value_counts().idxmax() if has("road_type") and len(df) else "N/A"
most_common_cause = df["cause"].value_counts().idxmax() if has("cause") and len(df) else "N/A"
avg_casualties = df["casualties"].mean() if has("casualties") else 0
peak_hour = int(df["hour"].value_counts().idxmax()) if has("hour") and len(df) else "N/A"

row1 = st.columns(5)
kpi_row1 = [
    ("📁 Total Records", f"{total_records:,}"),
    ("💀 Fatal Accidents", f"{total_fatal:,}"),
    ("🚨 Major / Serious", f"{total_major:,}"),
    ("⚠️ Minor Accidents", f"{total_minor:,}"),
    ("🗺️ States Covered", f"{states_covered}"),
]
for col, (label, value) in zip(row1, kpi_row1):
    with col.container(border=True):
        st.metric(label, value)

row2 = st.columns(5)
kpi_row2 = [
    ("🛣️ Road Types", f"{road_types_covered}"),
    ("📅 Peak Accident Month", f"{peak_month}"),
    ("🔥 Most Dangerous State", f"{most_dangerous_state}"),
    ("🚧 Top Road Type", f"{most_common_road.title() if most_common_road != 'N/A' else most_common_road}"),
    ("🧍 Avg. Casualties / Accident", f"{avg_casualties:.2f}"),
]
for col, (label, value) in zip(row2, kpi_row2):
    with col.container(border=True):
        st.metric(label, value)

st.write("")


# --------------------------------------------------------------------------
# INSIGHT HELPER
# --------------------------------------------------------------------------
def insight(text):
    st.info(f"💡 **Insight:** {text}")


# --------------------------------------------------------------------------
# TABS — CHARTS
# --------------------------------------------------------------------------
st.header("📈 Interactive Analysis")

tab_overview, tab_severity, tab_time, tab_geo, tab_causes, tab_explorer = st.tabs(
    ["🏁 Overview", "🚨 Severity", "⏱️ Time Patterns", "🗺️ Geography", "🌦️ Causes & Conditions", "🔎 Data Explorer"]
)

# ---- TAB 1: OVERVIEW ----
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        if has("road_type"):
            counts = df["road_type"].value_counts().reset_index()
            counts.columns = ["road_type", "count"]
            fig = px.bar(
                counts, x="road_type", y="count", color="road_type",
                title="Accidents by Road Type",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                text="count",
            )
            fig.update_layout(showlegend=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            top_road = counts.iloc[0]["road_type"]
            insight(f"**{top_road.title()}** roads report the highest accident count in the current selection.")

    with c2:
        if has("accident_severity"):
            sev_counts = df["accident_severity"].value_counts().reset_index()
            sev_counts.columns = ["severity", "count"]
            fig = px.pie(
                sev_counts, names="severity", values="count", hole=0.45,
                title="Accident Severity Distribution",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            share_fatal = 100 * total_fatal / total_records if total_records else 0
            insight(f"Fatal accidents make up **{share_fatal:.1f}%** of all recorded accidents in the current selection.")

    c3, c4 = st.columns(2)
    with c3:
        if has("vehicles_involved"):
            fig = px.histogram(
                df, x="vehicles_involved", nbins=df["vehicles_involved"].nunique(),
                title="Distribution of Vehicles Involved per Accident",
                color_discrete_sequence=["#2E5AAC"],
            )
            fig.update_layout(template="plotly_white", bargap=0.15)
            st.plotly_chart(fig, use_container_width=True)
            insight(f"Most accidents involve around **{int(df['vehicles_involved'].mode()[0])}** vehicle(s).")

    with c4:
        if has("risk_score"):
            fig = px.box(
                df, x="accident_severity" if has("accident_severity") else None,
                y="risk_score", color="accident_severity" if has("accident_severity") else None,
                title="Risk Score Spread by Severity",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            insight(f"Average risk score across current records is **{df['risk_score'].mean():.2f}** (scale 0–1).")

# ---- TAB 2: SEVERITY ----
with tab_severity:
    c1, c2 = st.columns(2)

    with c1:
        if has("cause") and has("accident_severity"):
            grp = df.groupby(["cause", "accident_severity"]).size().reset_index(name="count")
            fig = px.bar(
                grp, x="cause", y="count", color="accident_severity", barmode="stack",
                title="Severity Breakdown by Cause",
                color_discrete_sequence=["#E3A008", "#2E5AAC", "#1B3B6F"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            insight(f"**{most_common_cause.title()}** is the most frequently recorded cause overall.")

    with c2:
        if has("road_type") and has("accident_severity"):
            grp = df.groupby(["road_type", "accident_severity"]).size().reset_index(name="count")
            fig = px.treemap(
                grp, path=["road_type", "accident_severity"], values="count",
                title="Road Type → Severity Breakdown",
                color="count", color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)
            insight("The treemap highlights which road type carries the heaviest concentration of severe accidents.")

    c3, c4 = st.columns(2)
    with c3:
        if has("casualties") and has("accident_severity"):
            fig = px.violin(
                df, x="accident_severity", y="casualties", box=True, points=False,
                title="Casualties Distribution by Severity",
                color="accident_severity",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if has("traffic_signal") and has("accident_severity"):
            df_sig = df.copy()
            df_sig["traffic_signal"] = df_sig["traffic_signal"].map({1: "Signal Present", 0: "No Signal"})
            grp = df_sig.groupby(["traffic_signal", "accident_severity"]).size().reset_index(name="count")
            fig = px.bar(
                grp, x="traffic_signal", y="count", color="accident_severity", barmode="group",
                title="Severity by Traffic Signal Presence",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

# ---- TAB 3: TIME PATTERNS ----
with tab_time:
    c1, c2 = st.columns(2)

    with c1:
        if has("hour"):
            hour_counts = df["hour"].value_counts().sort_index().reset_index()
            hour_counts.columns = ["hour", "count"]
            fig = px.line(
                hour_counts, x="hour", y="count", markers=True,
                title="Accidents by Hour of Day",
                color_discrete_sequence=["#1B3B6F"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            insight(f"Accident frequency peaks around **{peak_hour}:00 hrs**.")

    with c2:
        if has("day_of_week"):
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_counts = df["day_of_week"].value_counts().reindex(day_order).fillna(0).reset_index()
            day_counts.columns = ["day", "count"]
            fig = px.bar(
                day_counts, x="day", y="count", title="Accidents by Day of Week",
                color="count", color_continuous_scale="Blues",
            )
            fig.update_layout(template="plotly_white", coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            top_day = day_counts.loc[day_counts["count"].idxmax(), "day"]
            insight(f"**{top_day}** records the highest number of accidents among all weekdays.")

    c3, c4 = st.columns(2)
    with c3:
        if has("month"):
            month_order = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"]
            month_counts = df["month"].value_counts().reindex(month_order).fillna(0).reset_index()
            month_counts.columns = ["month", "count"]
            fig = px.line(
                month_counts, x="month", y="count", markers=True,
                title="Monthly Accident Trend", color_discrete_sequence=["#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if has("is_peak_hour") and has("accident_severity"):
            df_peak = df.copy()
            df_peak["is_peak_hour"] = df_peak["is_peak_hour"].map({1: "Peak Hour", 0: "Non-Peak Hour"})
            grp = df_peak.groupby(["is_peak_hour", "accident_severity"]).size().reset_index(name="count")
            fig = px.bar(
                grp, x="is_peak_hour", y="count", color="accident_severity", barmode="group",
                title="Peak vs Non-Peak Hour Severity",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

# ---- TAB 4: GEOGRAPHY ----
with tab_geo:
    c1, c2 = st.columns(2)

    with c1:
        if has("state"):
            state_counts = df["state"].value_counts().reset_index()
            state_counts.columns = ["state", "count"]
            fig = px.bar(
                state_counts, x="count", y="state", orientation="h",
                title="Accidents by State", color="count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(template="plotly_white", coloraxis_showscale=False,
                               yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)
            insight(f"**{state_counts.iloc[0]['state']}** reports the highest number of accidents in the current selection.")

    with c2:
        if has("latitude") and has("longitude"):
            sample = df.sample(min(2000, len(df)), random_state=42)
            fig = px.scatter_mapbox(
                sample, lat="latitude", lon="longitude",
                color="accident_severity" if has("accident_severity") else None,
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
                zoom=3.5, height=420, title="Geographic Spread of Accidents",
                mapbox_style="carto-positron",
            )
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    if has("city") and has("state"):
        grp = df.groupby(["state", "city"]).size().reset_index(name="count")
        fig = px.sunburst(
            grp, path=["state", "city"], values="count",
            title="State → City Accident Breakdown",
            color="count", color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 5: CAUSES & CONDITIONS ----
with tab_causes:
    c1, c2 = st.columns(2)

    with c1:
        if has("weather") and has("cause"):
            grp = df.groupby(["weather", "cause"]).size().reset_index(name="count")
            fig = px.density_heatmap(
                grp, x="weather", y="cause", z="count",
                title="Weather vs Cause Heatmap", color_continuous_scale="Blues",
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if has("visibility") and has("accident_severity"):
            grp = df.groupby(["visibility", "accident_severity"]).size().reset_index(name="count")
            fig = px.bar(
                grp, x="visibility", y="count", color="accident_severity", barmode="group",
                title="Severity by Visibility Conditions",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            insight("Low-visibility conditions tend to coincide with a higher share of severe accidents.")

    c3, c4 = st.columns(2)
    with c3:
        if has("temperature") and has("risk_score"):
            fig = px.scatter(
                df, x="temperature", y="risk_score",
                color="accident_severity" if has("accident_severity") else None,
                title="Temperature vs Risk Score",
                color_discrete_sequence=["#1B3B6F", "#2E5AAC", "#E3A008"],
                opacity=0.6,
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if has("festival"):
            fest_counts = df["festival"].value_counts().reset_index()
            fest_counts.columns = ["festival", "count"]
            fig = px.pie(
                fest_counts, names="festival", values="count", hole=0.4,
                title="Accidents: Festival vs Non-Festival Days",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

# ---- TAB 6: DATA EXPLORER ----
with tab_explorer:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(50), use_container_width=True)

    e1, e2 = st.columns(2)
    with e1:
        st.subheader("Column Information")
        info_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isna().sum().values,
            "Unique Values": [df[c].nunique() for c in df.columns],
        })
        st.dataframe(info_df, use_container_width=True, height=350)

    with e2:
        st.subheader("Summary Statistics")
        st.dataframe(df.describe().T, use_container_width=True, height=350)

    st.subheader("Duplicate Records")
    st.write(f"Duplicate rows in filtered data: **{df.duplicated().sum()}**")


# --------------------------------------------------------------------------
# AUTOMATIC INSIGHTS SECTION
# --------------------------------------------------------------------------
st.header("🧠 Automated Insights")

insights_list = []
if has("accident_severity") and total_records:
    insights_list.append(
        f"Fatal accidents account for **{100*total_fatal/total_records:.1f}%** of all filtered records, "
        f"while minor accidents make up **{100*total_minor/total_records:.1f}%**."
    )
if has("cause") and len(df):
    insights_list.append(f"**{most_common_cause.title()}** is the leading recorded cause of accidents in the current view.")
if has("state") and total_fatal > 0:
    insights_list.append(f"**{most_dangerous_state}** has the highest count of fatal accidents among filtered states.")
if has("hour") and len(df):
    insights_list.append(f"Accident frequency peaks around **{peak_hour}:00 hrs**, suggesting a high-risk time window.")
if has("road_type") and len(df):
    insights_list.append(f"**{most_common_road.title()}** roads are associated with the highest accident volume.")
if has("month") and len(df):
    insights_list.append(f"**{peak_month}** is the peak month for accidents in the current selection.")

cols_insight = st.columns(2)
for i, text in enumerate(insights_list):
    with cols_insight[i % 2]:
        st.info(f"📌 {text}")


# --------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------
st.divider()
st.caption("**Technologies Used:** Python • Pandas • NumPy • Plotly • Streamlit")
st.caption("GitHub: github.com/your-username/indian-roads-dashboard  |  Version 2.0.0")
st.caption("© 2026 Jasdeep Singh Dhami — Rayat Bahra Group of Institutes & Nano Technology, Hoshiarpur")
