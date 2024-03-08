import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


#streamlit global parameters and layout
st.set_page_config(layout="wide", page_title="Badge Criteria Analysis")
st.title("Badge Criteria Analysis")
left_empty_col, main_body, right_column = st.columns([2, 15, 5])

#read data
data = pd.read_csv("resources/Technical Challenge Data Analyst.csv")
data.fillna(0, inplace=True)
data = data.astype('int64')
data['USER_ID'] = data['USER_ID'].astype(str)
event_columns = ['POSTS_CREATED','REPLIES_RECEIVED','THANKYOUS_RECEIVED','EVENTS_CREATED','EVENT_PARTICIPANTS','ITEMS_GIFTED','PLACES_RECOMMENDED']
# data['active'] = (data[event_columns] != 0).any(axis=1)

#dataframe with distribution of events per each event type
# distribution_events_df = data.groupby('LAST_X_WEEKS').describe().drop(columns=['USER_ID']).transpose()
# distribution_events_df = data.set_index('LAST_X_WEEKS').stack().reset_index().rename(columns={'level_1': 'groups', 0: 'values'})

with main_body:
    st.markdown('''
This is an interactive dashboard that helps to analyse user participation on the platform. The goal of this dashboard is to understand the user distribution for each of the following events:
- Posts_created: Number of posts the user created in given time frame
- Replies_received: Number of replies to posts the user received in given time frame
- Thankyous_received: Number of thankyou reactions the user received in given time frame
- Events_created: Number of events created by user in given time frame
- Event_participants: Number of users that attended events by user in given time frame
- Items_gifted: Number of items the user gave away for free in given time frame
- Places_recommended: Number of places the user recommended in given time frame
                
You can use the following widgets to select a subset of data for exploration. The dashboard will adapt instantly. 
                ''')
    #parameters selected via input elements
    week_select = st.selectbox(
        'Choose the number of weeks',
        data['LAST_X_WEEKS'].unique(),
        help='The timeframe that you want to include data for (up to 4, 6, 8 or 12 weeks)')
    event_select = st.selectbox(
        'Choose the event',
        ['All']+event_columns,
        help='The event type (all or one of the above)')
    not_null_select = st.radio(
        'Should non-active users be included?',
        [True, False],
        help='Whether to include non-active users. For allevent types  a non-active user is someone who had none of the events in the selected timeframe. For one selected event only non-zero entries are included.')
    

    week_select_df = data[data['LAST_X_WEEKS']==week_select]
    if event_select!='All':
        week_event_select_df = week_select_df[event_select].reset_index()
        dist_columns = [event_select]
        # week_event_select_df['active'] = (week_event_select_df != 0)
        if not not_null_select:
            week_event_select_df = week_event_select_df[week_event_select_df!=0]
    else:
        week_event_select_df = week_select_df[event_columns]
        dist_columns = event_columns
        if not not_null_select:
            week_event_select_df = week_event_select_df[(week_event_select_df[dist_columns] != 0).any(axis=1)]

    # st.write(week_event_select_df)

    fig = make_subplots(rows=1, cols=len(dist_columns))
    for i, var in enumerate(dist_columns):
        fig.add_trace(
            go.Box(y=week_event_select_df[var],
            name=var),
            row=1, col=i+1
        )

    fig.update_traces(boxpoints=False,jitter=.3)
    st.plotly_chart(fig,use_container_width=True)

    st.divider()
    st.header("Badges")
    st.subheader("Event Planner")
    pct_users_badge = np.round(data[data['EVENTS_CREATED']>0]['USER_ID'].nunique()*100/data['USER_ID'].nunique(),1)
    badge_df_per_week = data[data['EVENTS_CREATED']>0].groupby('LAST_X_WEEKS').agg({'EVENTS_CREATED':'mean','EVENT_PARTICIPANTS':'mean','USER_ID':'nunique'})
    badge_df_per_week['% of all users'] = badge_df_per_week['USER_ID']*100/data['USER_ID'].nunique()
    badge_df_per_week.rename(columns={'EVENTS_CREATED':"Avg. Events created per user",
                                      'EVENT_PARTICIPANTS':"Avg. number of participants",
                                      'USER_ID':'Number of users who created events'},inplace=True)

    st.markdown(f'''This badge is given to users that create events with a certain number of participants in given timeframe.  
{pct_users_badge}% of all users created at least 1 event in the last 12 weeks.
                ''')
    st.dataframe(badge_df_per_week)

    col1,col2,col3 = st.columns(3)
    user_pct_filter = col1.slider(label="% of users to award the badge to", 
                                  min_value=1,
                                  max_value=50,
                                  value=20)
    week_filter = col2.selectbox(
        'Choose the number of weeks',
        badge_df_per_week.index)

    # fig = px.histogram(data[data['EVENTS_CREATED']>0], x="EVENTS_CREATED", color="LAST_X_WEEKS")
    # st.plotly_chart(fig,use_container_width=True)

    #filter out for events more than 1 and number of perticipants not 0
    event_df = data[(data['EVENTS_CREATED']>0)&(data['LAST_X_WEEKS']==week_filter)&(data['EVENT_PARTICIPANTS']>0)].sort_values(by = 'EVENTS_CREATED', ascending = False)
    event_df['Events created, cummulative'] = event_df['EVENTS_CREATED'].cumsum()
    event_df['%of events created, cummulative'] = event_df['Events created, cummulative']/event_df['EVENTS_CREATED'].sum()
    event_df['Avg. participants/event'] = np.round(event_df['EVENT_PARTICIPANTS']/event_df['EVENTS_CREATED'])
    event_df = event_df[['EVENTS_CREATED','Avg. participants/event','USER_ID','Events created, cummulative','%of events created, cummulative']]
    event_df_top_pct = event_df.head(int(len(event_df)*(user_pct_filter/100))).reset_index(drop=True)
    st.dataframe(event_df_top_pct)
    st.markdown(f"For top {user_pct_filter}% of users to earn the badge they need to create at least {event_df_top_pct['EVENTS_CREATED'].min()} events with {event_df_top_pct['Avg. participants/event'].min()} participants.")

