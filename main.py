import streamlit as st

# utilizamos todo el anchura de la página
st.set_page_config(layout="wide")
# --- PAGE SETUP ---
about_page = st.Page(
    page ="views/about.py",
    title = "About Me",
    icon = ":material/account_circle:",
    
)


db_01 = st.Page(
    page ="dashboards_pages/dashboard01.py",
    title = "Unicorn Dashboards",
    icon = ":material/bar_chart:",
    default = True,
)

db_02 = st.Page(
    page ="dashboards_pages/dashboard02.py",
    title = "Pourt Dashboards",
    icon = ":material/bar_chart:",
)

db_03 = st.Page(
    page ="dashboards_pages/dashboard03.py",
    title = "Sales Dashboards",
    icon = ":material/bar_chart:",
)

# --- NAVIGATION ---
#pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

pg = st.navigation(
        {
            "Info": [about_page],
            "Dashboards": [db_01, db_02, db_03],
            
        }    
    )

st.logo("assets/logo4.png")
st.sidebar.title("Navigation")

pg.run()