import streamlit as st
from frontend.home import show_home
from frontend.submit_workload import show_submit_workload

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
    show_home()

elif page == "Submit Workload":
    show_submit_workload()

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