import streamlit as st

st.set_page_config(
    page_title="SysNexa",
    page_icon="⚙️",
    layout="wide"
)

st.title("SysNexa")
st.subheader("Operating System and Database Resource Manager")

st.sidebar.title("SysNexa")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Submit Workload",
        "Scheduler",
        "Process Monitor",
        "Resource Monitor",
        "History",
        "Bottleneck Analysis",
        "Database Monitor"
    ]
)

if page == "Home":
    st.header("Home")
    st.write("Welcome to SysNexa.")

elif page == "Submit Workload":
    st.header("Submit Workload")

elif page == "Scheduler":
    st.header("Scheduler")

elif page == "Process Monitor":
    st.header("Process Monitor")

elif page == "Resource Monitor":
    st.header("Resource Monitor")

elif page == "History":
    st.header("History")

elif page == "Bottleneck Analysis":
    st.header("Bottleneck Analysis")

elif page == "Database Monitor":
    st.header("Database Monitor")