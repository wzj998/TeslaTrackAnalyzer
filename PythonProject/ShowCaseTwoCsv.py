import pandas as pd
from matplotlib import pyplot as plt

from Structures import ContinusLaps, Lap
from AboutDraw import CurveDrawTool, TrackDrawTool
from Structures.ContinusLapsConsts import *


def main():
    csv_paths = ['../SampleData/telemetry-v1-2024-01-28-13_15_43.csv',
                 '../SampleData/telemetry-v1-2024-01-28-14_44_07.csv']
    continus_lapss = []
    longtitude_start = None
    latitude_start = None
    for csv_path in csv_paths:
        df = pd.read_csv(csv_path)
        if longtitude_start is None:
            longtitude_start = df[COL_NAME_LONGITUDE].iloc[0]
            latitude_start = df[COL_NAME_LATITUDE].iloc[0]
        continus_lapss.append(ContinusLaps.ContinusLaps(df,
                                                        642.7 / 670.4, longtitude_start, latitude_start,
                                                        29))

    for i_continus_laps, continus_laps in enumerate(continus_lapss):
        print('---continus_laps', i_continus_laps, '---')
        print('laps:', continus_laps.laps)
        print('laptimes:', ContinusLaps.get_dict_time_str_2_show(continus_laps.laptimes))
        print('validlap_times_dict_sorted:',
              ContinusLaps.get_dict_time_str_2_show(continus_laps.validlap_times_dict_sorted))

    # should not be removed, to avoid garbage collection
    # noinspection PyUnusedLocal
    list_return_example_for_diff_continus_laps = example_for_diff_continus_laps(continus_lapss)

    plt.show()


def example_for_diff_continus_laps(continus_lapss):
    print('---example_for_diff_continus_laps---')
    list_2_return = []

    for i_continus_laps in range(len(continus_lapss)):
        continus_laps = continus_lapss[i_continus_laps]
        lap_fastest = list(continus_laps.validlap_times_dict_sorted.keys())[0]
        str_i_continus_laps = str(i_continus_laps)

        # 绘制最快圈的gps轨迹图
        list_2_return.append(TrackDrawTool.draw_gps_track(continus_laps,
                                                          lap_fastest, lap_fastest,
                                                          False, False, False,
                                                          'GPS Track of Fastest Lap of Period' + str_i_continus_laps))

        # 绘制所有圈的gps轨迹图在一张图上
        list_2_return.append(TrackDrawTool.draw_gps_track(continus_laps,
                                                          continus_laps.laps[0], continus_laps.laps[-1],
                                                          True, True, True,
                                                          'GPS Track of Period' + str_i_continus_laps))

        # 横坐标为总时间
        list_2_return.append(CurveDrawTool.draw_x_total_time_curves(continus_laps.df, continus_laps.laps[0],
                                                                    continus_laps.laps[-1],
                                                                    [
                                                                        COL_NAME_SPEED_KMH,
                                                                        COL_NAME_POWER_LEVEL,
                                                                        COL_NAME_STATE_OF_CHARGE,
                                                                        COL_NAME_BRAKE_TEMP_FRONT_LEFT,
                                                                        COL_NAME_BRAKE_TEMP_FRONT_RIGHT,
                                                                        COL_NAME_BATTERY_TEMP
                                                                    ],
                                                                    'Total Time Curves of Period' + str_i_continus_laps))

    # 两个csv文件各自的最快圈对比
    laps_2compare = [
        Lap.Lap(continus_lapss[0], 0, list(continus_lapss[0].validlap_times_dict_sorted.keys())[0]),
        Lap.Lap(continus_lapss[1], 1, list(continus_lapss[1].validlap_times_dict_sorted.keys())[0])
    ]
    # 横坐标为路程
    list_2_return.append([CurveDrawTool.draw_x_lap_checkpoint_dist_curves_diff_continus_laps_all_same_timeing_line(
        laps_2compare,
        [
            COL_NAME_TIME_DELTA,
            COL_NAME_SPEED_KMH,
            COL_NAME_BRAKE, COL_NAME_THROTTLE,
        ])])

    return list_2_return


if __name__ == "__main__":
    main()
