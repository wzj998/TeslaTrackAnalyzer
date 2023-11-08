from ContinusLapsConsts import *


def interpolate_x_m_y_m(df_lap):
    if len(df_lap) <= 2:
        return
    # get first index of df_checkpoints_lap
    i_last = 0
    x_m_last = df_lap.iloc[i_last][COL_NAME_X_M]
    y_m_last = df_lap.iloc[i_last][COL_NAME_Y_M]
    # for row in df_checkpoints_lap, if x_m or y_m change, interpolate x_m and y_m before
    for i in range(len(df_lap)):
        row = df_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        if x_m != x_m_last or y_m != y_m_last:
            # interpolate rows before
            interpolate_x_m_y_m_between(df_lap, i_last, i)
            i_last = i
            x_m_last = x_m
            y_m_last = y_m

    # interpolate final rows
    row_index_last_row = len(df_lap) - 1
    row_index_b4_last = i_last - 1
    if row_index_last_row > row_index_b4_last >= 0:
        interpolate_x_m_y_m_between(df_lap, row_index_b4_last, row_index_last_row)


def interpolate_x_m_y_m_between(df_checkpoints_lap, row_index_last, row_index):
    if row_index_last >= row_index:
        raise Exception('row_index_last >= row_index in interpolate_x_m_y_m_between')
    row_last = df_checkpoints_lap.iloc[row_index_last]
    row = df_checkpoints_lap.iloc[row_index]
    x_m_last = row_last[COL_NAME_X_M]
    y_m_last = row_last[COL_NAME_Y_M]
    x_m = row[COL_NAME_X_M]
    y_m = row[COL_NAME_Y_M]
    x_m_delta = x_m - x_m_last
    y_m_delta = y_m - y_m_last
    row_index_delta = row_index - row_index_last
    for i in range(1, row_index_delta):
        row_index_i = row_index_last + i
        x_m_i = x_m_last + x_m_delta / row_index_delta * i
        y_m_i = y_m_last + y_m_delta / row_index_delta * i
        df_checkpoints_lap.loc[df_checkpoints_lap.index[row_index_i], COL_NAME_X_M] = x_m_i
        df_checkpoints_lap.loc[df_checkpoints_lap.index[row_index_i], COL_NAME_Y_M] = y_m_i
