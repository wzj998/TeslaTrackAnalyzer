import math

import pandas as pd
from typing import List

from Structures.ContinusLapsConsts import *


def add_kmh_col(df):
    df.insert(df.columns.get_loc(COL_NAME_SPEED_MPH) + 1, COL_NAME_SPEED_KMH, '')
    df[COL_NAME_SPEED_KMH] = df[COL_NAME_SPEED_MPH].apply(lambda x: x * 1.60934)


def add_lap_datetime_col(df):
    # add new column, just after col ms
    df.insert(df.columns.get_loc(COL_NAME_LAP_MS) + 1, COL_NAME_LAP_DATETIME, '')
    # use datetime
    df[COL_NAME_LAP_DATETIME] = pd.to_datetime(df[COL_NAME_LAP_MS], unit='ms')


# must be called after calculate_every_lap_time
def add_total_time_col(df, laps: List[int], lap_times: dict):
    df.insert(df.columns.get_loc(COL_NAME_LAP_DATETIME) + 1, COL_NAME_TOTAL_MS, '')
    df.insert(df.columns.get_loc(COL_NAME_LAP_DATETIME) + 2, COL_NAME_TOTAL_DATETIME, '')
    sum_ms_laps_b4 = 0
    for lap in laps:
        df_lap = df[df[COL_NAME_LAP] == lap]
        total_ms_now = sum_ms_laps_b4 + df_lap[COL_NAME_LAP_MS]
        df.loc[df_lap.index, COL_NAME_TOTAL_MS] = total_ms_now
        df.loc[df_lap.index, COL_NAME_TOTAL_DATETIME] = pd.to_datetime(total_ms_now, unit='ms')
        lap_time_ms = lap_times[lap].timestamp() * 1000
        sum_ms_laps_b4 += lap_time_ms

    # fill lap 0 with 0
    df.loc[df[df[COL_NAME_LAP] == 0].index, COL_NAME_TOTAL_DATETIME] = pd.to_datetime(0, unit='ms')


def calculate_every_lap_time(df, b_contain_first_enter_lap, b_contain_last_back_lap) -> (list, dict):
    laps = df[COL_NAME_LAP].unique().tolist()
    lap_times_dict = {}
    # find rows col lap changed
    df_lap_changed = df[df[COL_NAME_LAP].diff() >= 1]
    for i in range(len(df_lap_changed)):
        last_row = df.iloc[df_lap_changed.index[i] - 1]
        last_lap = last_row[COL_NAME_LAP]
        lap_times_dict[last_lap] = last_row[COL_NAME_LAP_DATETIME]
    # last lap
    last_row = df.iloc[-1]
    last_lap = last_row[COL_NAME_LAP]
    lap_times_dict[last_lap] = last_row[COL_NAME_LAP_DATETIME]

    validlaps = laps.copy()
    if b_contain_first_enter_lap:
        validlaps = validlaps[1:]
    if b_contain_last_back_lap:
        validlaps = validlaps[:-1]

    return laps, lap_times_dict, validlaps


def add_x_m_y_m_col(df, longtitude_origin, latitude_origin_in, altitude):
    df.insert(df.columns.get_loc(COL_NAME_LATITUDE) + 1, COL_NAME_Y_M, '')
    df.insert(df.columns.get_loc(COL_NAME_LONGITUDE) + 1, COL_NAME_X_M, '')

    # caculate distance x, y to start point, according to longitude, latitude and altitude
    earth_radius_2_use, latitude_origin_rad = calculate_earth_radius_2_use(altitude, latitude_origin_in)
    df[COL_NAME_X_M] = (df[
                            COL_NAME_LONGITUDE] - longtitude_origin) * math.pi / 180 * earth_radius_2_use * \
                       math.cos(latitude_origin_rad)
    df[COL_NAME_Y_M] = (df[
                            COL_NAME_LATITUDE] - latitude_origin_in) * math.pi / 180 * earth_radius_2_use


def calculate_earth_radius_2_use(altitude, latitude_origin_in):
    earth_radius_equator = 6378137.0
    earth_radius_polar = 6356752.3
    latitude_origin_rad = latitude_origin_in * math.pi / 180
    earth_radius_2_use = (earth_radius_equator * earth_radius_polar) / math.sqrt(
        earth_radius_equator ** 2 * math.cos(latitude_origin_rad) ** 2 + earth_radius_polar ** 2 * math.sin(
            latitude_origin_rad) ** 2) + altitude
    return earth_radius_2_use, latitude_origin_rad


def get_avg_timing_line_x_y_m(df):
    rows_lap_diff = df[df[COL_NAME_LAP].diff() >= 1]
    avg_x_m = rows_lap_diff[COL_NAME_X_M].mean()
    avg_y_m = rows_lap_diff[COL_NAME_Y_M].mean()
    return avg_x_m, avg_y_m
