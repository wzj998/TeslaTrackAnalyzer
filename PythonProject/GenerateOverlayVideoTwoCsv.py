import numpy as np
import pandas as pd
import imageio

from AboutDraw import OverlayVideoTool, CurveDrawTool
from Structures import ContinusLaps, Lap


def main():
    csv_paths = ['../SampleData/telemetry-v1-2024-01-28-13_15_43.csv',
                 '../SampleData/telemetry-v1-2024-01-28-14_44_07.csv']
    out_video_path = '../SampleOut/overlay_video.mp4'

    continus_lapss = [ContinusLaps.ContinusLaps(pd.read_csv(csv_path), 29) for csv_path in csv_paths]
    for i_continus_laps, continus_laps in enumerate(continus_lapss):
        print('---continus_laps', i_continus_laps, '---')
        print('laps:', continus_laps.laps)
        print('laptimes:', ContinusLaps.get_dict_time_str_2_show(continus_laps.laptimes))
        print('validlap_times_dict_sorted:',
              ContinusLaps.get_dict_time_str_2_show(continus_laps.validlap_times_dict_sorted))

    # 两个csv文件各自的最快圈对比，第一个csv文件的最快圈作为参考圈
    laps_compare = [
        Lap.Lap(continus_lapss[0], 0, list(continus_lapss[0].validlap_times_dict_sorted.keys())[0]),
        Lap.Lap(continus_lapss[1], 1, list(continus_lapss[1].validlap_times_dict_sorted.keys())[0])
    ]
    lap_checkpoints = laps_compare[0]
    CurveDrawTool.add_col_x_m_y_m_by_lap_checkpoints(laps_compare, lap_checkpoints)
    # we use first lap in laps_2_compare to generate checkpoints
    df_checkpoints_lap = CurveDrawTool.get_df_checkpoints_lap(lap_checkpoints)
    CurveDrawTool.process_laps_for_x_dist([True] * len(laps_compare), df_checkpoints_lap, laps_compare)

    # generate overlay video, background is purple
    img_paths = OverlayVideoTool.generate_overlay_video_img_paths(continus_lapss[1], 1, 1920, 1080,
                                                                  None, None, laps_compare)
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
