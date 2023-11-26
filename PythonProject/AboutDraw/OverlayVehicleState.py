from AboutDraw.OverlayBaseTool import draw_text, AnchorHorizontal, AnchorVertical
from Structures.ContinusLapsConsts import *


def draw_vehicle_state(draw, row,
                       battery_rect_left, battery_rect_top, battery_rect_width_in, battery_rect_height,
                       font, x_ratio, y_ratio):
    # battery rect width height ratio won't change
    battery_rect_width = battery_rect_width_in * y_ratio / x_ratio
    battery_rect = (battery_rect_left,
                    battery_rect_top,
                    battery_rect_left + battery_rect_width,
                    battery_rect_top + battery_rect_height)

    wheel_rect_width = 20
    wheel_rect_height = 40

    wheel_offset_x = -12
    wheel_offset_y = -2

    left_top_wheel_rect_left = battery_rect[0] + wheel_offset_x - wheel_rect_width
    left_top_wheel_rect_top = battery_rect[1] + wheel_offset_y - wheel_rect_height
    right_top_wheel_rect_left = battery_rect[2] - wheel_offset_x
    right_top_wheel_rect_top = battery_rect[1] + wheel_offset_y - wheel_rect_height
    left_bottom_wheel_rect_left = battery_rect[0] + wheel_offset_x - wheel_rect_width
    left_bottom_wheel_rect_top = battery_rect[3] - wheel_offset_y
    right_bottom_wheel_rect_left = battery_rect[2] - wheel_offset_x
    right_bottom_wheel_rect_top = battery_rect[3] - wheel_offset_y
    draw_constant_vehicle(battery_rect, draw, x_ratio, y_ratio,
                          wheel_rect_width, wheel_rect_height,
                          left_top_wheel_rect_left, left_top_wheel_rect_top,
                          right_top_wheel_rect_left, right_top_wheel_rect_top,
                          left_bottom_wheel_rect_left, left_bottom_wheel_rect_top,
                          right_bottom_wheel_rect_left, right_bottom_wheel_rect_top)

    # battery temp
    battery_temp = row[COL_NAME_BATTERY_TEMP]
    battery_rect_center_x = battery_rect_left + battery_rect_width / 2
    battery_rect_center_y = battery_rect_top + battery_rect_height / 2
    draw_text(draw, f'battery temp\n{battery_temp:.3f}', battery_rect_center_x,
              battery_rect_center_y - 6, font,
              x_ratio, y_ratio,
              80, AnchorHorizontal.CENTER,
              40, AnchorVertical.BOTTOM)
    # battery percent
    battery_percent = row[COL_NAME_STATE_OF_CHARGE]
    draw_text(draw, f'battery remain\n{battery_percent:.1f}%', battery_rect_center_x,
              battery_rect_center_y + 6, font,
              x_ratio, y_ratio,
              80, AnchorHorizontal.CENTER)

    draw_around_left_top_wheel(draw, font, row,
                               left_top_wheel_rect_left, left_top_wheel_rect_top,
                               wheel_rect_height, wheel_rect_width,
                               x_ratio, y_ratio)

    draw_around_right_top_wheel(draw, font, row,
                                right_top_wheel_rect_left, right_top_wheel_rect_top,
                                wheel_rect_height, wheel_rect_width,
                                x_ratio, y_ratio)

    draw_around_left_bottom_wheel(draw, font, row,
                                  left_bottom_wheel_rect_left, left_bottom_wheel_rect_top,
                                  wheel_rect_height, wheel_rect_width,
                                  x_ratio, y_ratio)

    draw_around_right_bottom_wheel(draw, font, row,
                                   right_bottom_wheel_rect_left, right_bottom_wheel_rect_top,
                                   wheel_rect_height, wheel_rect_width,
                                   x_ratio, y_ratio)


