import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="SIR / NFHS Data Dashboard",
    layout="wide"
)

st.title("📊 SIR / NFHS Data Analytics Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    file_path = "All India National Family Health Survey4.xlsx"
    df = pd.read_excel(file_path)
    return df

df = load_data()

st.write("### Raw Dataset Preview")
st.dataframe(df.head())

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Filters")

# Try auto-detecting State column
state_col = None
for col in df.columns:
    if "state" in col.lower():
        state_col = col
        break

if state_col:
    states = df[state_col].dropna().unique()
    selected_states = st.sidebar.multiselect(
        "Select State",
        states,
        default=states
    )
    df_filtered = df[df[state_col].isin(selected_states)]
else:
    df_filtered = df

# -----------------------------
# COLUMN SELECTION
# -----------------------------
numeric_cols = df_filtered.select_dtypes(include="number").columns

metric = st.sidebar.selectbox(
    "Select Metric for Visualization",
    numeric_cols
)

# -----------------------------
# MAIN LAYOUT
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.write("### Filtered Data")
    st.dataframe(df_filtered)

with col2:
    st.write("### Chart View")

    if metric:
        fig = plt.figure()
        df_filtered[metric].plot(kind="hist")
        st.pyplot(fig)

# -----------------------------
# STATISTICS SECTION
# -----------------------------
st.write("### 📈 Basic Statistics")
st.write(df_filtered.describe())
