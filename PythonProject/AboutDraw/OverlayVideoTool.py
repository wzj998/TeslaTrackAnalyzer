import math
import multiprocessing
import os
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageFont

from AboutDraw import OverlayImgTool
from Structures import ContinusLaps
from Structures.ContinusLapsConsts import *


def generate_samecolor_np(width, height, color):
    return np.full((height, width, 3), color, dtype=np.uint8)


def generate_overlay_video_img_paths(continus_lap: ContinusLaps.ContinusLaps,
                                     width, height,
                                     min_total_s=None, max_total_s=None,
                                     backcolor=(128, 0, 128), fps=60) -> list:
    frame_ms_delta = 1000 / fps
    lap_valid_start = 1

    df = continus_lap.df
    if min_total_s is None:
        min_total_s = 0
    min_total_ms_really = min_total_s * 1000

    last_total_ms = df.iloc[-1][COL_NAME_TOTAL_MS]
    if max_total_s is None:
        max_total_ms = last_total_ms
    else:
        max_total_ms = max_total_s * 1000
    max_total_ms_really = min(last_total_ms, max_total_ms)

    if max_total_ms_really <= min_total_ms_really:
        raise ValueError(f'max_total_ms_really <= min_total_ms_really: {max_total_ms_really} <= {min_total_ms_really}')

    np_back = generate_samecolor_np(width, height, backcolor)

    img_paths = []
    # delete folder overlay_video_imgs if exist
    if os.path.exists('../SampleOut/overlay_video_imgs'):
        for file in os.listdir('../SampleOut/overlay_video_imgs'):
            os.remove(f'../SampleOut/overlay_video_imgs/{file}')
        os.rmdir('../SampleOut/overlay_video_imgs')
    # create folder overlay_video_imgs if not exist
    if not os.path.exists('../SampleOut/overlay_video_imgs'):
        os.makedirs('../SampleOut/overlay_video_imgs')

    font_normal = ImageFont.truetype('arial.ttf', 20)
    font_small = ImageFont.truetype('arial.ttf', 12)

    row_indexes_really_deal = []
    num_frames = int((max_total_ms_really - min_total_ms_really) / frame_ms_delta)
    index_start = df[df[COL_NAME_LAP] >= lap_valid_start].index[0]
    index_now = index_start
    index_last = df.index[-1]
    for i_frame in range(num_frames):
        if i_frame % 60 == 0:
            print(f'\rgenerate_overlay_video find index: {i_frame / num_frames * 100:.1f}%', end='')
        b_found_this_frame = False
        total_ms = i_frame * frame_ms_delta + min_total_ms_really
        while index_now <= index_last:
            row = df.iloc[index_now]
            if row[COL_NAME_TOTAL_MS] >= total_ms:
                b_found_this_frame = True
                row_indexes_really_deal.append(index_now)
                break
            index_now += 1
        if not b_found_this_frame:
            break
    print(f'\rgenerate_overlay_video find index: 100.0%')

    num_processes = os.cpu_count()
    # split row_indexes_really_deal to num_cpu parts
    row_indexes_really_deal_split = np.array_split(row_indexes_really_deal, num_processes)
    power_level_min = df[COL_NAME_POWER_LEVEL].min()
    power_level_max = df[COL_NAME_POWER_LEVEL].max()

    earth_radius_2_use, latitude_origin_rad = ContinusLaps.calculate_earth_radius_2_use(continus_lap.altitude,
                                                                                        continus_lap.latitude_start)
    # 先根据万有引力计算g
    m_earth = 5.9722 * 10 ** 24
    g = 6.67408 * 10 ** -11 * m_earth / (earth_radius_2_use ** 2)
    # 再计算自转加速度
    w = 2 * math.pi / 86400 * math.cos(latitude_origin_rad)
    a = w ** 2 * earth_radius_2_use
    g -= a

    max_accel_length = 0.1
    for _, row in df.iterrows():
        accel_length = math.sqrt(row[COL_NAME_LONG_ACCEL] ** 2 + row[COL_NAME_LAT_ACCEL] ** 2)
        if accel_length > max_accel_length:
            max_accel_length = accel_length

    # use multiprocessing to deal with rows_really_deal_split
    pool = Pool(num_processes)
    results = []
    manager = multiprocessing.Manager()
    lock_finished_frames = manager.Lock()
    finished_frames = manager.Value('i', 0)
    print_really_draw_progress(0, 0, num_frames)
    time_start_really_draw = time.time()
    for i_part, row_indexes in enumerate(row_indexes_really_deal_split):
        result = pool.apply_async(generate_overlay_video_part,
                                  args=(i_part, np_back, df, power_level_min, power_level_max,
                                        row_indexes,
                                        font_normal, font_small,
                                        num_frames, num_processes,
                                        lock_finished_frames, finished_frames, time_start_really_draw,
                                        g, max_accel_length))
        results.append(result)
    pool.close()
    pool.join()
    # get img_paths
    for result in results:
        img_paths.extend(result.get())
    print_really_draw_progress(time.time() - time_start_really_draw, num_frames, num_frames, end_str='\n')

    return img_paths


# noinspection PyUnusedLocal
def generate_overlay_video_part(i_part, np_back, df, power_level_min, power_level_max, row_indexes,
                                font_normal, font_small,
                                num_frames, num_processes, lock_finished_frames, finished_frames, time_start,
                                g, max_accel_length):
    img_paths = []
    img_width, img_height = np_back.shape[1], np_back.shape[0]
    img_back = Image.fromarray(np_back)
    len_row_indexes = len(row_indexes)
    prgress_last_report = 0
    i_last_report = 0
    delta_progress_2_report = 0.01  # * num_processes
    for i, index in enumerate(row_indexes):
        row = df.iloc[index]

        img = img_back.copy()
        OverlayImgTool.draw_overlays_on_img(img, row, power_level_min, power_level_max,
                                            img_width, img_height,
                                            font_normal, font_small,
                                            g, max_accel_length)

        # save img will trigger shell infrastructure
        # noinspection PyTypeChecker
        np_arr = np.array(img)
        img_path = f'../SampleOut/overlay_video_imgs/{index}'
        img_path_with_npz = f'{img_path}.npz'
        # save with compression
        retry_times = 0
        while not os.path.exists(img_path_with_npz):
            try:
                np.savez_compressed(img_path, arr_0=np_arr)
            except PermissionError:
                retry_times += 1
                if retry_times > 10:
                    raise PermissionError(
                        f'generate_overlay_video_part: {img_path_with_npz} PermissionError retry_times > 10')
        img_paths.append(img_path_with_npz)

        # print progress of this part
        progress = (i + 1) / len_row_indexes
        if progress - prgress_last_report >= delta_progress_2_report:
            with lock_finished_frames:
                finished_frames.value += i - i_last_report
                elapsed_time = time.time() - time_start
                print_really_draw_progress(elapsed_time, finished_frames.value, num_frames)
            prgress_last_report = progress
            i_last_report = i
    return img_paths


def print_really_draw_progress(elapsed_time, finished_frames_value, num_frames, end_str=''):
    if finished_frames_value > 0:
        remaining_time_str = f'remaining time: {elapsed_time / finished_frames_value * (num_frames - finished_frames_value):.1f}s'
    else:
        remaining_time_str = ''
    print(f'\rgenerate_overlay_video really draw: '
          f'{finished_frames_value / num_frames * 100:.1f}% '
          f'elapsed time: {elapsed_time:.1f}s '
          f'{remaining_time_str}',
          end=end_str)
