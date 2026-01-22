import streamlit as st
import requests
import pandas as pd
from utils.config import header_key

st.set_page_config(page_title="Player Statistics", layout="wide")
st.title("Player Statistics")

headers = { 
    "x-rapidapi-key": header_key, 
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com" 
}

if "multiple_player" not in st.session_state:
    st.session_state.multiple_player = None

def api_call(url):
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        st.error(e)
        return

def get_info(player):

    st.subheader(f"{player['name']} details")
    tab1, tab2, tab3 = st.tabs(["Profile", "Batting Statistics", "Boweling Statistics"])
    with tab1:
        specificplayerurl = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player['id']}"
        data = api_call(specificplayerurl)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Personal Info")
            st.write(f"**Name:** {data.get('name')}")
            st.write(f"**Nickname:** {data.get('nickName')}")
            st.write(f"**Role:** {data.get('role')}")
            st.write(f"**Date of Birth:** {data.get('DoB')}")
            st.write(f"**Birth Place:** {data.get('birthPlace')}")

        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"**Batting Style:** {data.get('bat')}")
            st.write(f"**Bowling Style:** {data.get('bowl')}")
            st.write(f"**Height:** {data.get('height')}")
            st.write(f"**International Team:** {data.get('intlTeam')}")


    with tab2:
        battingstatsurl = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player['id']}/batting"
        data = api_call(battingstatsurl)
        if not data:
            st.warning("No Batting Statistics Available")
            return

        header_list = data.get("headers", [])
        values_list = data.get("values", [])

        if header_list and values_list:
            bat_data = []
            for row in values_list:
                bat_data.append(row["values"])
            
            df = pd.DataFrame(bat_data, columns=header_list)

            higlights = ["Runs", "Average", "SR", "100s", "Highest"]
            hdf = df[df["ROWHEADER"].isin(higlights)]
            hdf = hdf.set_index("ROWHEADER")

            st.markdown("### Highlights")
            cols = st.columns(4)
            hds = header_list[1:]
            for i in range(len(cols)):
                with cols[i]:
                    st.markdown(f"### {hds[i]}")
                    st.write(f"🏏Runs:  **{hdf.loc['Runs', hds[i]]}**")
                    st.write(f"📊Avg:  **{hdf.loc['Average', hds[i]]}**")
                    st.write(f"🚀SR:  **{hdf.loc['SR', hds[i]]}**")

            st.markdown("### Batting Statistics")
            st.dataframe(df)
        else:
            st.warning("No Batting Statistics Available")


    with tab3:
        bowelingstatsurl = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player['id']}/bowling"
        data1 = api_call(bowelingstatsurl)
        if not data1:
            st.warning("No Boweling Statistics Available")
            return

        header_list = data1.get("headers", [])
        values_list = data1.get("values", [])

        if header_list and values_list:
            bowel_data = []
            for row in values_list:
                bowel_data.append(row["values"])
            df = pd.DataFrame(bowel_data, columns=header_list)

            higlights = ["Balls", "Runs", "Eco", "Maidens"]
            hdf = df[df["ROWHEADER"].isin(higlights)]
            hdf = hdf.set_index("ROWHEADER")

            st.markdown("### Highlights")
            cols = st.columns(4)
            hds = header_list[1:]
            for i in range(len(cols)):
                with cols[i]:
                    st.markdown(f"### {hds[i]}")
                    st.write(f"🎯Balls:  **{hdf.loc['Balls', hds[i]]}**")
                    st.write(f"🏏Runs:  **{hdf.loc['Runs', hds[i]]}**")
                    st.write(f"⏱️Economy:  **{hdf.loc['Eco', hds[i]]}**")
            st.markdown("### Boweling Statistics")
            st.dataframe(df)
        else:
            st.warning("No Boweling Statistics Available")

col1, col2 = st.columns([4,1])
name = col1.text_input("Enter player name:", placeholder="Eg: Virat Kholi, MS Dhoni")
if col2.button("Search", type="primary"):
    if not name.replace(' ', '').isalpha():
        st.warning("Please enter a valid player name")
    else:
        try:
            searchurl = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
            querystring = {"plrN":name}
            response = requests.get(searchurl, headers=headers, params=querystring)
            data = response.json()

            if data.get("player"):
                playerList = []
                for player in data.get("player", []):
                    playerList.append({
                        "id": player.get("id"),
                        "name": player.get("name"),
                        "teamName": player.get("teamName"),
                        "faceImageId": player.get("faceImageId"),
                        "dob": player.get("dob")
                    })
                length = len(playerList)
                if length == 1:
                    get_info(playerList[0])
                else:
                    st.session_state.multiple_player = {}
                    for i in playerList:
                        key = f"{i['name']} ({i['teamName']})"
                        st.session_state.multiple_player[key] = i
            else:
                st.warning("No Data Available")
        except Exception as e:
            st.error(e)

if st.session_state.multiple_player:
    st.subheader(f"'{name}' {len(st.session_state.multiple_player)} players found")

    selected_value = st.selectbox(
        "Select a player",
        list(st.session_state.multiple_player.keys())
    )

    get_info(st.session_state.multiple_player[selected_value])