def draw_constant_vehicle(battery_rect, draw, x_ratio, y_ratio,
                          wheel_rect_width, wheel_rect_height,
                          left_top_wheel_rect_left, left_top_wheel_rect_top,
                          right_top_wheel_rect_left, right_top_wheel_rect_top,
                          left_bottom_wheel_rect_left, left_bottom_wheel_rect_top,
                          right_bottom_wheel_rect_left, right_bottom_wheel_rect_top):
    # draw rect respresent battery
    draw.rectangle((battery_rect[0] * x_ratio,
                    battery_rect[1] * y_ratio,
                    battery_rect[2] * x_ratio,
                    battery_rect[3] * y_ratio),
                   outline=(255, 255, 255), width=3)

    # draw left top wheel
    draw.rectangle((left_top_wheel_rect_left * x_ratio,
                    left_top_wheel_rect_top * y_ratio,
                    (left_top_wheel_rect_left + wheel_rect_width) * x_ratio,
                    (left_top_wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)

    # draw right top wheel
    draw.rectangle((right_top_wheel_rect_left * x_ratio,
                    right_top_wheel_rect_top * y_ratio,
                    (right_top_wheel_rect_left + wheel_rect_width) * x_ratio,
                    (right_top_wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)

    # draw left bottom wheel
    draw.rectangle((left_bottom_wheel_rect_left * x_ratio,
                    left_bottom_wheel_rect_top * y_ratio,
                    (left_bottom_wheel_rect_left + wheel_rect_width) * x_ratio,
                    (left_bottom_wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)

    # draw right bottom wheel
    draw.rectangle((right_bottom_wheel_rect_left * x_ratio,
                    right_bottom_wheel_rect_top * y_ratio,
                    (right_bottom_wheel_rect_left + wheel_rect_width) * x_ratio,
                    (right_bottom_wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)


def draw_around_left_top_wheel(draw, font, row,
                               wheel_rect_left, wheel_rect_top, wheel_rect_height, wheel_rect_width,
                               x_ratio, y_ratio,
                               margin_x=6, margin_y=4,
                               text_height_one_line=16, text_height_two_line=30,
                               text_width_small=44):
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # left top tire pressure
    draw_text(draw, f'{row[COL_NAME_TIRE_PRESSURE_FRONT_LEFT]:.2f} bar',
              wheel_rect_left - margin_x, wheel_rect_y_center - margin_y,
              font, x_ratio, y_ratio,
              text_width_small, AnchorHorizontal.RIGHT,
              text_height_one_line, AnchorVertical.BOTTOM)
    # left top tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_FRONT_LEFT]:.2f}',
              wheel_rect_left - margin_x, wheel_rect_y_center + margin_y,
              font, x_ratio, y_ratio,
              text_width_small, AnchorHorizontal.RIGHT)
    # left top brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_FRONT_LEFT]:.2f}',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center,
              font, x_ratio, y_ratio,
              None, AnchorHorizontal.LEFT,
              text_height_two_line, AnchorVertical.CENTER)


def draw_around_right_top_wheel(draw, font, row,
                                wheel_rect_left, wheel_rect_top, wheel_rect_height, wheel_rect_width,
                                x_ratio, y_ratio,
                                margin_x=6, margin_y=4,
                                text_height_one_line=16, text_height_two_line=30,
                                text_width_big=60):
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # right top tire pressure
    draw_text(draw, f'{row[COL_NAME_TIRE_PRESSURE_FRONT_RIGHT]:.2f} bar',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center - margin_y,
              font, x_ratio, y_ratio,
              None, AnchorHorizontal.LEFT,
              text_height_one_line, AnchorVertical.BOTTOM)
    # right top tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_FRONT_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center + margin_y,
              font, x_ratio, y_ratio)
    # right top brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_FRONT_RIGHT]:.2f}',
              wheel_rect_left - margin_x, wheel_rect_y_center,
              font, x_ratio, y_ratio,
              text_width_big, AnchorHorizontal.RIGHT,
              text_height_two_line, AnchorVertical.CENTER)


def draw_around_left_bottom_wheel(draw, font, row,
                                  wheel_rect_left, wheel_rect_top, wheel_rect_height, wheel_rect_width,
                                  x_ratio, y_ratio,
                                  margin_x=6, margin_y=4,
                                  text_height_one_line=16, text_height_two_line=30,
                                  text_width_small=44):
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # left bottom tire pressure
    draw_text(draw, f'{row[COL_NAME_TIRE_PRESSURE_REAR_LEFT]:.2f} bar',
              wheel_rect_left - margin_x, wheel_rect_y_center - margin_y,
              font, x_ratio, y_ratio,
              text_width_small, AnchorHorizontal.RIGHT,
              text_height_one_line, AnchorVertical.BOTTOM)
    # left bottom tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_REAR_LEFT]:.2f}',
              wheel_rect_left - margin_x, wheel_rect_y_center + margin_y,
              font, x_ratio, y_ratio,
              text_width_small, AnchorHorizontal.RIGHT)
    # left bottom brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_REAR_LEFT]:.2f}',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center,
              font, x_ratio, y_ratio,
              None, AnchorHorizontal.LEFT,
              text_height_two_line, AnchorVertical.CENTER)


def draw_around_right_bottom_wheel(draw, font, row,
                                   wheel_rect_left, wheel_rect_top, wheel_rect_height, wheel_rect_width,
                                   x_ratio, y_ratio,
                                   margin_x=6, margin_y=4,
                                   text_height_one_line=16, text_height_two_line=30,
                                   text_width_big=60):
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # right bottom tire pressure
    draw_text(draw, f'{row[COL_NAME_TIRE_PRESSURE_REAR_RIGHT]:.2f} bar',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center - margin_y,
              font, x_ratio, y_ratio,
              None, AnchorHorizontal.LEFT,
              text_height_one_line, AnchorVertical.BOTTOM)
    # right bottom tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_REAR_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + margin_x, wheel_rect_y_center + margin_y,
              font, x_ratio, y_ratio)
    # right bottom brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_REAR_RIGHT]:.2f}',
              wheel_rect_left - margin_x, wheel_rect_y_center,
              font, x_ratio, y_ratio,
              text_width_big, AnchorHorizontal.RIGHT,
              text_height_two_line, AnchorVertical.CENTER)
