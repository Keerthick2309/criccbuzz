import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from utils.config import header_key

st.set_page_config(page_title="Cricbuzz Live", layout="wide")
st.title("Cricbuzz Match Details")
st.divider()

headers = { 
    "x-rapidapi-key": header_key, 
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com" 
}

url_map = {
    "Live": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live",
    "Upcoming": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming",
    "Recent": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent",
}

match_type = st.selectbox(
    "Select Match Type",
    ["Live", "Upcoming", "Recent"]
)

def apicall(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code  == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(e)
        return


def fetch_matches(category):
    try:
        data = apicall(url_map[category])
        if not data:
            return
        matches = []

        for type_match in data.get("typeMatches", []):
            for series in type_match.get("seriesMatches", []):
                series_wrapper = series.get("seriesAdWrapper")
                if not series_wrapper:
                    continue

                series_name = series_wrapper.get("seriesName")

                for match in series_wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    team1 = info.get("team1", {})
                    team2 = info.get("team2", {})

                    score = match.get("matchScore", {})
                    t1 = score.get("team1Score", {}).get("inngs1", {})
                    t2 = score.get("team2Score", {}).get("inngs1", {})

                    matchid = info.get("matchId")

                    matches.append({
                        "category": category,
                        "matchid": matchid,
                        "series": series_name,
                        "team1": team1.get("teamName"),
                        "team2": team2.get("teamName"),
                        "team1_score": f"{t1.get('runs', '-')}/{t1.get('wickets', '-')}",
                        "team2_score": f"{t2.get('runs', '-')}/{t2.get('wickets', '-')}",
                        "overs1": t1.get("overs", ""),
                        "overs2": t2.get("overs", ""),
                        "status": info.get("status"),
                        "venue": info.get("venueInfo", {}).get("ground"),
                        "city": info.get("venueInfo", {}).get("city"),
                        "startdate": info.get("startDate"),
                        "endate": info.get("endDate"),
                        "matchFormat": info.get("matchFormat")
                    })
        return matches
    except Exception as e:
        st.error(e)
        return

matches = fetch_matches(match_type)

if not matches:
    st.warning("No matches available")
else:
    match_labels = []
    match_map = {}

    for m in matches:
        label = f"{m['team1']} vs {m['team2']} - ({m["series"]})"
        match_labels.append(label)
        match_map[label] = m

    selected_match = st.selectbox(
        "Select Match",
        match_labels
    )

    da = match_map[selected_match]
    
    datet = datetime.fromtimestamp(int(da['startdate']) / 1000).strftime("%d %b %Y")
    column1, column2, column3 = st.columns(3)
    column1.caption(f"Match Date: {datet}")
    column2.caption(f"Series: {da["series"]}")
    column3.caption(f"Venue: {da['venue']}, {da['city']}")
    st.caption(f"Format: {da["matchFormat"]}")

    col1, col2 = st.columns(2)

    col1.write(f"**{da['team1']}**")
    col1.write(f"**{da['team2']}**")
    
    col2.write(f"{da['team1_score']} ({da['overs1']} ov)")
    col2.write(f"{da['team2_score']} ({da['overs2']} ov)")

    if match_type == "Live" or match_type == "Upcoming":
        st.info(da["status"])
    else:
        st.success(da["status"])

    if st.button("Scorecard"):
        try:
            scorecardurl = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{da["matchid"]}/scard"
            data = apicall(scorecardurl)

            if not data.get("scorecard", []):
                st.warning('No Scorecard Available')
            else:
                for innings  in data.get("scorecard", []):
                    inn = innings["inningsid"]
                    team_name = innings["batteamname"]
                    score = innings["score"]
                    wickets = innings["wickets"]
                    overs = innings["overs"]
                    runrate = innings["runrate"]
                    st.subheader(f"{team_name} Innings {inn}")
                    cols1, cols2, cols3 = st.columns(3)
                    cols1.caption(f"Score: {score}/{wickets}")
                    cols2.caption(f"Overs: {overs}")
                    cols3.caption(f"Run Rate: {runrate}")

                    extras =  innings.get("extras", {})
                    legbyes = extras.get("legbyes")
                    byes = extras.get("byes")
                    wides = extras.get("wides")
                    noballs = extras.get("noballs")
                    penalty = extras.get("penalty")
                    total = extras.get("total")
                    st.caption(f"Extras: {total} (b: {byes}, lb: {legbyes}, w: {wides}, nb: {noballs}, p: {penalty})")
                    
                    batting = []
                    for batsman in innings.get("batsman",[]):
                        batting.append({
                            "Batsman": batsman["name"],
                            "Runs": batsman["runs"],
                            "Balls": batsman["balls"],
                            "4s": batsman["fours"],
                            "6s": batsman["sixes"],
                            "SR": batsman["strkrate"],
                            "Status": batsman["outdec"]
                        })
                    st.markdown("#### Batter")
                    st.table(pd.DataFrame(batting))

                    bowling = []
                    for bowler in innings.get("bowler"):
                        bowling.append({
                            "Bowler": bowler["name"],
                            "Overs": bowler["overs"],
                            "Runs": bowler["runs"],
                            "Wickets": bowler["wickets"],
                            "Economy": bowler["economy"],
                            "maidens": bowler["maidens"],
                        })
                    st.markdown("##### Bowler")
                    st.table(pd.DataFrame(bowling))

                    fallofwickets = []
                    fows = innings.get("fow", {})
                    if not fows:
                        continue
                    for fow in fows.get("fow", []):
                        fallofwickets.append({
                            "name": fow["batsmanname"],
                            "score": fow["runs"],
                            "over": fow["overnbr"]
                        })
                    st.markdown("#### Fall of Wickets")
                    st.table(pd.DataFrame(fallofwickets))
        except Exception as e:
            st.error(e)