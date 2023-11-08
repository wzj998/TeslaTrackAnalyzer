import multiprocessing

import pandas as pd
from matplotlib import pyplot as plt

import ContinusLaps
import CurveDrawTool
import Lap
import TrackDrawTool
from ContinusLapsConsts import *


def example_for_diff_continus_laps(continus_lapss):
    print('---example_for_diff_continus_laps---')
    ans = [CurveDrawTool.draw_x_lap_checkpoint_dist_curves_diff_continus_laps_all_same_timeing_line(
        [
            Lap.Lap(continus_lapss[0], 0, list(continus_lapss[0].validlap_times_dict_sorted.keys())[0]),
            Lap.Lap(continus_lapss[1], 1, list(continus_lapss[1].validlap_times_dict_sorted.keys())[0])
        ],
        [
            COL_NAME_TIME_DELTA,
            COL_NAME_SPEED_KMH,
            COL_NAME_BRAKE, COL_NAME_THROTTLE,
        ])]

    for i_continus_laps in range(len(continus_lapss)):
        continus_laps = continus_lapss[i_continus_laps]
        lap_fastest = list(continus_laps.validlap_times_dict_sorted.keys())[0]
        str_i_continus_laps = str(i_continus_laps)
        if i_continus_laps == 1:
            # 绘制最快圈的gps轨迹图
            ans.append(TrackDrawTool.draw_gps_track(continus_laps,
                                                    lap_fastest, lap_fastest,
                                                    False, False, False,
                                                    'GPS Track of Fastest Lap of Period' + str_i_continus_laps))
        if i_continus_laps == 0:
            # 绘制所有圈的gps轨迹图
            ans.append(TrackDrawTool.draw_gps_track(continus_laps,
                                                    continus_laps.laps[0], continus_laps.laps[-1],
                                                    True, True, True, 'GPS Track of Period' + str_i_continus_laps))
    return ans


def main():
    csv_paths = ['../SampleData/telemetry-v1-2023-10-28-16_25_58.csv',
                 '../SampleData/telemetry-v1-2023-10-28-16_48_56.csv']
    continus_lapss = [ContinusLaps.ContinusLaps(pd.read_csv(csv_path), 29) for csv_path in csv_paths]
    for i_continus_laps, continus_laps in enumerate(continus_lapss):
        print('---continus_laps', i_continus_laps, '---')
        print('laps:', continus_laps.laps)
        print('laptimes:', ContinusLaps.get_dict_time_str_2_show(continus_laps.laptimes))
        print('validlap_times_dict_sorted:',
              ContinusLaps.get_dict_time_str_2_show(continus_laps.validlap_times_dict_sorted))

    list_return_example_for_diff_continus_laps = example_for_diff_continus_laps(continus_lapss)
    list_return_example_for_continus_laps = example_for_continus_laps(continus_lapss[0])

    plt.show()


def example_for_continus_laps(continus_laps):
    list_2_return = []

    print('---example_for_continus_laps---')
    laps_2_draw = list(continus_laps.validlap_times_dict_sorted.keys())[:2]
    list_2_return.append(CurveDrawTool.draw_x_lap_checkpoint_dist_curves_same_continus_laps(
        continus_laps, laps_2_draw,
        [
            COL_NAME_TIME_DELTA,
            COL_NAME_SPEED_KMH,
            COL_NAME_BRAKE, COL_NAME_THROTTLE,
        ]))
    # list_2_return.append(CurveDrawTool.draw_x_lap_time_curves_same_continus_laps(
    #     continus_laps.df, laps_2_draw,
    #     [
    #         COL_NAME_SPEED_KMH,
    #         COL_NAME_BRAKE,
    #         COL_NAME_THROTTLE,
    #         # COL_NAME_STEER_ANGLE,
    #         # COL_NAME_LAT_ACCEL, COL_NAME_LONG_ACCEL,
    #         # COL_NAME_POWER_LEVEL,
    #         # COL_NAME_TIRE_SLIP_FRONT_LEFT, COL_NAME_TIRE_SLIP_FRONT_RIGHT,
    #         # COL_NAME_TIRE_SLIP_REAR_LEFT, COL_NAME_TIRE_SLIP_REAR_RIGHT,
    #     ]))
    list_2_return.append(CurveDrawTool.draw_x_total_time_curves(continus_laps.df, continus_laps.laps[0],
                                                                continus_laps.laps[-1],
                                                                [
                                                                    COL_NAME_SPEED_KMH,
                                                                    # COL_NAME_BRAKE, COL_NAME_THROTTLE,
                                                                    COL_NAME_POWER_LEVEL,
                                                                    COL_NAME_STATE_OF_CHARGE,
                                                                    COL_NAME_BRAKE_TEMP_FRONT_LEFT,
                                                                    COL_NAME_BRAKE_TEMP_FRONT_RIGHT,
                                                                    # COL_NAME_REAR_INVERTER_TEMP,
                                                                    COL_NAME_BATTERY_TEMP
                                                                ]))

    return list_2_return


if __name__ == "__main__":
    main()
