from AboutDraw.OverlayBaseTool import draw_text
from Structures.ContinusLapsConsts import *


def draw_vehicle_state(draw, row,
                       battery_rect_left, battery_rect_top, battery_rect_width, battery_rect_height,
                       font, x_ratio, y_ratio):
    # draw rect respresent battery
    battery_rect = (battery_rect_left,
                    battery_rect_top,
                    battery_rect_left + battery_rect_width,
                    battery_rect_top + battery_rect_height)
    draw.rectangle((battery_rect[0] * x_ratio,
                    battery_rect[1] * y_ratio,
                    battery_rect[2] * x_ratio,
                    battery_rect[3] * y_ratio),
                   outline=(255, 255, 255), width=3)
    battery_text_x_offset = 22
    # battery temp
    battery_temp = row[COL_NAME_BATTERY_TEMP]
    draw_text(draw, f'battery temp\n{battery_temp:.3f}', battery_rect_left + battery_text_x_offset,
              battery_rect_top + 28, font,
              x_ratio, y_ratio)
    # battery percent
    battery_percent = row[COL_NAME_STATE_OF_CHARGE]
    draw_text(draw, f'battery remain\n{battery_percent:.1f}%', battery_rect_left + battery_text_x_offset,
              battery_rect_top + 70, font,
              x_ratio, y_ratio)

    wheel_rect_width = 20
    wheel_rect_height = 40

    wheel_offset_x = -12
    wheel_offset_y = -2

    text_height = 12
    text_height_2_line = 2 * text_height + 8

    draw_around_left_top_wheel(battery_rect, draw, font, row,
                               text_height, text_height_2_line,
                               wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width,
                               x_ratio, y_ratio)
    draw_around_right_top_wheel(battery_rect, draw, font, row,
                                text_height, text_height_2_line,
                                wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width,
                                x_ratio, y_ratio)
    draw_around_left_bottom_wheel(battery_rect, draw, font, row,
                                  text_height, text_height_2_line,
                                  wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width,
                                  x_ratio, y_ratio)
    draw_around_right_bottom_wheel(battery_rect, draw, font, row,
                                   text_height, text_height_2_line,
                                   wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width,
                                   x_ratio, y_ratio)


