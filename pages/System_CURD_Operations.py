import streamlit as st
import pandas as pd
from utils.db_connection import get_connection

st.set_page_config(
    page_title="Player CRUD",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Create • Read • Update • Delete Player Records")

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
create table if not exists players(
    Id int auto_increment primary key,
    Name varchar(50),
    TeamName varchar(50),
    Country varchar(50),
    DOB date
)
""")
connection.commit()

operation = st.radio(
    "Select action",
    ["Create Player", "Read Player", "Update Player", "Delete Player"],
    horizontal=True
)

def create_player():
    st.subheader("➕ Add New Player")

    with st.form("create_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("👤 Player Name", placeholder="MS Dhoni")
            team = st.text_input("🏏 Team", placeholder="India")

        with col2:
            country = st.text_input("🌍 Country", placeholder="India")
            dob = st.date_input("🎂 Date of Birth")

        submit = st.form_submit_button("Create Player", type="primary")

    if submit:
        if not name.replace(" ", "").isalpha():
            st.warning("Enter a valid player name")
            return

        cursor.execute("SELECT * FROM players WHERE name=%s", (name,))
        if cursor.fetchone():
            st.warning("Player already exists")
        else:
            cursor.execute(
                "INSERT INTO players (Name, TeamName, Country, DOB) VALUES (%s,%s,%s,%s)",
                (name, team, country, dob)
            )
            connection.commit()
            st.success("Player added successfully")

def read_players():
    st.subheader("🔍 View Players")

    col1, col2, col3 = st.columns([8,1,1])
    name = col1.text_input("Search Player", placeholder="Virat Kohli")

    if col2.button("🔍 Search"):
        if not name.replace(" ", "").isalpha():
            st.warning("Invalid name")
        else:
            cursor.execute(
                "SELECT * FROM players WHERE name LIKE %s",
                (f"%{name}%",)
            )
            df = pd.DataFrame(
                cursor.fetchall(),
                columns=["Id","Name","TeamName","Country","DOB"]
            ).set_index("Id")
            st.dataframe(df, use_container_width=True)

    if col3.button("📂 Load All"):
        cursor.execute("SELECT * FROM players")
        df = pd.DataFrame(
            cursor.fetchall(),
            columns=["Id","Name","TeamName","Country","DOB"]
        ).set_index("Id")
        st.dataframe(df, use_container_width=True)

def update_player():
    st.subheader("✏️ Update Player")
    if "update_player" not in st.session_state:
        st.session_state.update_player = False
    
    name = st.text_input("Enter player name", placeholder="Virat Kohli")
    if st.button("Get Details", type="primary"):
        cursor.execute("SELECT * FROM players WHERE name=%s", (name,))
        row = cursor.fetchone()

        if not row:
            st.warning("Player not found")
            st.session_state.update_player = False
            return
        
        st.session_state.update_player = True
        st.session_state.row = row
    if st.session_state.update_player:
        row = st.session_state.row

        with st.form("update_form"):
            col1, col2 = st.columns(2)

            with col1:
                newname = st.text_input("Name", row[1])
                newcountry = st.text_input("Country", row[3])

            with col2:
                newteam = st.text_input("Team", row[2])
                dob = st.date_input("DOB", row[4])

            update = st.form_submit_button("Update Player")

        if update:
            cursor.execute(
                "UPDATE players SET name=%s, teamname=%s, country=%s, dob=%s WHERE id=%s",
                (newname, newteam, newcountry, dob, row[0])
            )
            connection.commit()
            st.success("Player updated successfully")
            st.session_state.update_player = False

def delete_player():
    st.subheader("🗑️ Delete Player")
    if "delete_player" not in st.session_state:
        st.session_state.delete_player = False

    name = st.text_input("Enter player name", placeholder="Virat kolhi")
    if st.button("Get Player", type="primary"):
        cursor.execute("SELECT * FROM players WHERE name=%s", (name,))
        row = cursor.fetchone()

        if not row:
            st.warning("Player not found")
            st.session_state.delete_player = False
            return

        df = pd.DataFrame(
            [row],
            columns=["Id","Name","TeamName","Country","DOB"]
        ).set_index("Id")

        st.session_state.delete_player = True
        st.session_state.player_id = row[0]
        st.session_state.player_df = df

    if st.session_state.delete_player:
        st.warning("Note: This action cannot be undone")
        st.dataframe(st.session_state.player_df, use_container_width=True)
        
        if st.button("Confirm Delete"):
            cursor.execute("DELETE FROM players WHERE id=%s", (st.session_state.player_id,))
            connection.commit()
            st.success("Player deleted successfully")
            st.session_state.delete_player = False

if operation == "Create Player":
    create_player()
elif operation == "Read Player":
    read_players()
elif operation == "Update Player":
    update_player()
else:
    delete_player()
