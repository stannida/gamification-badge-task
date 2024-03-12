import pandas as pd
import numpy as np


def read_data(file_path):
    """
    Read the dataset and clean it: fill null values, convert to the right format and introduce missing columns
    """

    data = pd.read_csv(file_path)
    data.fillna(0, inplace=True)

    # convert all columns but user IDs to integer
    data = data.astype("int64")
    data["USER_ID"] = data["USER_ID"].astype(str)

    # New column with average number of participants per event
    data["AVG_PARTICIPANTS_action"] = np.round(
        data["EVENT_PARTICIPANTS"] / data["EVENTS_CREATED"]
    )

    return data


def get_users_per_action(data, action_columns):
    """
    Count the percentage of users with non-zero actions per week, out of total
    Args:
        data: dataframe
        action_columns: list of column names

    Returns:
        users_per_action_type: dataframe with number and percentage of users per action and week, sorted by week and % of users in descending order
    """
    users_per_action_type = pd.DataFrame()
    for action_type in action_columns:
        non_empty_action_data = data[data[action_type] > 0]
        users_for_each_action = (
            non_empty_action_data.groupby(["LAST_X_WEEKS"])["USER_ID"]
            .nunique()
            .reset_index()
        )
        users_for_each_action["ACTION_TYPE"] = action_type
        users_per_action_type = pd.concat(
            [users_per_action_type, users_for_each_action]
        )

    users_per_action_type = users_per_action_type.merge(
        data.groupby("LAST_X_WEEKS").agg("USER_ID").nunique().reset_index(),
        how="left",
        on="LAST_X_WEEKS",
        suffixes=("_ACTION", "_TOTAL"),
    )
    users_per_action_type["%_OF_TOTAL_USERS"] = (
        users_per_action_type["USER_ID_ACTION"]
        * 100
        / users_per_action_type["USER_ID_TOTAL"]
    )

    return users_per_action_type[
        ["LAST_X_WEEKS", "ACTION_TYPE", "USER_ID_ACTION", "%_OF_TOTAL_USERS"]
    ].sort_values(["LAST_X_WEEKS", "%_OF_TOTAL_USERS"], ascending=[False, True])


def get_action_stats(
    data, week_filter, main_action_column, second_action_column, second_column_limit
):
    """
    Get dataframes for the selected action types and percentages of active users.
    Args:
        data: dataframe, users and actions dataframe
        week_filter: int, filter for the last X weeks
        main_action_column: string, name for the action type column
        second_action_column: string, name for the action metric column, like participants or replies. None if not applicable
        second_column_limit: integer, most common value for the action metric column. 0 if not applicable

    Returns:
        pct_users_with_action: float, percentage of users who have done at least 1 action out of all users
        pct_users_with_one_action: float, percentage of users who have done exctly 1 action (and 0 or 1 participants/replies) out of all users who have done this action
        action_df_per_week: dataframe, avg. number of actions per user, avg. number of participants/replies per action, number of users who have done this action and percentage of total PER EACH WEEK PERIOD
        action_df_cumm: dataframe, data for each user who performed an action with cummulative number and percentage for action number and ranked by the number of actions
    """
    pct_users_with_action = np.round(
        data[data[main_action_column] > 0]["USER_ID"].nunique()
        * 100
        / data["USER_ID"].nunique(),
        1,
    )
    if second_action_column:
        pct_users_with_one_action = np.round(
            data[
                (data[main_action_column] == 1)
                & (data[second_action_column] == second_column_limit)
            ]["USER_ID"].nunique()
            * 100
            / data[(data[main_action_column] > 0)]["USER_ID"].nunique(),
            1,
        )
        action_df_per_week = (
            data[data[main_action_column] > 0]
            .groupby("LAST_X_WEEKS")
            .agg(
                {
                    main_action_column: "mean",
                    second_action_column: "mean",
                    "USER_ID": "nunique",
                }
            )
        )
        action_df_per_week.rename(
            columns={
                main_action_column: "Avg. action per user",
                second_action_column: "Avg. number of participants/replies",
                "USER_ID": "Number of users",
            },
            inplace=True,
        )

        data[second_action_column + "_AVG"] = (
            data[second_action_column] / data[main_action_column]
        )
        data[second_action_column + "_AVG"] = data[
            second_action_column + "_AVG"
        ].round()
        action_df_cumm = data[
            (data[main_action_column] > 0)
            & (data["LAST_X_WEEKS"] == week_filter)
            & (data[second_action_column + "_AVG"] > 0)
        ].sort_values(by=main_action_column, ascending=False)

        action_df_cumm = action_df_cumm[
            [main_action_column, second_action_column + "_AVG", "USER_ID"]
        ]
    else:
        pct_users_with_one_action = np.round(
            data[(data[main_action_column] == 1)]["USER_ID"].nunique()
            * 100
            / data[(data[main_action_column] > 0)]["USER_ID"].nunique(),
            1,
        )
        action_df_per_week = (
            data[data[main_action_column] > 0]
            .groupby("LAST_X_WEEKS")
            .agg({main_action_column: "mean", "USER_ID": "nunique"})
        )
        action_df_per_week.rename(
            columns={
                main_action_column: "Avg. action per user",
                "USER_ID": "Number of users",
            },
            inplace=True,
        )

        action_df_cumm = data[
            (data[main_action_column] > 0) & (data["LAST_X_WEEKS"] == week_filter)
        ].sort_values(by=main_action_column, ascending=False)
        action_df_cumm = action_df_cumm[[main_action_column, "USER_ID"]]

    action_df_per_week["% of all users"] = (
        action_df_per_week["Number of users"] * 100 / data["USER_ID"].nunique()
    )

    action_df_cumm["TOTAL_ACTIONS_CUMMULATIVE"] = action_df_cumm[
        main_action_column
    ].cumsum()
    action_df_cumm["%_OF_ACTIONS_CUMMULATIVE"] = (
        action_df_cumm["TOTAL_ACTIONS_CUMMULATIVE"]
        / action_df_cumm[main_action_column].sum()
    )

    return (
        pct_users_with_action,
        pct_users_with_one_action,
        action_df_per_week,
        action_df_cumm,
    )
