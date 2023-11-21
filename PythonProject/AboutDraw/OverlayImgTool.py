import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from Structures.ContinusLapsConsts import *


def draw_text(draw, text, x, y, font, text_color=(255, 255, 255)):
    draw.text((x, y), text, font=font, fill=text_color, stroke_width=2, stroke_fill=(0, 0, 0))


# 水平方向，0会被一条竖线标出来
def draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                left, top, fill_color,
                x_ratio, y_ratio,
                width=140, height=8, center_height=16):
    if power_level_max <= power_level_min:
        return

    rect_back = (left,
                 top,
                 left + width,
                 top + height)

    zero_ratio = (0 - power_level_min) / (power_level_max - power_level_min)
    x_zero = rect_back[0] + width * zero_ratio

    # draw inner
    power_level_ratio = (power_level - power_level_min) / (power_level_max - power_level_min)
    power_level_x = rect_back[0] + width * power_level_ratio
    # draw from x_zero to power_level_x
    rect_inner = None
    if power_level_x * x_ratio - x_zero * x_ratio >= 1:
        rect_inner = (x_zero * x_ratio, rect_back[1] * y_ratio, power_level_x * x_ratio, rect_back[3] * y_ratio)
    elif power_level_x * x_ratio - x_zero * x_ratio <= -1:
        rect_inner = (power_level_x * x_ratio, rect_back[1] * y_ratio, x_zero * x_ratio, rect_back[3] * y_ratio)
    if rect_inner is not None:
        draw.rectangle(rect_inner, fill=fill_color)

    # draw zero line
    center_height_offset = (center_height - height) / 2 * y_ratio
    draw.line((x_zero * x_ratio, (rect_back[1] - center_height_offset) * y_ratio,
               x_zero * x_ratio, (rect_back[3] + center_height_offset) * y_ratio),
              fill=(0, 0, 0), width=1)


def draw_overlays_on_img(img: Image, row: pd.Series, power_level_min: int, power_level_max: int,
                         img_width: int, img_height: int, font: ImageFont):
    draw = ImageDraw.Draw(img)

    x_ratio = img_width / 1280
    y_ratio = img_height / 960

    # show lap
    lap = row[COL_NAME_LAP]
    draw_text(draw, f'Lap {lap}', 10 * x_ratio, 6 * y_ratio, font)

    # show lap time
    lap_datetime = row[COL_NAME_LAP_DATETIME]
    str_mmssms_laptime = f'{lap_datetime.minute}:{lap_datetime.second:02}.{lap_datetime.microsecond // 1000:03}'
    draw_text(draw, str_mmssms_laptime, 10 * x_ratio, 40 * y_ratio, font)

    # show speed
    speed = row[COL_NAME_SPEED_KMH]
    draw_text(draw, f'{speed:.0f} km/h', 1140 * x_ratio, 890 * y_ratio, font)

    # draw power level
    power_level = row[COL_NAME_POWER_LEVEL]
    draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                1130, 850, (255, 255, 0), x_ratio, y_ratio)

    top_progress_rect = 760
    # draw throttle rect
    draw_progress_rect(draw, row[COL_NAME_THROTTLE] / 100, 1220, top_progress_rect, (255, 255, 0), x_ratio, y_ratio)
    # draw brake rect
    draw_progress_rect(draw, row[COL_NAME_BRAKE] / 100, 1200, top_progress_rect, (255, 0, 0), x_ratio, y_ratio)


def draw_progress_rect(draw,
                       ratio, rect_left_x, rect_top_y, fill_color,
                       x_ratio, y_ratio,
                       rect_width=12, rect_height_max=80,
                       border_color=(128, 128, 128), border_width=2):
    rect_back = (rect_left_x,
                 rect_top_y,
                 rect_left_x + rect_width,
                 rect_top_y + rect_height_max)

    # draw inner
    throttle_inner_rect_y = rect_top_y + rect_height_max - rect_height_max * ratio
    if (rect_back[3] - throttle_inner_rect_y) * y_ratio >= 1:
        rect_inner = (rect_back[0] * x_ratio, throttle_inner_rect_y * y_ratio,
                      rect_back[2] * x_ratio, rect_back[3] * y_ratio)
        draw.rectangle(rect_inner, fill=fill_color)

    # draw border
    rect_border = (rect_back[0] * x_ratio, rect_back[1] * y_ratio - border_width,
                   rect_back[2] * x_ratio, rect_back[3] * y_ratio)
    draw.rectangle(rect_border, outline=border_color, width=border_width)
