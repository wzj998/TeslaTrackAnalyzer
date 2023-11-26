import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from AboutDraw.OverlayBaseTool import *
from AboutDraw.OverlayVehicleState import draw_vehicle_state
from Structures.ContinusLapsConsts import *


def draw_overlays_on_img(img: Image, row: pd.Series, power_level_min: int, power_level_max: int,
                         x_ratio: float, y_ratio: float, size_ratio: float,
                         font_normal: ImageFont, font_small: ImageFont,
                         g: float, max_accel_length: float):
    draw = ImageDraw.Draw(img)

    draw_left_top(draw, font_normal, row, x_ratio, y_ratio, size_ratio)
    draw_left_bottom(draw, font_small, row, 140, 740, x_ratio, y_ratio)
    draw_right_bottom(draw, font_normal, power_level_max, power_level_min, row, x_ratio, y_ratio, size_ratio)
    draw_center_bottom(draw, font_normal, g, max_accel_length, row, x_ratio, y_ratio, size_ratio)


def draw_left_top(draw, font, row, x_ratio, y_ratio, _):
    # show lap
    lap = row[COL_NAME_LAP]
    draw_text(draw, f'Lap {lap}', 20, 14, font, x_ratio, y_ratio)
    # show lap time
    lap_datetime = row[COL_NAME_LAP_DATETIME]
    str_mmssms_laptime = f'{lap_datetime.minute}:{lap_datetime.second:02}.{lap_datetime.microsecond // 1000:03}'
    draw_text(draw, str_mmssms_laptime, 20, 14 + 30, font, x_ratio, y_ratio)


def draw_left_bottom(draw, font, row,
                     battery_rect_left, battery_rect_top,
                     x_ratio, y_ratio, battery_rect_width_in=134, battery_rect_height=148):
    draw_vehicle_state(draw, row,
                       battery_rect_left, battery_rect_top, battery_rect_width_in, battery_rect_height,
                       font, x_ratio, y_ratio)


def draw_center_bottom(draw, font, g, max_accel_length, row, x_ratio, y_ratio, size_ratio):
    g_force_big_radius = 40
    # draw g-force circle
    draw_g_force_circle(draw, row[COL_NAME_LONG_ACCEL], row[COL_NAME_LAT_ACCEL], max_accel_length, 1280 / 2, 840,
                        x_ratio, y_ratio, size_ratio, g_force_big_radius)
    accel_length = math.sqrt(row[COL_NAME_LONG_ACCEL] ** 2 + row[COL_NAME_LAT_ACCEL] ** 2)
    draw_text(draw, f'{accel_length / g:.2f} g', 1280 / 2, 840 - g_force_big_radius - 12, font, x_ratio, y_ratio,
              50 * size_ratio, AnchorHorizontal.CENTER,
              20 * size_ratio, AnchorVertical.BOTTOM)
    # show speed
    speed = row[COL_NAME_SPEED_KMH]
    draw_text(draw, f'{speed:.0f} km/h', 1280 / 2, 840 + g_force_big_radius + 12, font, x_ratio, y_ratio,
              50 * size_ratio, AnchorHorizontal.CENTER)


def draw_right_bottom(draw, font, power_level_max, power_level_min, row, x_ratio, y_ratio, size_ratio):
    # draw power level
    power_level = row[COL_NAME_POWER_LEVEL]
    draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                1170, 860, (0, 255, 0), x_ratio, y_ratio)
    draw_text(draw, f'{power_level:.1f} kw', 1170, 860 + 25, font, x_ratio, y_ratio,
              70 * size_ratio, AnchorHorizontal.CENTER)
    top_progress_rect = 760
    # draw throttle rect
    draw_progress_rect(draw, row[COL_NAME_THROTTLE] / 100, 1240, top_progress_rect, (0, 255, 0), x_ratio, y_ratio)
    # draw brake rect
    draw_progress_rect(draw, row[COL_NAME_BRAKE] / 100, 1220, top_progress_rect, (255, 0, 0), x_ratio, y_ratio)
    # draw steering wheel
    draw_steering_wheel(draw, row[COL_NAME_STEER_ANGLE], 1170, top_progress_rect + 40, x_ratio, y_ratio, size_ratio)
