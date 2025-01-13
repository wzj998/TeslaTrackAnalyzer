import pandas as pd
from matplotlib import pyplot as plt

from Structures import ContinusLaps, Lap, ContinusLapsPrepare
from AboutDraw import CurveDrawTool, TrackDrawTool
from Structures.ContinusLapsConsts import *
from Utils.WheelUtil import calculate_wheel_diameter

def main():
    csv_paths = ['../SampleData/telemetry-v1-2025-01-05-16_44_02.csv',
                 '../SampleData/telemetry-v1-2025-01-11-14_41_45.csv', ]
    
    dfs = []
    max_kmh_every_laps = []
    for i_csv_path in range(len(csv_paths)):
        df = pd.read_csv(csv_paths[i_csv_path])
        dfs.append(df)    
        max_kmh_every_lap = ContinusLapsPrepare.get_max_kmh_every_lap_before_adjust(df)        
        print('max_kmh_every_lap:', max_kmh_every_lap)
        max_kmh_every_laps.append(max_kmh_every_lap)

    original_wheel_diameter = calculate_wheel_diameter(235, 40, 19)
    adjust_ratios = [calculate_wheel_diameter(295, 35, 18) / original_wheel_diameter,
                     calculate_wheel_diameter(295, 35, 18) / original_wheel_diameter]

    # adjust_ratios = [
    #     ContinusLapsPrepare.get_avg_adjust_ratio(max_kmh_every_laps[0], 1, [171.49, 164.35, 170.51, 164.38]),
    #     ContinusLapsPrepare.get_avg_adjust_ratio(max_kmh_every_laps[1], 2, [169.9, 169.68, 159.88, 167.61])
    # ]
    print('adjust_ratios:', adjust_ratios)

    continus_lapss = []
    longitude_start = None
    latitude_start = None
    # for csv_path in csv_paths:
    for i_csv_path in range(len(dfs)):
        df = dfs[i_csv_path]    
        if longitude_start is None:
            longitude_start = df[COL_NAME_LONGITUDE].iloc[0]
            latitude_start = df[COL_NAME_LATITUDE].iloc[0]        
        continus_lapss.append(ContinusLaps.ContinusLaps(df, adjust_ratios[i_csv_path],
                                                        longitude_start, latitude_start,
                                                        4))

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
