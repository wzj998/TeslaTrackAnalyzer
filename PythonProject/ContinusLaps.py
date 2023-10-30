import numpy as np
from sklearn.cluster import KMeans

from ContinusLapsPrepare import *


class ContinusLaps:
    def __init__(self, df_in, altitude=0, b_contain_first_enter_lap=True, b_contain_last_back_lap=True):
        df = df_in
        add_lap_datetime_col(df)
        laps, laptimes, validlaps = calculate_every_lap_time(df, b_contain_first_enter_lap, b_contain_last_back_lap)
        add_total_time_col(df, laps, laptimes)

        add_kmh_col(df)

        longtitude_start = df.iloc[0][COL_NAME_LONGITUDE]
        latitude_start = df.iloc[0][COL_NAME_LATITUDE]
        add_x_m_y_m_col(df, longtitude_start, latitude_start, altitude)
        timing_line_x_m, timing_line_y_m = get_timing_line_x_y_m(df)

        self.laps = laps
        self.laptimes = laptimes
        self.validlaps = validlaps
        self.validlaptimes = {lap: laptimes[lap] for lap in validlaps}
        self.validlap_times_dict_sorted = dict(sorted(self.validlaptimes.items(), key=lambda k: k[1]))
        self.longtitude_start = longtitude_start
        self.latitude_start = latitude_start
        self.altitude = altitude
        self.timing_line_x_m = timing_line_x_m
        self.timing_line_y_m = timing_line_y_m
        self.df = df


def generate_cool_laps_set(laps_2_draw, laptimes: dict):
    if len(laps_2_draw) <= 0:
        raise Exception('laps_2_draw is empty')
    if len(laps_2_draw) == 1:
        return set()

    ans = set()

    laptimes_2_draw = [laptimes[lap] for lap in laps_2_draw]
    laps_by_ms = {}
    for lap in laps_2_draw:
        ms = int(laptimes[lap].timestamp() * 1000)
        if ms not in laps_by_ms.keys():
            laps_by_ms[ms] = [lap]
        else:
            laps_by_ms[ms].append(lap)
    mss = [int(datetime.timestamp() * 1000) for datetime in laptimes_2_draw]
    # 聚类为两类
    kmeans = KMeans(n_clusters=2, random_state=0, n_init=10).fit(np.array(mss).reshape(-1, 1))
    # noinspection PyUnresolvedReferences
    labels = kmeans.labels_
    # 根据聚类结果，选择值较大的那类作为冷却圈
    mss_first_cluster = [mss[index] for index in range(len(mss)) if labels[index] == 0]
    mss_second_cluster = [mss[index] for index in range(len(mss)) if labels[index] == 1]
    if np.mean(mss_first_cluster) > np.mean(mss_second_cluster):
        mss_cool_laps = mss_first_cluster
    else:
        mss_cool_laps = mss_second_cluster
    for ms in mss_cool_laps:
        laps_this_ms = laps_by_ms[int(ms)]
        for lap in laps_this_ms:
            ans.add(lap)

    return ans
