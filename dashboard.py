import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from tools import *

# streamlit global parameters and layout
st.set_page_config(layout="wide", page_title="Badge Criteria Analysis")
st.title("Badge Criteria Analysis")
left_empty_col, main_body, right_column = st.columns([2, 15, 5])

# read data
data = read_data("resources/Technical Challenge Data Analyst.csv")

# action columns names
action_columns = [
    "POSTS_CREATED",
    "REPLIES_RECEIVED",
    "THANKYOUS_RECEIVED",
    "EVENTS_CREATED",
    "EVENT_PARTICIPANTS",
    "ITEMS_GIFTED",
    "PLACES_RECOMMENDED",
]

#a variable for storing the column name for the date period
period_column_name = "LAST_X_WEEKS"

# count the percentage of users with non-zero actions per week, out of total
users_per_action_type = get_users_per_action(data, action_columns)


with main_body:
    st.markdown(
        """
This is an interactive dashboard that helps to analyse user participation on the platform. The goal of this dashboard is to understand the user distribution for each of the following actions:
- Posts_created: Number of posts the user created in given time frame
- Replies_received: Number of replies to posts the user received in given time frame
- Thankyous_received: Number of thankyou reactions the user received in given time frame
- Events_created: Number of actions created by user in given time frame
- Event_participants: Number of users that attended actions by user in given time frame
- Items_gifted: Number of items the user gave away for free in given time frame
- Places_recommended: Number of places the user recommended in given time frame
                
You can use the following widgets to select a subset of data for exploration. The dashboard will adapt instantly. 
                """
    )
    # parameters selected via input elements
    week_select = st.selectbox(
        "Choose the number of weeks",
        data[period_column_name].unique(),
        help="The timeframe that you want to include data for (up to 4, 6, 8 or 12 weeks)",
    )
    action_select = st.selectbox(
        "Choose the action",
        ["All"] + action_columns,
        help="The action type (all or one of the above)",
    )
    not_null_select = st.radio(
        "Should non-active users be included?",
        [True, False],
        help="Whether to include non-active users. For all action types  a non-active user is someone who had none of the actions in the selected timeframe. For one selected action only non-zero entries are included.",
    )

    # filter the dataset for the selected week
    week_select_df = data[data[period_column_name] == week_select]

    # if all actions are selected the full dataset with only action columns is returned
    if action_select != "All":
        week_action_select_df = week_select_df[action_select].reset_index()
        dist_columns = [action_select]
        # if users with only non zero actions are selected
        if not not_null_select:
            week_action_select_df = week_action_select_df[week_action_select_df != 0]
    else:
        week_action_select_df = week_select_df[action_columns]
        dist_columns = action_columns
        if not not_null_select:
            week_action_select_df = week_action_select_df[
                (week_action_select_df[dist_columns] != 0).any(axis=1)
            ]

    st.write(
        f"Distribution(s) of the number of actions performed by users in the last {week_select} weeks:"
    )
    # plotly chart with boxplots per all actions or just one selected
    fig = make_subplots(rows=1, cols=len(dist_columns))
    for i, var in enumerate(dist_columns):
        fig.add_trace(go.Box(y=week_action_select_df[var], name=var), row=1, col=i + 1)

    fig.update_traces(boxpoints=False, jitter=0.3)
    st.plotly_chart(fig, use_container_width=True)

    # dataframe table with distribution of users per action per week
    st.write(
        "Percentage of users with at least 1 action of each type out of total number of users in the last N weeks."
    )
    st.dataframe(users_per_action_type)

    st.divider()

    # specific badges
    st.header("Badges")
    col1, col2, col3 = st.columns(3)
    badge_select = col1.selectbox(
        "Select the badge type",
        (
            "Event Planner",
            "Conversation Starter",
            "Philanthropist",
            "Helping Hand",
            "Local Guide",
        ),
    )
    user_pct_filter = col2.slider(
        label="top % of users to award the badge to",
        min_value=1,
        max_value=50,
        value=20,
        help="Where the threshold for the badge achievement lies if all users are ranked by the number of events they created",
    )
    week_filter = col3.selectbox(
        "Choose the number of weeks", data[period_column_name].unique()
    )

    # selected badge type
    st.subheader(badge_select)

    # placeholders for the text and visualisation for each selected badge
    if badge_select == "Event Planner":
        main_action_column, second_action_column, second_column_limit = (
            "EVENTS_CREATED",
            "EVENT_PARTICIPANTS",
            1,
        )
        badge_data = data
        badge_description = "This badge is given to users that create events with a certain number of participants in given timeframe"
        most_common_action = "created only 1 event with 1 participant out of all users who created events"
        action_metric_name = "participants"
        action_verb = "create"
    elif badge_select == "Conversation Starter":
        main_action_column, second_action_column, second_column_limit = (
            "POSTS_CREATED",
            "REPLIES_RECEIVED",
            0,
        )
        badge_data = data[data["USER_ID"] != "17211"]
        badge_description = "This badge is given to users that create a certain amount of posts with replies in given timeframe"
        most_common_action = (
            "created only 1 post with 0 replies out of all users who posted"
        )
        action_metric_name = "replies"
        action_verb = "create"
    elif badge_select == "Philanthropist":
        main_action_column, second_action_column, second_column_limit = (
            "ITEMS_GIFTED",
            None,
            0,
        )
        badge_data = data
        badge_description = "This badge is given to users that give away items for free in given timeframe"
        most_common_action = (
            "gifted only 1 item of all users who gifted on the marketplace"
        )
        action_verb = "give away"
    elif badge_select == "Helping Hand":
        main_action_column, second_action_column, second_column_limit = (
            "THANKYOUS_RECEIVED",
            None,
            0,
        )
        badge_data = data
        badge_description = "This badge is given to users that receive thank you messages in given timeframe"
        most_common_action = (
            "received only 1 thank-you message of all users who received any"
        )
        action_verb = "receive"
    elif badge_select == "Local Guide":
        main_action_column, second_action_column, second_column_limit = (
            "PLACES_RECOMMENDED",
            None,
            0,
        )
        badge_data = data
        badge_description = (
            "This badge is given to users that recommend places in given timeframe"
        )
        most_common_action = "recommended only 1 place of all users who recommended any"
        action_verb = "recommend"

    # get the dataframes with weekly distribution of users per action as well as a ranked dataframe by the number of actions performed
    (
        pct_users_with_action,
        pct_users_with_one_action,
        action_df_per_week,
        action_df_cumm,
    ) = get_action_stats(
        badge_data,
        week_filter,
        main_action_column,
        second_action_column,
        second_column_limit,
    )

    st.markdown(
        f"""{badge_description}.  
**{pct_users_with_action}%** of all users created at least 1 action in the last 12 weeks.  
**{pct_users_with_one_action}%** of all users {most_common_action} in the last 12 weeks.
                """
    )
    # avg. number of actions per user, total number of users who did the action and a percentage of active users out of all per each week
    st.dataframe(action_df_per_week)

    # top X% of users who performed this action, the X is selected in the slider filter
    action_df_top_pct = action_df_cumm.head(
        int(len(action_df_cumm) * (user_pct_filter / 100))
    ).reset_index(drop=True)
    st.write(
        f"List of users who performed at least 1 action of type {main_action_column} ranked by the number of actions, top {user_pct_filter}% selected:"
    )
    st.dataframe(action_df_top_pct)

    # relationship between first and second action columns (e.g. events and event participants), colored by the number of users who created such events
    if second_action_column:
        participants_per_action_freq = (
            badge_data[
                (badge_data[main_action_column] > 0)
                & (badge_data[period_column_name] == week_filter)
            ]
            .groupby(
                [main_action_column, second_action_column + "_AVG", "LAST_X_WEEKS"]
            )["USER_ID"]
            .nunique()
            .reset_index()
        )
        participants_per_action_freq.rename(
            columns={"USER_ID": "Number of Users"}, inplace=True
        )
        fig = px.scatter(
            participants_per_action_freq,
            x=main_action_column,
            y=second_action_column + "_AVG",
            color="Number of Users",
        )
    else:  # only the number of events matters, the chart is a simple distribution of users per number of actions
        participants_per_action_freq = (
            badge_data[
                (badge_data[main_action_column] > 0)
                & (badge_data[period_column_name] == week_filter)
            ]
            .groupby([main_action_column, "LAST_X_WEEKS"])["USER_ID"]
            .nunique()
            .reset_index()
        )
        participants_per_action_freq.rename(
            columns={"USER_ID": "Number of Users"}, inplace=True
        )
        fig = px.scatter(
            participants_per_action_freq, x=main_action_column, y="Number of Users"
        )

    st.plotly_chart(fig, use_container_width=True, theme=None)

    # percentage of total users that will receive a badge
    badge_achievers_pct = np.round(
        action_df_cumm[
            action_df_cumm[main_action_column]
            >= action_df_top_pct[main_action_column].min()
        ]["USER_ID"].nunique()
        * 100
        / badge_data[badge_data[period_column_name] == week_filter]["USER_ID"].nunique(),
        1,
    )

    if second_action_column:
        st.markdown(
            f"""For top {user_pct_filter}% of users to earn the badge they need to {action_verb} at least {action_df_top_pct[main_action_column].min()} actions with {action_df_top_pct[second_action_column+'_AVG'].min()} {action_metric_name} on average in {week_filter} weeks.  
    This way the bagde would be awarded to {badge_achievers_pct}% of all users.
                """
        )
    else:
        st.markdown(
            f"""For top {user_pct_filter}% of users to earn the badge they need to {action_verb} at least {action_df_top_pct[main_action_column].min()} actions in {week_filter} weeks.  
    This way the bagde would be awarded to {badge_achievers_pct}% of all users.
                """
        )
    st.divider()
