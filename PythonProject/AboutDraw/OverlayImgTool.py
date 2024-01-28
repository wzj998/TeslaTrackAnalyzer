import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from AboutDraw.OverlayBaseTool import *
from AboutDraw.OverlayVehicleState import draw_vehicle_state
from Structures.ContinusLapsConsts import *


def draw_overlays_on_img(img: Image, row: pd.Series, power_level_min: int, power_level_max: int,
                         x_ratio: float, y_ratio: float, size_ratio: float,
                         font_normal: ImageFont, font_small: ImageFont,
                         g: float, max_accel_length: float,
                         x_min: float, x_max: float, y_min: float, y_max: float,
                         time_delta: float):
    draw = ImageDraw.Draw(img)

    draw_left_top(draw, font_normal, row, x_ratio, y_ratio, size_ratio, time_delta)
    draw_right_top(draw, row, x_ratio, y_ratio, size_ratio, x_min, x_max, y_min, y_max)
    draw_left_bottom(draw, font_small, row, 140, 740, x_ratio, y_ratio, size_ratio)
    draw_right_bottom(draw, font_normal, power_level_max, power_level_min, row, x_ratio, y_ratio, size_ratio)
    draw_center_bottom(draw, font_normal, g, max_accel_length, row, x_ratio, y_ratio, size_ratio)


def draw_left_top(draw, font, row, x_ratio, y_ratio, _, time_delta: float):
    # show lap
    lap = row[COL_NAME_LAP]
    draw_text(draw, f'Lap {lap}', 20 + 20, 100, font, x_ratio, y_ratio)
    # show lap time
    lap_datetime = row[COL_NAME_LAP_DATETIME]
    str_mmssms_laptime = f'{lap_datetime.minute}:{lap_datetime.second:02}.{lap_datetime.microsecond // 1000:03}'
    draw_text(draw, str_mmssms_laptime, 20 + 20, 100 + 30, font, x_ratio, y_ratio)
    # show time delta
    if time_delta is not None:
        str_mmssms_timedelta = f'{time_delta:03}'
        if time_delta > 0:
            str_mmssms_timedelta = '+' + str_mmssms_timedelta
        draw_text(draw, str_mmssms_timedelta, 20 + 20, 100 + 30 * 2, font, x_ratio, y_ratio)


def draw_right_top(draw, row, x_ratio, y_ratio, size_ratio, x_min, x_max, y_min, y_max):
    if x_max <= x_min:
        raise ValueError(f'x_max <= x_min: {x_max} <= {x_min}')
    if y_max <= y_min:
        raise ValueError(f'y_max <= y_min: {y_max} <= {y_min}')

    # draw red circle by gps pos
    circle_radius, x_m_draw, y_m_draw = get_gps_x_y_2_draw(row, x_ratio, y_ratio, size_ratio, x_min, x_max, y_min,
                                                           y_max)

    draw.ellipse((x_m_draw - circle_radius, y_m_draw - circle_radius,
                  x_m_draw + circle_radius, y_m_draw + circle_radius),
                 fill=(255, 0, 0))


def get_gps_x_y_2_draw(row, x_ratio, y_ratio, size_ratio, x_min, x_max, y_min, y_max):
    x_m = row[COL_NAME_X_M]
    y_m = row[COL_NAME_Y_M]
    width_m = x_max - x_min
    height_m = y_max - y_min
    if width_m <= 0:
        raise ValueError(f'width_m <= 0: {width_m} <= 0')
    if height_m <= 0:
        raise ValueError(f'height_m <= 0: {height_m} <= 0')
    if width_m > height_m:
        graph_width = 250 * x_ratio
        graph_height = graph_width * height_m / width_m
    else:
        graph_height = 250 * y_ratio
        graph_width = graph_height * width_m / height_m
    circle_radius = 5 * size_ratio
    x_origin = 1280 * x_ratio - graph_width - 20 * x_ratio
    y_origin = 20 * y_ratio

    x_ratio = (x_m - x_min) / width_m
    y_ratio = (y_m - y_min) / height_m
    x_m_draw = x_ratio * graph_width + x_origin
    y_m_draw = graph_height - y_ratio * graph_height + y_origin
    return circle_radius, x_m_draw, y_m_draw


def draw_left_bottom(draw, font, row,
                     battery_rect_left, battery_rect_top,
                     x_ratio, y_ratio, size_ratio,
                     battery_rect_width_in=134, battery_rect_height=148):
    draw_vehicle_state(draw, row,
                       battery_rect_left, battery_rect_top, battery_rect_width_in, battery_rect_height,
                       font, x_ratio, y_ratio, size_ratio)


def draw_center_bottom(draw, font, g, max_accel_length, row, x_ratio, y_ratio, size_ratio):
    g_force_big_radius = 40
    # draw g-force circle
    draw_g_force_circle(draw, row[COL_NAME_LONG_ACCEL], row[COL_NAME_LAT_ACCEL], max_accel_length, 1280 / 2, 840,
                        x_ratio, y_ratio, size_ratio, g_force_big_radius)
    accel_length = math.sqrt(row[COL_NAME_LONG_ACCEL] ** 2 + row[COL_NAME_LAT_ACCEL] ** 2)
    # g-force length
    draw_text(draw, f'total: {accel_length / g:.2f} g', 1280 / 2,
              840 - (g_force_big_radius + 14) / y_ratio * size_ratio, font, x_ratio, y_ratio,
              size_ratio,
              90, AnchorHorizontal.CENTER,
              20, AnchorVertical.BOTTOM)
    # x g-force
    draw_text(draw, f'x: {row[COL_NAME_LAT_ACCEL] / g:.2f} g',
              1280 / 2 + (g_force_big_radius + 20) / x_ratio * size_ratio, 840, font,
              x_ratio, y_ratio,
              size_ratio,
              None, AnchorHorizontal.LEFT,
              20, AnchorVertical.CENTER)
    # y g-force
    draw_text(draw, f'y: {row[COL_NAME_LONG_ACCEL] / g:.2f} g', 1280 / 2,
              840 + (g_force_big_radius + 14) / y_ratio * size_ratio, font,
              x_ratio, y_ratio,
              size_ratio,
              50, AnchorHorizontal.CENTER)
    # show speed
    speed = row[COL_NAME_SPEED_KMH]
    draw_text(draw, f'{speed:.0f} km/h', 1280 / 2, 840 + (g_force_big_radius + 14 + 20 + 10) / y_ratio * size_ratio,
              font,
              x_ratio, y_ratio,
              size_ratio,
              50, AnchorHorizontal.CENTER)


def draw_right_bottom(draw, font, power_level_max, power_level_min, row, x_ratio, y_ratio, size_ratio):
    # draw power level
    power_level = row[COL_NAME_POWER_LEVEL]
    draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                1150, 860, (0, 255, 0), x_ratio, y_ratio)
    draw_text(draw, f'{power_level:.1f} kw', 1150, 860 + 25, font, x_ratio, y_ratio,
              size_ratio,
              70, AnchorHorizontal.CENTER)
    top_progress_rect = 760
    # draw throttle rect
    draw_progress_rect(draw, row[COL_NAME_THROTTLE] / 100, 1220, top_progress_rect, (0, 255, 0), x_ratio, y_ratio)
    # draw brake rect
    draw_progress_rect(draw, row[COL_NAME_BRAKE] / 100, 1200, top_progress_rect, (255, 0, 0), x_ratio, y_ratio)
    # draw steering wheel
    draw_steering_wheel(draw, row[COL_NAME_STEER_ANGLE], 1150, top_progress_rect + 40, x_ratio, y_ratio, size_ratio)
