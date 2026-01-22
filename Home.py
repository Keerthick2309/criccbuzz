import streamlit as st

st.set_page_config(page_title="Home", layout="wide")
st.title("Cricbuzz")

st.write("""
**Live Match Details**  
View real-time cricket match information including scores, teams, match status, and key moments, updated directly from live cricket APIs.
""")

st.write("""
**Player Statistics**  
Analyze detailed batting and bowling statistics of players across formats, including runs, averages, strike rates, and performance highlights.
""")

st.write("""
**SQL Queries & Analysis**  
Cricket data is stored in a SQL database, allowing complex queries and analysis such as filtering matches, player performance trends, and team statistics.
""")

st.write("""
**CRUD Operations**  
The application supports Create, Read, Update, and Delete operations to manage player efficiently using a database-backed system.
""")