def draw_around_left_top_wheel(battery_rect, draw, font, row,
                               text_height, text_height_2_line,
                               wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width, x_ratio, y_ratio):
    tire_pressure_offset_x = -82
    tire_pressure_offset_y = -6 - text_height
    tire_slip_offset_x = -82
    tire_slip_offset_y = 6

    brake_temp_offset_x = 8
    brake_temp_offset_y = -text_height_2_line / 2

    # draw left top wheel
    wheel_rect_left = battery_rect[0] + wheel_offset_x - wheel_rect_width
    wheel_rect_top = battery_rect[1] + wheel_offset_y - wheel_rect_height
    draw.rectangle((wheel_rect_left * x_ratio,
                    wheel_rect_top * y_ratio,
                    (wheel_rect_left + wheel_rect_width) * x_ratio,
                    (wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # left top tire pressure
    draw_text(draw, f'pressure {row[COL_NAME_TIRE_PRESSURE_FRONT_LEFT]:.2f}',
              wheel_rect_left + tire_pressure_offset_x, wheel_rect_y_center + tire_pressure_offset_y,
              font, x_ratio, y_ratio)
    # left top tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_FRONT_LEFT]:.2f}',
              wheel_rect_left + tire_slip_offset_x, wheel_rect_y_center + tire_slip_offset_y,
              font, x_ratio, y_ratio)
    # left top brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_FRONT_LEFT]:.2f}',
              wheel_rect_left + wheel_rect_width + brake_temp_offset_x, wheel_rect_y_center + brake_temp_offset_y,
              font, x_ratio, y_ratio)


def draw_around_right_top_wheel(battery_rect, draw, font, row,
                                text_height, text_height_2_line,
                                wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width, x_ratio, y_ratio):
    tire_pressure_offset_x = 8
    tire_pressure_offset_y = -6 - text_height
    tire_slip_offset_x = 8
    tire_slip_offset_y = 6

    brake_temp_offset_x = -66
    brake_temp_offset_y = -text_height_2_line / 2

    # draw right top wheel
    wheel_rect_left = battery_rect[2] - wheel_offset_x
    wheel_rect_top = battery_rect[1] + wheel_offset_y - wheel_rect_height
    draw.rectangle((wheel_rect_left * x_ratio,
                    wheel_rect_top * y_ratio,
                    (wheel_rect_left + wheel_rect_width) * x_ratio,
                    (wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # right top tire pressure
    draw_text(draw, f'pressure {row[COL_NAME_TIRE_PRESSURE_FRONT_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + tire_pressure_offset_x, wheel_rect_y_center + tire_pressure_offset_y,
              font, x_ratio, y_ratio)
    # right top tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_FRONT_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + tire_slip_offset_x, wheel_rect_y_center + tire_slip_offset_y,
              font, x_ratio, y_ratio)
    # right top brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_FRONT_RIGHT]:.2f}',
              wheel_rect_left + brake_temp_offset_x, wheel_rect_y_center + brake_temp_offset_y,
              font, x_ratio, y_ratio)


def draw_around_left_bottom_wheel(battery_rect, draw, font, row,
                                  text_height, text_height_2_line,
                                  wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width, x_ratio,
                                  y_ratio):
    tire_pressure_offset_x = -82
    tire_pressure_offset_y = -6 - text_height
    tire_slip_offset_x = -82
    tire_slip_offset_y = 6

    brake_temp_offset_x = 8
    brake_temp_offset_y = -text_height_2_line / 2

    # draw left bottom wheel
    wheel_rect_left = battery_rect[0] + wheel_offset_x - wheel_rect_width
    wheel_rect_top = battery_rect[3] - wheel_offset_y
    draw.rectangle((wheel_rect_left * x_ratio,
                    wheel_rect_top * y_ratio,
                    (wheel_rect_left + wheel_rect_width) * x_ratio,
                    (wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # left bottom tire pressure
    draw_text(draw, f'pressure {row[COL_NAME_TIRE_PRESSURE_REAR_LEFT]:.2f}',
              wheel_rect_left + tire_pressure_offset_x, wheel_rect_y_center + tire_pressure_offset_y,
              font, x_ratio, y_ratio)
    # left bottom tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_REAR_LEFT]:.2f}',
              wheel_rect_left + tire_slip_offset_x, wheel_rect_y_center + tire_slip_offset_y,
              font, x_ratio, y_ratio)
    # left bottom brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_REAR_LEFT]:.2f}',
              wheel_rect_left + wheel_rect_width + brake_temp_offset_x, wheel_rect_y_center + brake_temp_offset_y,
              font, x_ratio, y_ratio)


def draw_around_right_bottom_wheel(battery_rect, draw, font, row,
                                   text_height, text_height_2_line,
                                   wheel_offset_x, wheel_offset_y, wheel_rect_height, wheel_rect_width, x_ratio,
                                   y_ratio):
    tire_pressure_offset_x = 8
    tire_pressure_offset_y = -6 - text_height
    tire_slip_offset_x = 8
    tire_slip_offset_y = 6

    brake_temp_offset_x = -66
    brake_temp_offset_y = -text_height_2_line / 2

    # draw right bottom wheel
    wheel_rect_left = battery_rect[2] - wheel_offset_x
    wheel_rect_top = battery_rect[3] - wheel_offset_y
    draw.rectangle((wheel_rect_left * x_ratio,
                    wheel_rect_top * y_ratio,
                    (wheel_rect_left + wheel_rect_width) * x_ratio,
                    (wheel_rect_top + wheel_rect_height) * y_ratio),
                   outline=(255, 255, 255), width=3)
    wheel_rect_y_center = wheel_rect_top + wheel_rect_height / 2
    # right bottom tire pressure
    draw_text(draw, f'pressure {row[COL_NAME_TIRE_PRESSURE_REAR_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + tire_pressure_offset_x, wheel_rect_y_center + tire_pressure_offset_y,
              font, x_ratio, y_ratio)
    # right bottom tire slip
    draw_text(draw, f'slip {row[COL_NAME_TIRE_SLIP_REAR_RIGHT]:.2f}',
              wheel_rect_left + wheel_rect_width + tire_slip_offset_x, wheel_rect_y_center + tire_slip_offset_y,
              font, x_ratio, y_ratio)
    # right bottom brake temp
    draw_text(draw, f'brake temp\n{row[COL_NAME_BRAKE_TEMP_REAR_RIGHT]:.2f}',
              wheel_rect_left + brake_temp_offset_x, wheel_rect_y_center + brake_temp_offset_y,
              font, x_ratio, y_ratio)