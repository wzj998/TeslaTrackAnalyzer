import multiprocessing
import os
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip

from Structures import ContinusLaps
from Structures.ContinusLapsConsts import *


def generate_samecolor_np(width, height, color):
    return np.full((height, width, 3), color, dtype=np.uint8)


def draw_text(draw, text, x, y, font, text_color=(255, 255, 255)):
    draw.text((x, y), text, font=font, fill=text_color, stroke_width=2, stroke_fill=(0, 0, 0))


def generate_overlay_video(continus_lap: ContinusLaps.ContinusLaps,
                           width, height, s_limit=None,
                           backcolor=(0, 255, 0), fps=60, lap_start=1) -> ImageSequenceClip:
    frame_ms_delta = 1000 / fps

    df = continus_lap.df
    last_total_ms = df.iloc[-1][COL_NAME_TOTAL_MS]
    if s_limit is None:
        ms_limit = last_total_ms
    else:
        ms_limit = s_limit * 1000
    max_total_ms_really = min(last_total_ms, ms_limit)
    np_back = generate_samecolor_np(width, height, backcolor)
    img_back = Image.fromarray(np_back)
    img_paths = []
    # create folder overlay_video_imgs if not exist
    if not os.path.exists('../SampleOut/overlay_video_imgs'):
        os.makedirs('../SampleOut/overlay_video_imgs')

    font = ImageFont.truetype('arial.ttf', 20)

    row_indexes_really_deal = []
    num_frames = int(max_total_ms_really / frame_ms_delta)
    index_start = df[df[COL_NAME_LAP] >= lap_start].index[0]
    index_now = index_start
    index_last = df.index[-1]
    for i_frame in range(num_frames):
        print(f'\rgenerate_overlay_video find index: {i_frame / num_frames * 100:.0f}%', end='')
        b_found_this_frame = False
        total_ms = i_frame * frame_ms_delta
        while index_now <= index_last:
            row = df.iloc[index_now]
            if row[COL_NAME_TOTAL_MS] >= total_ms:
                b_found_this_frame = True
                row_indexes_really_deal.append(index_now)
                break
            index_now += 1
        if not b_found_this_frame:
            break
    print(f'\rgenerate_overlay_video find index: 100%')

    print(f'\rgenerate_overlay_video really draw: 0%', end='')
    num_processes = os.cpu_count()
    # split row_indexes_really_deal to num_cpu parts
    row_indexes_really_deal_split = np.array_split(row_indexes_really_deal, num_processes)
    # use multiprocessing to deal with rows_really_deal_split
    pool = Pool(num_processes)
    results = []
    manager = multiprocessing.Manager()
    lock_finished_frames = manager.Lock()
    finished_frames = manager.Value('i', 0)
    for i_part, row_indexes in enumerate(row_indexes_really_deal_split):
        result = pool.apply_async(generate_overlay_video_part,
                                  args=(i_part, img_back, df, row_indexes, font, num_frames, num_processes,
                                        lock_finished_frames, finished_frames))
        results.append(result)
    pool.close()
    pool.join()
    # get img_paths
    for result in results:
        img_paths.extend(result.get())
    print(f'\rgenerate_overlay_video really draw: 100%')

    print(f'\rgenerate_overlay_video create ImageSequenceClip: 0%', end='')
    ans = ImageSequenceClip(
        img_paths,
        fps=fps,
    )
    print(f'\rgenerate_overlay_video create ImageSequenceClip: 100%')
    return ans


def generate_overlay_video_part(_, img_back, df, row_indexes, font, num_frames, num_processes,
                                lock_finished_frames, finished_frames):
    img_paths = []
    img_width, img_height = img_back.size
    len_row_indexes = len(row_indexes)
    prgress_last_report = 0
    i_last_report = 0
    delta_progress_2_report = 0.01 * num_processes
    for i, index in enumerate(row_indexes):
        row = df.iloc[index]

        img = img_back.copy()
        draw = ImageDraw.Draw(img)

        # show lap
        lap = row[COL_NAME_LAP]
        draw_text(draw, f'Lap {lap}', 10 / 1280 * img_width, 6 / 960 * img_height, font)
        # show lap time
        lap_datetime = row[COL_NAME_LAP_DATETIME]
        str_mmssms_laptime = f'{lap_datetime.minute}:{lap_datetime.second:02}.{lap_datetime.microsecond // 1000:03}'
        draw_text(draw, str_mmssms_laptime, 10 / 1280 * img_width, 40 / 960 * img_height, font)

        # save img
        img_path = f'../SampleOut/overlay_video_imgs/{index}.png'
        img.save(img_path)
        img_paths.append(img_path)

        # print progress of this part
        progress = (i + 1) / len_row_indexes
        if progress - prgress_last_report >= delta_progress_2_report:
            with lock_finished_frames:
                finished_frames.value += i - i_last_report
                print(f'\rgenerate_overlay_video really draw: {finished_frames.value / num_frames * 100:.0f}%', end='')
            prgress_last_report = progress
            i_last_report = i
    return img_paths
