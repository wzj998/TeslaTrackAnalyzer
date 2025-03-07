import numpy as np
import pandas as pd
import imageio

from AboutDraw import OverlayVideoTool, CurveDrawTool
from Structures import ContinusLaps, Lap, ContinusLapsPrepare
from Structures.ContinusLapsConsts import COL_NAME_LONGITUDE, COL_NAME_LATITUDE
from Utils.WheelUtil import calculate_wheel_diameter

def main():
    csv_paths = ['../SampleData/telemetry-v1-2024-06-16-18_33_19.csv',
                 '../SampleData/telemetry-v1-2025-01-11-14_41_45.csv', ]
    original_wheel_diameter = calculate_wheel_diameter(235, 40, 19)
    adjust_ratios = [calculate_wheel_diameter(265, 35, 18) / original_wheel_diameter,
                     calculate_wheel_diameter(295, 35, 18) / original_wheel_diameter]
    out_video_path = '../SampleOut/overlay_video.mp4'

    continus_lapss = []
    longitude_start = None
    latitude_start = None
    for i_csv_path in range(len(csv_paths)):
        csv_path = csv_paths[i_csv_path]
        df = pd.read_csv(csv_path)
        max_kmh_every_lap = ContinusLapsPrepare.get_max_kmh_every_lap_before_adjust(df)
        print('max_kmh_every_lap:', max_kmh_every_lap)
        if longitude_start is None:
            longitude_start = df[COL_NAME_LONGITUDE].iloc[0]
            latitude_start = df[COL_NAME_LATITUDE].iloc[0]
        continus_lapss.append(ContinusLaps.ContinusLaps(df, adjust_ratios[i_csv_path],
                                                        longitude_start, latitude_start,  # 669.2
                                                        4))

    for i_continus_laps, continus_laps in enumerate(continus_lapss):
        print('---continus_laps', i_continus_laps, '---')
        print('laps:', continus_laps.laps)
        print('laptimes:', ContinusLaps.get_dict_time_str_2_show(continus_laps.laptimes))
        print('validlap_times_dict_sorted:',
              ContinusLaps.get_dict_time_str_2_show(continus_laps.validlap_times_dict_sorted))

    # 两个csv文件各自的最快圈对比，第一个csv文件的最快圈作为参考圈
    laps_compare = [
        Lap.Lap(continus_lapss[0], 0, list(continus_lapss[0].validlap_times_dict_sorted.keys())[0]),
        Lap.Lap(continus_lapss[1], 1, 3),
        Lap.Lap(continus_lapss[1], 1, 7)
    ]
    lap_checkpoints = laps_compare[0]
    # we use first lap in laps_2_compare to generate checkpoints
    df_checkpoints_lap = CurveDrawTool.get_df_checkpoints_lap(lap_checkpoints)
    CurveDrawTool.process_laps_for_x_dist([True] * len(laps_compare), df_checkpoints_lap, laps_compare)

    # generate overlay video, background is purple
    img_paths = OverlayVideoTool.generate_overlay_video_img_paths(continus_lapss[1], 1, 1280, 720,
                                                                  280, 290, laps_compare)
    # save overlay video using ImageIO
    writer = imageio.get_writer(out_video_path, fps=60, macro_block_size=None)
    for i_img_path in range(len(img_paths)):
        path_now = img_paths[i_img_path]

        # use .npz file now
        np_array = np.load(path_now)['arr_0']
        writer.append_data(np_array)

        if i_img_path % 60 == 0:
            print(f'\rsave overlay video: {i_img_path / len(img_paths) * 100:.1f}%', end='')
    writer.close()
    print(f'\rsave overlay video: 100.0%')


if __name__ == "__main__":
    main()
