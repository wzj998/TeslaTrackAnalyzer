import math
import os

import pandas as pd
from typing import List

from Structures.ContinusLapsConsts import *
from Utils.MyMath import EPS
import multiprocessing

def get_max_kmh_every_lap_before_adjust(df):
    ans = {}
    # 获取每圈最大速度
    laps = df[COL_NAME_LAP].unique()
    for lap in laps:
        df_lap = df[df[COL_NAME_LAP] == lap]
        ans[lap] = df_lap[COL_NAME_SPEED_MPH].max() * KMH_DIV_MPH  # 转换为km/h
    return ans


def get_avg_adjust_ratio(max_kmh_every_lap, lap_index_start, max_kmh_gps_list):
    sum_ratio = 0
    count_ratio = 0
    for i_lap in range(lap_index_start, len(max_kmh_gps_list)):
        index_max_kmh_every_lap = lap_index_start + i_lap
        if index_max_kmh_every_lap not in max_kmh_every_lap:
            break
        kmh_df = max_kmh_every_lap[index_max_kmh_every_lap]
        kmh_gps = max_kmh_gps_list[i_lap]
        if kmh_df < EPS:
            raise Exception("kmh_df too small")
        ratio_now = kmh_gps / kmh_df
        print(f"{kmh_gps}/{kmh_df}={ratio_now}")
        sum_ratio += ratio_now
        count_ratio += 1

    if count_ratio == 0:
        raise Exception("count_ratio is 0")
    avg_ratio = sum_ratio / count_ratio
    print(f"avg_ratio={avg_ratio}")
    return avg_ratio    


def add_kmh_col(df, adjust_ratio):
    df.insert(df.columns.get_loc(COL_NAME_SPEED_MPH) + 1, COL_NAME_SPEED_KMH, 0)
    df[COL_NAME_SPEED_KMH] = df[COL_NAME_SPEED_MPH].apply(lambda x: x * KMH_DIV_MPH * adjust_ratio)


def calculate_speed_gps(df, x, ms_smooth_half_window):
    row_index_now = x.name
    row_index_start = row_index_now - ms_smooth_half_window
    if row_index_start < 0:
        row_index_start = 0
    row_index_end = row_index_now + ms_smooth_half_window
    if row_index_end >= len(df):
        row_index_end = len(df) - 1

    time = (df.iloc[row_index_end][COL_NAME_TOTAL_MS] - df.iloc[row_index_start][COL_NAME_TOTAL_MS]) / 1000
    if time == 0:
        return 0

    x_start = df.iloc[row_index_start][COL_NAME_X_M]
    y_start = df.iloc[row_index_start][COL_NAME_Y_M]
    x_end = df.iloc[row_index_end][COL_NAME_X_M]
    y_end = df.iloc[row_index_end][COL_NAME_Y_M]
    distance = math.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)

    speed = distance / time * 3.6

    if row_index_now % 250 == 0:
        progress = (row_index_now + 1) / len(df)
        print(f'\rcalculate_speed_gps progress: {progress * 100:.1f}%', end='')

    return speed


def add_gps_kmh_col(df):
    rows_smooth_half_window = 10

    # use COL_NAME_Y_M, COL_NAME_X_M to calculate speed
    df.insert(df.columns.get_loc(COL_NAME_Y_M) + 1, COL_NAME_SPEED_GPS, 0)

    df[COL_NAME_SPEED_GPS] = df.apply(lambda x: calculate_speed_gps(df, x, rows_smooth_half_window), axis=1)
    print('\rcalculate_speed_gps progress: 100.0%')
    # TODO: use multiprocessing to speed up

    # print all COL_NAME_SPEED_KMH and gps speed in same line
    print(df[[COL_NAME_SPEED_KMH, COL_NAME_SPEED_GPS]].to_string())
    # print max speed
    print('max speed kmh:', df[COL_NAME_SPEED_KMH].max())
    print('max speed gps:', df[COL_NAME_SPEED_GPS].max())


def add_lap_datetime_col(df):
    # add new column, just after col ms
    df.insert(df.columns.get_loc(COL_NAME_LAP_MS) + 1, COL_NAME_LAP_DATETIME, 0)
    # use datetime
    df[COL_NAME_LAP_DATETIME] = pd.to_datetime(df[COL_NAME_LAP_MS], unit='ms')


# must be called after calculate_every_lap_time
def add_total_time_col(df, laps: List[int], lap_times: dict):
    df.insert(df.columns.get_loc(COL_NAME_LAP_DATETIME) + 1, COL_NAME_TOTAL_MS, 0)
    df.insert(df.columns.get_loc(COL_NAME_LAP_DATETIME) + 2, COL_NAME_TOTAL_DATETIME, 0)
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


def calculate_every_lap_time(df, b_contain_first_enter_lap, b_contain_last_back_lap):
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


def add_x_m_y_m_col_new(df, longtitude_origin, latitude_origin_in, altitude):
    df.insert(df.columns.get_loc(COL_NAME_LATITUDE) + 1, COL_NAME_Y_M, 0)
    df.insert(df.columns.get_loc(COL_NAME_LONGITUDE) + 1, COL_NAME_X_M, 0)

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

def get_g(altitude, latitude):
    earth_radius_2_use, latitude_origin_rad = calculate_earth_radius_2_use(altitude, latitude)
    # 先根据万有引力计算g
    m_earth = 5.9722 * 10 ** 24
    g = 6.67408 * 10 ** -11 * m_earth / (earth_radius_2_use ** 2)
    # 再计算自转加速度
    w = 2 * math.pi / 86400 * math.cos(latitude_origin_rad)
    a = w ** 2 * earth_radius_2_use
    g -= a

    return g
