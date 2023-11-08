import pandas as pd
from matplotlib import pyplot as plt

import ContinusLaps
import CurveDrawTool
import TrackDrawTool
from ContinusLapsConsts import *


def main():
    csv_paths = ['../SampleData/telemetry-v1-2023-10-28-16_25_58.csv',
                 '../SampleData/telemetry-v1-2023-10-28-16_48_56.csv']
    continus_lapss = [ContinusLaps.ContinusLaps(pd.read_csv(csv_path)) for csv_path in csv_paths]

    example_for_continus_laps(continus_lapss[0])
    # _, _, cc_lap_x_checkpoint = CurveDrawTool.draw_x_lap_checkpoint_dist_curves_diff_continues_laps(
    #
    #     [
    #         COL_NAME_TIME_DELTA,
    #         COL_NAME_SPEED_KMH,
    #         COL_NAME_BRAKE, COL_NAME_THROTTLE,
    #     ])

    plt.show()


def example_for_continus_laps(continus_laps):
    # print(continus_laps.df.columns)
    print(continus_laps.df.to_string(max_rows=20))
    print('laps:', continus_laps.laps)
    print('laptimes:', continus_laps.laptimes)
    print('validlap_times_dict_sorted:', continus_laps.validlap_times_dict_sorted)
    # get fisrt 2 laps to draw graph
    laps_2_draw = list(continus_laps.validlap_times_dict_sorted.keys())[:2]
    _, _, cc_lap_x_checkpoint = CurveDrawTool.draw_x_lap_checkpoint_dist_curves_same_continues_laps(
        continus_laps.df, laps_2_draw,
        [
            COL_NAME_TIME_DELTA,
            COL_NAME_SPEED_KMH,
            COL_NAME_BRAKE, COL_NAME_THROTTLE,
        ])
    # _, _, cc_lap_x_time = CurveDrawTool.draw_x_lap_time_curves_same_continues_laps(
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
    #     ])
    _, _, cc_total = CurveDrawTool.draw_x_total_time_curves(continus_laps.df, continus_laps.laps[0],
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
                                                            ])
    # 绘制所有圈的gps轨迹图
    _, _, slider_all = TrackDrawTool.draw_gps_track(continus_laps,
                                                    continus_laps.laps[0], continus_laps.laps[-1],
                                                    True, True, True)
    # # 绘制最快圈的gps轨迹图
    # lap_fastest = list(continus_laps.validlap_times_dict_sorted.keys())[0]
    # _, _, slider_fastest = TrackDrawTool.draw_gps_track(continus_laps,
    #                                                     lap_fastest, lap_fastest,
    #                                                     False, False,
    #                                                     29)


if __name__ == "__main__":
    main()
