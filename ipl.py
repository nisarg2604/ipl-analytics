import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Indian Premier League", page_icon = "ipl_logo.png",
                   layout="wide")

PAGE_OPTIONS = ["Overview","Team Analysis","Venue","Data Assistant","Developer's Choice"]
if "page" not in st.query_params:
    st.query_params["page"] = "Overview"
current_page = st.query_params["page"]
default_index = PAGE_OPTIONS.index(current_page)

@st.cache_data
def load_data():
    df = pd.read_csv("matches.csv")
    df = df.replace('Royal Challengers Bangalore', 'Royal Challengers Bengaluru')
    df = df.replace('Delhi Daredevils','Delhi Capitals')
    df = df.replace('Kings XI Punjab','Punjab Kings')
    return df
df = load_data()

with st.sidebar:

    st.title("Indian Premier League")
    selected = option_menu("",["Overview","Team Analysis","Venue","Data Assistant","Developer's Choice"],
                            icons = ["clipboard-data","people-fill","geo-alt-fill","robot","person-fill"],
                            default_index = default_index)
    st.query_params["page"] = selected

if selected == "Overview":
    st.header("IPL Data Analysis")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Teams",df["team1"].nunique())
    col2.metric("Total Stadiums",df["venue"].nunique())
    col3.metric("Highest Match Win",df["winner"].value_counts().idxmax())
    col4.metric("Top POTM",df["player_of_match"].value_counts().idxmax())
    st.divider()

    # Total wins per team
    st.header("Wins Analysis Per Team")
    wins = df["winner"].value_counts()
    fig = px.bar(wins,y=wins.index,x=wins.values,color=wins.index,title="Top Wins",orientation="h")
    fig.update_layout(height=500)
    st.plotly_chart(fig)

    # Team Performance
    st.header("Team Performance")
    select = st.selectbox("Select Team",df["team1"].unique(),index = None)
    win = df[df["winner"] == select].groupby(["season"]).agg(
        Winner=("winner", "count"),
    ).reset_index()
    played = df[(df["team1"] == select) | (df["team2"] == select)].groupby(["season"]).agg(
        play_count=("season", "count"),
    ).reset_index()
    merged = pd.merge(played,win,on="season")
    fig = px.bar(merged,x="season",y=["play_count","Winner"],barmode="group")
    fig.update_layout(height=500,
                      xaxis = dict(tickmode="linear", dtick=1))
    st.plotly_chart(fig,use_container_width=True)
    st.divider()

    #  teams who reach Maximum times into final
    st.header("No. of Teams into the final")
    # find the teams who played final
    final = df[df["match_type"] == "Final"]
    # st.dataframe(final)
    # from team 1 find count per team
    team1 = final.groupby("team1").agg(
        f_played = ("match_type", "count"),
    ).reset_index().rename(columns={"team1":"team"})
    # st.dataframe(team1)
    # from team 2 find count per team
    team2 = final.groupby("team2").agg(
        f_played = ("match_type", "count"),
    ).reset_index().rename(columns={"team2":"team"})
    # st.dataframe(team2)
    # merge both dataframe
    merged = pd.merge(team1,team2,on="team",how="outer")
    merged = merged.fillna(0)
    merged["total_finals"] = merged["f_played_x"] + merged["f_played_y"]
    # st.dataframe(merged)
    fig = px.bar(merged,x="team",y="total_finals",color="team",title = "Teams Reached To final")
    fig.update_layout(height=500)
    st.plotly_chart(fig)
    st.divider()

    # Toss Decision
    st.subheader("Toss Decision Distribution")
    toss_decision = df["toss_decision"].value_counts()
    fig = px.pie(
        values=toss_decision.values,
        names=toss_decision.index,
        title="Toss Decision (Bat vs Field)",
        color = toss_decision.values,
        hole = 0.3
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

if selected == "Team Analysis":
    st.header("Team Performance")
    st.divider()

    # top 5 IPL winners
    st.header("Top Winners")
    final_wins = df[df["match_type"] == "Final"].groupby("winner").agg(
        Wins=("winner", "count")
    ).reset_index().sort_values("Wins", ascending=False)
    # st.dataframe(final_wins)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(final_wins.iloc[0]["winner"], f"🏆{final_wins.iloc[0]["Wins"]}")
    col2.metric(final_wins.iloc[1]["winner"], f"🏆{final_wins.iloc[1]["Wins"]}")
    col3.metric(final_wins.iloc[2]["winner"], f"🏆{final_wins.iloc[2]["Wins"]}")
    col4.metric(final_wins.iloc[3]["winner"], f"🏆{final_wins.iloc[3]["Wins"]}")
    col5.metric(final_wins.iloc[4]["winner"], f"🏆{final_wins.iloc[4]["Wins"]}")
    st.divider()

    # top wins teams metric
    st.header("Top 5 teams over the years")
    wins = df["winner"].value_counts()
    # st.dataframe(wins)
    col1 , col2, col3, col4, col5 = st.columns(5)
    col1.metric(wins.index[0],f"{wins.iloc[0]} wins")
    col2.metric(wins.index[1], f"{wins.iloc[1]}wins")
    col3.metric(wins.index[2], f"{wins.iloc[2]} wins")
    col4.metric(wins.index[3], f"{wins.iloc[3]} wins")
    col5.metric(wins.index[4], f"{wins.iloc[4]} wins")
    st.divider()

    # Year wise Team Performance
    st.header("Year wise Team Performance")
    team = df.groupby(["season", "winner"]).agg(
        Total_wins_per_year =("winner", "count"),
    ).reset_index()
    st.dataframe(team.style.background_gradient(cmap="Blues",subset=["Total_wins_per_year"]))
    st.divider()

    # wins based on choosing Bat vs Field
    st.header("Wins Based On Toss Decision")
    selected = st.selectbox("Select Team", df["team1"].unique(), index=None, key="select_team")
    batting_wins = df[(df["toss_winner"] == selected) & (df["toss_decision"] == "bat") & (df["winner"] == selected)]
    fielding_wins = df[(df["toss_winner"] == selected) & (df["toss_decision"] == "field") & (df["winner"] == selected)]
    # st.dataframe(batting_wins)
    # st.write(len(batting_wins))
    # st.dataframe(fielding_wins)
    # st.write(len(fielding_wins))
    toss_data = pd.DataFrame({
        "Decision": ["Bat", "Field"],
        "Wins": [len(batting_wins), len(fielding_wins)]
    })
    fig = px.pie(toss_data, values="Wins", names="Decision", title="Wins Based On Toss Decision", hole=0.4)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

if selected == "Venue":
    st.header("Venue Analysis")
    st.divider()

    st.header("Top Venues")
    top = df.groupby("venue").agg(
        Venues=("venue", "count"),
    ).reset_index().sort_values("Venues", ascending=False).head(10)
    # st.dataframe(top.sort_values("Venues", ascending=False))
    fig = px.bar(top,y= "venue", x="Venues", color = "Venues", orientation= "h", labels={"venue": "Stadium", "Venues": "Matches Hosted"} )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # Toss decision on Different stadium
    st.header("Toss Decision On **Battle Field**")
    selected = st.selectbox("Select Stadium",df["venue"].unique(), index=None, key="select_venue")
    venue = df[(df["venue"] == selected)]
    toss_count = venue["toss_decision"].value_counts()
    # st.dataframe(toss_count)
    fig = px.pie(toss_count, names=toss_count.index,
                 values= toss_count.values,
                 color_discrete_sequence=px.colors.qualitative.Bold,
                 hole = 0.4)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # Win VS Lost Ration by Toss Decision
    st.header("Win VS Lost Ration by Toss Decision")
    selected = st.selectbox("Select Stadium", df["venue"].unique(), index=None, key="venue")
    venue = df[(df["venue"] == selected)]
    # st.dataframe(venue)
    bat = venue[(venue["toss_decision"] == "bat")&(venue["toss_winner"]==venue["winner"])]
    field= venue[(venue["toss_decision"] == "field")&(venue["toss_winner"]==venue["winner"])]
    decision = pd.DataFrame({
        "Decision": ["bat", "field"],
        "Wins": [len(bat), len(field)]
    })
    st.dataframe(decision)
    fig = px.pie(decision,
                 values = "Wins",
                 names="Decision",
                 color = "Decision",
                 hole = 0.4)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.divider()


if selected == "Data Assistant":
    st.header("Data Assistants")
    st.divider()

    st.write("Ask Questions about the dataset")
    question = st.text_input("Ask Question")

    if question:
        q = question.lower().strip()

        if "highest runs" in q or "highest target" in q :
            st.write(f"Highest Target in IPL is: {df['target_runs'].max()} runs")

        elif "highest winning team" in q or "highest times win" in q or "highest wins" in q:
            st.write(df["winner"].value_counts().idxmax())

        elif "highest toss winner" in q or "highest times toss" in q or "highest toss" in q:
            st.write(df["toss_winner"].value_counts().idxmax())

        elif "highest cup winners" in q or "highest time winners" in q or "highest cup wins" in q:
            highest = (df[df["match_type"] == "Final"].groupby("winner").agg(
                        Wins=("winner", "count")
                        ).reset_index().sort_values("Wins", ascending=False))
            st.write(highest)

        elif "venue" in q or "stadium" in q:
            if "venue" in df.columns:
                venue = df["venue"].value_counts().reset_index()
                venue.columns = ["Venue", "Matches"]

                st.success(f"Top Venue: {venue.iloc[0, 0]}")
                fig = px.bar(venue.head(10), x="Venue", y="Matches",
                             title="Top Venues")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(venue)

        elif "player" in q or "man of the match" in q or "player of the match" in q:
            potm = df["player_of_match"].value_counts().idxmax()
            st.success(f"Top Player: {potm}")


        else:
            st.warning("Sorry, I don't understand that question.")
            st.info("Try asking about Highest Runs, Highest Wins, Highest Toss Winner, Highest cup winner, venue or stadium")

# if selected == "Developer's Choice":
#
#     st.header("😎 Developer Choice 😎")
#     st.divider()
#
#     col1, col2, col3 = st.columns([1,2,1])
#     with col2:
#         st.title("Royal Challengers Bengaluru")
#     st.divider()
#
#     rcb = df[(df["team1"] == "Royal Challengers Bengaluru") | (df["team2"] == "Royal Challengers Bengaluru")]
#     rcb_wins = df[df["winner"] == "Royal Challengers Bengaluru"]
#     rcb_potm = df[df["player_of_match"].isin(["V Kohli", "AB de Villiers", "CH Gayle"])]
#
#     col4, col5, col6, col7 = st.columns(4)
#     col4.metric("Total Matches", len(rcb))
#     col5.metric("Total Wins", len(rcb_wins))
#     col6.metric("Win %", f"{round(len(rcb_wins) / len(rcb) * 100, 2)}%")
#     col7.metric("Top Player", df[df["winner"] == "Royal Challengers Bengaluru"]["player_of_match"].value_counts().index[0])
#     st.divider()
#
#     col8, col9, col10 = st.columns(3)
#     col8.metric("Home Ground", "M Chinnaswamy Stadium")
#     col9.metric("Home Wins", len(rcb_wins[rcb_wins["venue"] == "M Chinnaswamy Stadium"]))
#     col10.metric("Highest Target", rcb["target_runs"].max())
#     st.divider()

