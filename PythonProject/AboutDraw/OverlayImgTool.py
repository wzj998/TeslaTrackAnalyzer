import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from AboutDraw.OverlayBaseTool import *
from Structures.ContinusLapsConsts import *


def draw_overlays_on_img(img: Image, row: pd.Series, power_level_min: int, power_level_max: int,
                         img_width: int, img_height: int, font: ImageFont):
    draw = ImageDraw.Draw(img)

    x_ratio = img_width / 1280
    y_ratio = img_height / 960

    # show lap
    lap = row[COL_NAME_LAP]
    draw_text(draw, f'Lap {lap}', 10, 6, font, x_ratio, y_ratio)

    # show lap time
    lap_datetime = row[COL_NAME_LAP_DATETIME]
    str_mmssms_laptime = f'{lap_datetime.minute}:{lap_datetime.second:02}.{lap_datetime.microsecond // 1000:03}'
    draw_text(draw, str_mmssms_laptime, 10, 40, font, x_ratio, y_ratio)

    # draw power level
    power_level = row[COL_NAME_POWER_LEVEL]
    draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                1170, 860, (255, 255, 0), x_ratio, y_ratio)
    draw_text(draw, f'{power_level:.1f} kw', 1170 - 15, 860 + 20, font, x_ratio, y_ratio)
    top_progress_rect = 760
    # draw throttle rect
    draw_progress_rect(draw, row[COL_NAME_THROTTLE] / 100, 1240, top_progress_rect, (255, 255, 0), x_ratio, y_ratio)
    # draw brake rect
    draw_progress_rect(draw, row[COL_NAME_BRAKE] / 100, 1220, top_progress_rect, (255, 0, 0), x_ratio, y_ratio)
    # draw steering wheel
    draw_steering_wheel(draw, row[COL_NAME_STEER_ANGLE], 1170, top_progress_rect + 40, x_ratio, y_ratio)

    # draw g-force circle
    draw_g_force_circle(draw, row[COL_NAME_LONG_ACCEL], row[COL_NAME_LAT_ACCEL], 1280 / 2, 840,
                        x_ratio, y_ratio)
    # show speed
    speed = row[COL_NAME_SPEED_KMH]
    draw_text(draw, f'{speed:.0f} km/h', 1280 / 2 - 15, 896, font, x_ratio, y_ratio)
