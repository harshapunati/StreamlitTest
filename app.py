import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="SIR / NFHS Intelligence Dashboard",
    layout="wide"
)

st.title("📊 National Data Intelligence Dashboard")

# ----------------------------------
# LOAD DATA
# ----------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("All India National Family Health Survey4.xlsx")
    return df

df = load_data()

# ----------------------------------
# AUTO COLUMN DETECTION
# ----------------------------------
state_col = None
for col in df.columns:
    if "state" in col.lower():
        state_col = col
        break

numeric_cols = df.select_dtypes(include="number").columns.tolist()

# ----------------------------------
# SIDEBAR CONTROLS
# ----------------------------------
st.sidebar.header("⚙️ Controls")

selected_states = None
if state_col:
    selected_states = st.sidebar.multiselect(
        "Select States",
        sorted(df[state_col].dropna().unique()),
        default=sorted(df[state_col].dropna().unique())[:6]
    )

metric_x = st.sidebar.selectbox("Primary Metric", numeric_cols)
metric_y = st.sidebar.selectbox("Secondary Metric", numeric_cols, index=1)

# FILTER DATA
df_filtered = df.copy()
if selected_states and state_col:
    df_filtered = df[df[state_col].isin(selected_states)]

# ----------------------------------
# KPI SECTION
# ----------------------------------
st.subheader("📌 Key Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Records", len(df_filtered))
c2.metric("States Selected", len(selected_states) if selected_states else 0)
c3.metric("Indicators", len(numeric_cols))
c4.metric("Columns", len(df_filtered.columns))

# ----------------------------------
# TABS
# ----------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Overview",
    "📈 Trends & Insights",
    "🔥 State Rankings",
    "🧠 Correlation Engine",
    "📄 Data Explorer"
])

# ----------------------------------
# TAB 1 — EXECUTIVE OVERVIEW
# ----------------------------------
with tab1:

    st.subheader("Distribution Analysis")

    fig_hist = px.histogram(
        df_filtered,
        x=metric_x,
        title=f"Distribution of {metric_x}"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    if state_col:
        st.subheader("State-wise Comparison")

        grouped = df_filtered.groupby(state_col)[metric_x].mean().reset_index()

        fig_bar = px.bar(
            grouped.sort_values(metric_x),
            x=metric_x,
            y=state_col,
            orientation="h"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------------
# TAB 2 — INSIGHTS
# ----------------------------------
with tab2:

    st.subheader("Relationship Between Indicators")

    fig_scatter = px.scatter(
        df_filtered,
        x=metric_x,
        y=metric_y,
        color=state_col if state_col else None,
        title=f"{metric_x} vs {metric_y}"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # AUTO INSIGHTS ENGINE
    st.subheader("🧠 Auto Insights")

    mean_val = df_filtered[metric_x].mean()
    max_val = df_filtered[metric_x].max()
    min_val = df_filtered[metric_x].min()

    st.info(f"""
    considered insight (auto-generated):

    • Average value of **{metric_x}** = {round(mean_val,2)}
    • Maximum observed value = {round(max_val,2)}
    • Minimum observed value = {round(min_val,2)}

    Use this to explain variation across states during presentation.
    """)

# ----------------------------------
# TAB 3 — STATE RANKINGS
# ----------------------------------
with tab3:

    if state_col:
        st.subheader("🏆 State Ranking Engine")

        ranking_metric = st.selectbox(
            "Select Metric for Ranking",
            numeric_cols
        )

        rank_df = (
            df_filtered.groupby(state_col)[ranking_metric]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        rank_df["Rank"] = range(1, len(rank_df)+1)

        st.dataframe(rank_df)

        fig_rank = px.bar(
            rank_df,
            x=state_col,
            y=ranking_metric,
            title="State Ranking Visualization"
        )
        st.plotly_chart(fig_rank, use_container_width=True)

# ----------------------------------
# TAB 4 — CORRELATION ENGINE
# ----------------------------------
with tab4:

    st.subheader("🔥 Correlation Heatmap")

    corr = df_filtered[numeric_cols].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        aspect="auto"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

# ----------------------------------
# TAB 5 — DATA EXPLORER
# ----------------------------------
with tab5:

    st.subheader("🔎 Smart Data Explorer")

    search = st.text_input("Search dataset")

    if search:
        st.dataframe(
            df_filtered[df_filtered.astype(str).apply(
                lambda x: x.str.contains(search, case=False)
            ).any(axis=1)]
        )
    else:
        st.dataframe(df_filtered)
