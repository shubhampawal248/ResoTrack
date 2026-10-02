import streamlit as st
from frontend.home import show_home
from frontend.submit_workload import show_submit_workload
from frontend.scheduler_page import show_scheduler
from frontend.process_monitor import show_process_monitor
from frontend.resource_monitor import show_resource_monitor
from frontend.history_page import show_history
from frontend.bottleneck_page import show_bottleneck_analysis
from frontend.database_page import show_database_monitor

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
    show_scheduler()

elif page == "Process Monitor":
    show_process_monitor()

elif page == "Resource Monitor":
    show_resource_monitor()

elif page == "History":
    show_history()

elif page == "Bottleneck Analysis":
    show_bottleneck_analysis()

elif page == "Database Monitor":
    show_database_monitor()