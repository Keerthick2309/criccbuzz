from utils.db_connection import get_connection
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import re
from utils.config import header_key

st.set_page_config(page_title="SQL Analytics", layout="wide")
st.title("SQL Analytics")

headers = { 
    "x-rapidapi-key": header_key, 
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com" 
}


def get_db():
    return get_connection()

connection = get_db()
cursor = connection.cursor()

def apicall(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code  == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(e)
        return


# def createtable():
#     query = """
#         create table if not exists indianteam(
#         id int,
#         name varchar(50),
#         role varchar(50),
#         battingstyle varchar(50),
#         bowlingstyle varchar(50)
#         );
#         """
#     cursor.execute(query)
#     connection.commit()

def first():
    query = """
        create table if not exists indianteam(
        id int,
        name varchar(50),
        role varchar(50),
        battingstyle varchar(50),
        bowlingstyle varchar(50)
        );
        """
    cursor.execute(query)
    connection.commit()

    url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/3718/squads/2"
    data = apicall(url)
    list1 = []
    for i in data.get("player"):
        if not i.get("isHeader"):
            id= i.get("id")
            name= i.get("name")
            role= i.get("role")
            battingStyle= i.get("battingStyle")
            bowlingStyle= i.get("bowlingStyle") 
            list1.append((id, name, role, battingStyle, bowlingStyle))
    try:
        cursor.executemany("""
        insert into indianteam (id,name,role,battingstyle,bowlingstyle)
        values(%s, %s, %s, %s, %s)
        """, list1)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
from datetime import datetime

def second():
    query = """
        CREATE TABLE IF NOT EXISTS recentmatches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            matchdesc VARCHAR(100),
            team1 VARCHAR(100),
            team2 VARCHAR(100),
            venue VARCHAR(200),
            matchdate DATE
        );
    """
    cursor.execute(query)
    connection.commit()

    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    data = apicall(url)

    matches = []

    try:
        for type_match in data.get("typeMatches", []):
            for series in type_match.get("seriesMatches", []):

                wrapper = series.get("seriesAdWrapper")
                if not wrapper:
                    continue

                for match in wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    if not info:
                        continue

                    team1 = info.get("team1", {})
                    team2 = info.get("team2", {})
                    venue = info.get("venueInfo", {})

                    datet = datetime.fromtimestamp(int(info["startDate"]) / 1000).date()

                    matches.append((
                        f"{info.get("seriesName")} - {info.get("matchFormat")} - {info.get("matchDesc")}",
                        team1.get("teamName"),
                        team2.get("teamName"),
                        f"{venue.get('ground')} - {venue.get('city')}",
                        datet
                    ))
        if matches:
            cursor.executemany("""
                INSERT IGNORE INTO recentmatches
                (matchdesc, team1, team2, venue, matchdate)
                VALUES (%s, %s, %s, %s, %s)
            """, matches)
            connection.commit()

        return True

    except Exception as e:
        st.error(str(e))
        return False
    
def third():
    try:
        query = """
            create table if not exists highodi(
            id int auto_increment primary key,
            name varchar(50),
            Matches int,
            Runs int,
            Average decimal(4,2),
            No_of_centuries int
            )
            """
        cursor.execute(query)
        connection.commit()

        url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
        querystring = {"statsType":"mostRuns","matchType":"2"}
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        odilist = []
        for val in data.get("values", []):
             vals = val.get("values", [])
             odilist.append((
                    vals[1],
                    int(vals[2]),
                    int(vals[4]),
                    float(vals[5])
                ))
        cursor.executemany("""
            insert into highodi (name, Matches, Runs, Average)
            values (%s, %s, %s, %s)
            """, odilist)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
def four():
    try:
        query = """
            create table if not exists venue(
            id int auto_increment primary key,
            ground varchar(100),
            city varchar(50),
            country varchar(50),
            capacity varchar(50),
            homeTeam varchar(100)
            )
            """
        cursor.execute(query)
        connection.commit()

        venuelist = []
        for i in range(1,51):
            url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{i}"
            data = apicall(url)
            if not data:
                continue
            ground = data.get("ground", "")
            city = data.get("city", "")
            country = data.get("country", "")
            capacity = data.get("capacity", "")
            homeTeam = data.get("homeTeam", "")
            venuelist.append((ground, city, country, capacity, homeTeam))
        cursor.executemany("""
            insert into venue (ground, city, country, capacity, homeTeam)
            values (%s, %s, %s, %s, %s)
            """, venuelist)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
def five():
    try:

        query = """
            create table if not exists mostwin(
            id int auto_increment primary key,
            seriesName varchar(100),
            team1 varchar(100),
            team2 varchar(100),
            Wonby varchar(100)
            )
            """
        cursor.execute(query)
        connection.commit()

        url = f"https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
        data = apicall(url)
        wondetails = []
        for type_match in data.get("typeMatches", []):
            for series in type_match.get("seriesMatches", []):
                series_wrapper = series.get("seriesAdWrapper")
                if not series_wrapper:
                    continue

                for match in series_wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    seriesName = info.get("seriesName")
                    wonteam = info.get("currBatTeamId")
                    team1id = info.get("team1", {}).get("teamId")
                    team2id = info.get("team2", {}).get("teamId")
                    team1 = info.get("team1", {}).get("teamName")
                    team2 = info.get("team2", {}).get("teamName")

                    if not wonteam:
                        continue
                    if wonteam == team1id:
                        wonby = team1
                    elif wonteam == team2id:
                        wonby = team2
                    else:
                        wonby = ""
                    wondetails.append((seriesName, team1, team2,wonby))
        cursor.executemany("""
            insert into mostwin (seriesName, team1, team2, Wonby)
            values (%s, %s, %s, %s)
            """, wondetails)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
                
def seven():
    try:
        query = """
            create table if not exists formathighscore(
            id int auto_increment primary key,
            Format varchar(100),
            name varchar(100),
            TotalRuns int
            )
            """
        cursor.execute(query)
        connection.commit()

        url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
        querystring = {"statsType":"mostRuns","matchType":"1"}
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        formatList = []
        for vals in data.get("values", []):
            val = vals.get("values", [])
            formatList.append((
                "Test",
                val[1],
                int(val[4])
            ))
        cursor.executemany("""
            insert into formathighscore (Format, name, TotalRuns)
            values (%s, %s, %s)
            """, formatList)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False

def Eight():
    try:
        query = """
            create table if not exists serieslist(
            id int auto_increment primary key,
            seriesname varchar(100),
            Country varchar(100),
            MatchType varchar(50),
            total_number_of_matches int,
            startDate date
            )
            """
        cursor.execute(query)
        connection.commit()

        serieslist = []
        li = ["international", "league", "domestic", "women"]
        for i in li:

            url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{i}"
            data = apicall(url)

            for block in data.get("seriesMapProto", []):
                for series in block.get("series", []):
                    start_ts = int(series.get("startDt", 0))
                    start_year = datetime.fromtimestamp(start_ts / 1000).year

                    if start_year == 2024:
                        serieslist.append({
                            "seriesId": series.get("id")
                        })
        serieslist2 = []
        for s in serieslist:
            url1 = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{s['seriesId']}"
            data1 = apicall(url1)
            count = 0
            for m in data1.get("matchDetails", []):
                matchDetailsMap = m.get("matchDetailsMap")
                if not matchDetailsMap:
                    continue
                for match in matchDetailsMap.get("match", []):
                    info = match.get("matchInfo", {})
                    seriesName = info.get("seriesName")
                    country = info.get("venueInfo").get("city")
                    matchTYpe = info.get("matchFormat")
                    match_count = count + 1
                    startdate = datetime.fromtimestamp(int(info.get("startDate")) / 1000).date()
                    serieslist2.append((seriesName, country, matchTYpe, match_count, startdate))
        cursor.executemany("""
            insert into serieslist (seriesname, Country, MatchType, total_number_of_matches, startDate)
            values (%s, %s, %s, %s, %s)
            """, serieslist2)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
def Ten():
    try:
        query = """
            create table if not exists last20matches(
            id int auto_increment primary key,
            match_description varchar(100),
            team1 varchar(100),
            team2 varchar(100),
            winning_team varchar(100),
            victory_margin varchar(100),
            victory_type varchar(100),
            venue varchar(100),
            dates date
            )
            """
        cursor.execute(query)
        connection.commit()

        url = f"https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
        data = apicall(url)
        matches = []
        for type_match in data.get("typeMatches", []):
            for series in type_match.get("seriesMatches", []):
                series_wrapper = series.get("seriesAdWrapper")
                if not series_wrapper:
                    continue

                for match in series_wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    team1 = info.get("team1", {})
                    team2 = info.get("team2", {})
                    match_desc = info.get("matchDesc")
                    venueDetails = info.get("venueInfo", {})

                    venue = f"{venueDetails.get("ground")}, {venueDetails.get("city")}"
                    team1name = team1.get("teamName")
                    team2name = team2.get("teamName")
                    winningTeam = info.get("stateTitle")
                    victoryType = info.get("status")
                    victoryMargin = info.get("status")
                    date = datetime.fromtimestamp(int(info.get("startDate")) / 1000).date()
                    matches.append((match_desc, team1name, team2name, winningTeam, victoryType, victoryMargin, venue, date))
        cursor.executemany("""
            insert into last20matches (match_description, team1, team2, winning_team, victory_margin, victory_type, venue, dates)
            values (%s,%s,%s,%s,%s,%s,%s,%s)
            """, matches)
        connection.commit()
        return True

    except Exception as e:
        st.error(e)
        return False
    
def extract_wickets(data):
    headers = data.get("headers", [])
    values = data.get("values", [])

    wickets_by_format = {}

    for row in values:
        row_values = row.get("values", [])
        if row_values[0] in "Wickets":
            for i in range(1, len(headers)):
                wickets_by_format[headers[i]] = int(row_values[i])

    return wickets_by_format

def extract_runs(data):
    headers = data.get("headers", [])
    values = data.get("values", [])

    runs_by_format = {}

    for row in values:
        row_values = row.get("values", [])
        if row_values[0] == "Runs":
            for i in range(1, len(headers)):
                runs_by_format[headers[i]] = int(row_values[i])

    return runs_by_format


def Nine():
    try:
        query = """
            create table if not exists allrounders(
            id int auto_increment primary key,
            Name varchar(100),
            TotalRuns varchar(100),
            TotalWickets varchar(100),
            CricketFormat varchar(100)
            )
            """
        cursor.execute(query)
        connection.commit()

        all_rounders = []
        for i in range(2, 3):
            url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{i}/players"
            data = apicall(url)
            if not data:
                continue
            current_role = None

            for item in data.get("player", []):
                if "id" not in item:
                    current_role = item.get("name").strip()
                    continue

                if current_role == "ALL ROUNDER":
                    all_rounders.append((item.get("id"), item.get("name")))
        insertplayers = []
        for j, name in all_rounders:
            url1 = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{j}/batting"
            url2 = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{j}/bowling"
            data1 = apicall(url1)
            data2 = apicall(url2)

            runs = extract_runs(data1)
            wickets = extract_wickets(data2)
            for format in runs:
                insertplayers.append((
                        name,
                        runs[format],
                        wickets.get(format, 0),
                        format
                    ))
        cursor.executemany("""
            insert into allrounders (Name, TotalRuns, TotalWickets, CricketFormat)
            values (%s,%s,%s,%s)
            """, insertplayers)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
def Eleven():
    try:
        query = """
            create table if not exists batting_stats(
            id int auto_increment primary key,
            PlayerName varchar(100),
            Format varchar(100),
            Runs int,
            Average decimal(5,2)
            )
            """
        cursor.execute(query)
        connection.commit()

        lists = []
        for i in range(2, 3):
            url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{i}/players"
            data = apicall(url)
            if not data:
                continue
            allplayer = []
            for item in data.get("player", []):
                if "id" in item:
                    allplayer.append((item.get("id"), item.get("name")))
            
            for id, name in allplayer:
                url1 = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{id}/batting"
                data1 = apicall(url1)

                if not data1:
                    continue

                headers = data1.get("headers", [])
                values = data1.get("values", [])

                runs = {}
                avgs = {}

                for row in values:
                    row_values = row.get("values", [])
                    if not row_values:
                        continue

                    if row_values[0] == "Runs":
                        for i in range(1, len(headers)):
                            runs[headers[i]] = int(row_values[i])

                    if row_values[0] == "Average":
                        for i in range(1, len(headers)):
                            avgs[headers[i]] = float(row_values[i])

                for format in runs:
                    lists.append((
                        name,
                        format,
                        runs[format],
                        avgs[format]
                    ))
        cursor.executemany("""
            insert into batting_stats (PlayerName, Format, Runs, Average)
            values (%s,%s,%s,%s)
            """, lists)
        connection.commit()
        return True
    except Exception as e:
        st.error(e)
        return False

def Twelve():
    try:
        query = """
            create table if not exists matchResults(
            id int auto_increment primary key,
            Team1 varchar(100),
            Team2 varchar(100),
            venueCountry varchar(100),
            winnerTeam VARCHAR(50)
            )
            """
        cursor.execute(query)
        connection.commit()

        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
        data = apicall(url)
        if data:
            mactchlist = []
            for type in data.get("typeMatches", []):
                if type.get("matchType") != "International":
                    continue
                for series in type.get("seriesMatches", []):
                    series_wrapper = series.get("seriesAdWrapper")
                    if not series_wrapper:
                        continue
                    for match in series_wrapper.get("matches", []):
                        info = match.get("matchInfo")
                        venueInfo = info.get("venueInfo", {})
                        state = info.get("state")
                        if state == "Complete":

                            mactchlist.append({
                                "team1": info.get("team1", {}).get("teamName"),
                                "team2": info.get("team2", {}).get("teamName"),
                                "winteamid": info.get("currBatTeamId"),
                                "venueid": venueInfo.get("id")
                            })
            newlist = []
            url2 = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/international"
            data2 = apicall(url2)
            for m in mactchlist:
                venueid = m.get("venueid")
                url1 = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{venueid}"
                data1 = apicall(url1)
                if not data1:
                    continue

                venueCountry = data1.get("country")
                winteam = m.get("winteamid")
                if not data2:
                    continue
                for i in  data2.get("list", []):
                    if i.get("teamId") == winteam:
                        winCountry = i.get("teamName")
                newlist.append((
                    m.get("team1"),
                    m.get("team2"),
                    venueCountry,
                    winCountry
                ))
            cursor.executemany("""
                INSERT INTO matchResults (Team1, Team2, VenueCountry, WinnerTeam)
                VALUES (%s, %s, %s, %s)
                """, newlist)
            connection.commit()
            return True
    except Exception as e:
        st.error(e)
        return False
    
def Thirteen():
    query = """
        create table if not exists partnerships (
            id int auto_increment primary key,
            Player1 varchar(100),
            Player2 varchar(100),
            PartnershipRuns int,
            Innings int
        );
        """
    cursor.execute(query)
    connection.commit()
    url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/121367/hscard"
    data = apicall(url)

    partnership = []
    for score in data.get("scorecard", []):
        innings = score.get("inningsid")
        p = score.get("partnership", {})
        if not p:
            continue
        for partner in p.get("partnership", []):
            player1 = partner.get("bat1name")
            player2 = partner.get("bat2name")
            totalruns = partner.get("totalruns")
            partnership.append((player1,player2, totalruns, innings))
    cursor.executemany("""
        insert into partnerships(Player1, Player2, PartnershipRuns, Innings)
        values (%s, %s, %s, %s)
        """, partnership)
    connection.commit()
    return True


def fifteen():
    try:
        query = """
             create table if not exists close_match_batting (
                MatchId INT,
                PlayerId INT,
                PlayerName VARCHAR(100),
                TeamName VARCHAR(100),
                Runs INT,
                TeamWon BOOLEAN
            );
        """
        cursor.execute(query)
        connection.commit()

        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
        data = apicall(url)

        close_matches = []

        for t in data.get("typeMatches", []):
            for s in t.get("seriesMatches", []):
                wrapper = s.get("seriesAdWrapper")
                if not wrapper:
                    continue

                for match in wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    status = info.get("status", "")
                    state = info.get("state")
                    matchId = info.get("matchId")

                    if state != "Complete":
                        continue

                    runs = wickets = None

                    run_match = re.search(r'(\d+)\s*runs', status)
                    wkt_match = re.search(r'(\d+)\s*wkts', status)

                    if run_match:
                        runs = int(run_match.group(1))
                    if wkt_match:
                        wickets = int(wkt_match.group(1))

                    if (runs is not None and runs < 50) or (wickets is not None and wickets < 5):
                        win_team = status.split(" won")[0].strip()
                        close_matches.append({
                            "matchId": matchId,
                            "winteam": win_team
                        })

        for match in close_matches:
            matchId = match["matchId"]
            winteam = match["winteam"]

            url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{matchId}/hscard"
            data = apicall(url)

            for innings in data.get("scorecard", []):
                team = innings.get("batteamname")

                for batsman in innings.get("batsman", []):
                    playerId = batsman.get("id")
                    playerName = batsman.get("name")
                    runs = batsman.get("runs", 0)

                    team_won = team == winteam

                    cursor.execute("""
                        INSERT INTO close_match_batting
                        (MatchId, PlayerId, PlayerName, TeamName, Runs, TeamWon)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (matchId, playerId, playerName, team, runs, team_won))

        connection.commit()
        return True

    except Exception as e:
        st.error(e)
        return False




names = [
    "1. List all players who represent India", 
    "2. Show all cricket matches that were played in the last Few days", 
    "3. List the top 10 highest run scorers in ODI cricket",
    "4. Display all cricket venues that have a seating capacity of more than 25,000 spectators",
    "5. how many matches each team has won",
    "6. Count how many players belong to each playing role",
    "7. Display the format and the highest score for that format",
    "8. Show all cricket series that started in the year 2024",
    "9. Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career",
    "10. Get details of the last 20 completed matches",
    "11. Compare each player's performance across different cricket formats",
    "12. Analyze each international team's performance when playing at home versus playing away",
    "13. Identify batting partnerships where two consecutive batsmen",
    "14.",
    "15. Identify players who perform exceptionally well in close matches",
    "16.",
    "17.",
    "18.",
    "19.",
    "20.",
    "21.",
    "22.",
    "23.",
    "24.",
    "25.",
    ]

selected_name = st.selectbox("Choose from list:", names)
select_index = names.index(selected_name)
st.subheader(f"Selected: {selected_name}")

match select_index:
    case 0:
        query = "select name as full_name, role, battingStyle, bowlingStyle from indianteam"
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["full_name", "role", "battingStyle", "bowlingStyle"])
        st.dataframe(df)
    case 1:
        # if second():
            query = "select matchDesc, Team1, Team2, venue, matchdate from recentmatches order by matchdate desc"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["matchDesc", "Team1", "Team2", "venue", "matchdate"])
            st.dataframe(df)
    case 2:
        #if third():
            query = "select name, runs, average, no_of_centuries from highodi order by runs desc limit 10"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["Name","Runs", "Avg", "Centuries"])
            st.dataframe(df)
    case 3:
        # if four():
            query = "select ground, city, country, capacity, hometeam from venue where capacity > 25000"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["Ground", "City", "Country", "Capacity", "Hometeam"])
            st.dataframe(df)
    case 4:
        #if five():
            query = "select wonby, count(wonby) as totalwins from mostwin group by wonby order by totalwins desc"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["wonby", "totalwins"])
            st.dataframe(df)
    case 5:
        query = "select role, count(*) as no_of_players from indianteam group by role"
        cursor.execute(query)
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=["Role", "No_of_players"])
        st.dataframe(df)
    case 6:
        #if seven():
            query = "select format, max(TotalRuns) from formathighscore group by Format"
            cursor.execute(query)
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=["Format", "TotalRuns"])
            st.dataframe(df)
    case 7:
        #if Eight():
            query = "select seriesname, country, matchType, sum(total_number_of_matches), startdate from serieslist group by seriesname, country, matchtype, startdate;"
            cursor.execute(query)
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=["seriesname", "country", "matchType", "No_of_matches", "StartDate"])
            st.dataframe(df)
    case 8:
        # if Nine():
            query = "select name, totalruns, totalwickets, cricketformat from allrounders where totalruns > 1000 and totalwickets > 50"
            cursor.execute(query)
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=["Name", "TotalRuns", "TotalWickets", "CricketFormat"])
            st.dataframe(df)
    case 9:
        #if Ten():
            query = "select match_description, team1, team2, winning_team, victory_margin, victory_type, venue from last20matches order by dates desc limit 20"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["match_description","Team1", "Team2", "Winning Team", "Vicatory Margin", "Victory Type", "venue"])
            st.dataframe(df)
    case 10:
        #if Eleven():
            query = """
                select
                    PlayerName,
                    SUM(CASE WHEN Format = 'Test' THEN Runs ELSE 0 END) AS TestRuns,
                    SUM(CASE WHEN Format = 'ODI'  THEN Runs ELSE 0 END) AS ODIRuns,
                    SUM(CASE WHEN Format = 'T20'  THEN Runs ELSE 0 END) AS T20Runs,
                    SUM(CASE WHEN Format = 'IPL'  THEN Runs ELSE 0 END) AS IPLRuns,

                    ROUND(AVG(Average), 2) AS OverallBattingAverage

                from batting_stats
                where runs > 0
                GROUP BY PlayerName
                HAVING COUNT(DISTINCT Format) >= 2;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["PlayerName","Test", "ODI", "T20", "IPL", "Average"])
            st.dataframe(df)
    case 11:
        #if Twelve():
            query = """
                select winnerTeam as Team,
                    SUM(CASE WHEN WinnerTeam = VenueCountry THEN 1 ELSE 0 END) AS HomeWins,
                    SUM(CASE WHEN WinnerTeam != VenueCountry THEN 1 ELSE 0 END) AS AwayWins
                from  matchResults where winnerteam != 'Associate Teams' group by winnerteam
                """
            cursor.execute(query)
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=["Team", "HomeWins", "AwayWins"])
            st.dataframe(df)
    case 12:
    #    if Thirteen(): 121367 108811
            query = "select Player1, player2,partnershipruns,  innings from partnerships where partnershipruns >= 100"
            cursor.execute(query)
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=["Player1", "player2", "partnershipruns", "innings"])
            st.dataframe(df)
    case 14:
        #if fifteen():
            query = """SELECT
                    PlayerName,
                    COUNT(*) AS close_matches,
                    ROUND(AVG(Runs), 2) AS avg_runs,
                    SUM(CASE WHEN TeamWon = TRUE then 1 else 0 END) AS wins_when_batted
                FROM close_match_batting
                group by PlayerName
                ORDER BY close_matches DESC;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["PlayerName", "close_matches", "avg_runs", "wins_when_batted"])
            st.dataframe(df)
