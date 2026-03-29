import streamlit as st
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(
    page_title="ProLabel AI | Data Annotation",
    page_icon="🧠",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .main { padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "file_name" not in st.session_state:
    st.session_state.file_name = ""


def reset_app():
    st.session_state.current_index = 0
    st.session_state.dataset = None


# --- SIDEBAR: SETTINGS & EXPORT ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    uploaded_file = st.file_uploader(
        "Upload CSV", type=["csv"], on_change=reset_app)

    label_input = st.text_input(
        "Define Labels (comma separated)", "Positive, Negative, Neutral, Spam")
    label_options = [opt.strip() for opt in label_input.split(",")]

    st.divider()

    if st.session_state.dataset is not None:
        st.subheader("💾 Export Progress")
        csv_buffer = io.StringIO()
        st.session_state.dataset.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download Labeled CSV",
            data=csv_buffer.getvalue(),
            file_name=f"labeled_{st.session_state.file_name}",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )

# --- MAIN LOGIC ---
st.title("🧠 ProLabel AI")

if uploaded_file:
    # Load data into session state once
    if st.session_state.dataset is None:
        df = pd.read_csv(uploaded_file)
        if "label" not in df.columns:
            df["label"] = None
        st.session_state.dataset = df
        st.session_state.file_name = uploaded_file.name

    df = st.session_state.dataset
    total_rows = len(df)
    idx = st.session_state.current_index

    # 📊 Metrics & Progress
    labeled_count = df["label"].notnull().sum()
    progress = labeled_count / total_rows

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rows", total_rows)
    m2.metric("Labeled", labeled_count)
    m3.metric("Remaining", total_rows - labeled_count)
    st.progress(progress)

    st.divider()

    # 📝 Labeling Interface
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader(f"Row {idx + 1} of {total_rows}")
        # Display current row data cleanly
        current_row = df.iloc[idx].drop("label")
        st.dataframe(current_row, use_container_width=True)

        with st.expander("View Full Context"):
            st.json(current_row.to_dict())

    with col_right:
        st.subheader("Annotate")

        # Display current label if it exists
        existing_label = df.at[idx, "label"]

        # Radio buttons for faster selection than Selectbox
        selected = st.radio(
            "Select the correct category:",
            options=label_options,
            index=label_options.index(
                existing_label) if existing_label in label_options else 0,
            horizontal=True
        )

        st.write("---")

        # Navigation Logic
        nav_prev, nav_next = st.columns(2)

        with nav_prev:
            if st.button("⬅ Previous", use_container_width=True, disabled=(idx == 0)):
                st.session_state.current_index -= 1
                st.rerun()

        with nav_next:
            if st.button("Save & Next ➡", use_container_width=True, type="primary"):
                st.session_state.dataset.at[idx, "label"] = selected
                if idx < total_rows - 1:
                    st.session_state.current_index += 1
                else:
                    st.balloons()
                    st.success("All items labeled!")
                st.rerun()

else:
    st.info("Please upload a CSV file in the sidebar to begin labeling.")
    st.image("https://img.icons8.com/illustrations/external-tulpahn-outline-color-tulpahn/100/external-data-analysis-big-data-tulpahn-outline-color-tulpahn.png", width=150)
