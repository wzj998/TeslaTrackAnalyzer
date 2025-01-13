import imageio
import numpy as np
import pandas as pd

from AboutDraw import OverlayVideoTool, CurveDrawTool
from Structures import ContinusLaps, Lap, ContinusLapsPrepare
from Structures.ContinusLapsConsts import COL_NAME_LONGITUDE, COL_NAME_LATITUDE
from Utils.WheelUtil import calculate_wheel_diameter


def main():
    csv_path = '../SampleData/telemetry-v1-2025-01-11-15_44_35.csv'
    out_video_path = '../SampleOut/overlay_video.mp4'

    df = pd.read_csv(csv_path)
    longitude_start = df[COL_NAME_LONGITUDE].iloc[0]
    latitude_start = df[COL_NAME_LATITUDE].iloc[0]
    original_wheel_diameter = calculate_wheel_diameter(235, 40, 19)
    max_kmh_every_lap = ContinusLapsPrepare.get_max_kmh_every_lap_before_adjust(df)
    print('max_kmh_every_lap:', max_kmh_every_lap)
    continus_laps = ContinusLaps.ContinusLaps(df,
                                              calculate_wheel_diameter(295, 35, 18) / original_wheel_diameter,
                                              longitude_start, latitude_start, 4)
    laps_compare = [
        Lap.Lap(continus_laps, 0, list(continus_laps.validlap_times_dict_sorted.keys())[0]),
        Lap.Lap(continus_laps, 0, list(continus_laps.validlap_times_dict_sorted.keys())[1])
    ]  # empty means do not show time delta
    if len(laps_compare) > 0:        
        lap_checkpoints = laps_compare[0]        
        df_checkpoints_lap = CurveDrawTool.get_df_checkpoints_lap(lap_checkpoints)
        CurveDrawTool.process_laps_for_x_dist([True] * len(laps_compare), df_checkpoints_lap, laps_compare)
    i_lap_compare_really = 1
    # generate overlay video, background is purple
    img_paths = OverlayVideoTool.generate_overlay_video_img_paths(continus_laps, 0, 1280, 720,
                                                                  480, 600, laps_compare, i_lap_compare_really)
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
