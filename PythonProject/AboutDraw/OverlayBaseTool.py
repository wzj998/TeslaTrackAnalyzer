import math


class AnchorHorizontal:
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class AnchorVertical:
    TOP = 0
    CENTER = 1
    BOTTOM = 2


def draw_text(draw, text, x, y, font, x_ratio, y_ratio, size_ratio=None,
              estimate_width=None, anchor_left_center_right: AnchorHorizontal = AnchorHorizontal.LEFT,
              estimate_height=None, anchor_top_center_bottom: AnchorVertical = AnchorVertical.TOP,
              text_color=(255, 255, 255)):
    x_really = x * x_ratio
    if anchor_left_center_right == AnchorHorizontal.CENTER:
        if estimate_width is None:
            raise ValueError('estimate_width is None')
        if size_ratio is None:
            raise ValueError('size_ratio is None')
        x_really -= estimate_width / 2 * size_ratio
    elif anchor_left_center_right == AnchorHorizontal.RIGHT:
        if estimate_width is None:
            raise ValueError('estimate_width is None')
        if size_ratio is None:
            raise ValueError('size_ratio is None')
        x_really -= estimate_width * size_ratio
    y_really = y * y_ratio
    if anchor_top_center_bottom == AnchorVertical.CENTER:
        if estimate_height is None:
            raise ValueError('estimate_height is None')
        if size_ratio is None:
            raise ValueError('size_ratio is None')
        y_really -= estimate_height / 2 * size_ratio
    elif anchor_top_center_bottom == AnchorVertical.BOTTOM:
        if estimate_height is None:
            raise ValueError('estimate_height is None')
        if size_ratio is None:
            raise ValueError('size_ratio is None')
        y_really -= estimate_height * size_ratio
    draw.text((x_really,
               y_really),
              text, font=font, fill=text_color, stroke_width=2, stroke_fill=(0, 0, 0))


# 水平方向，0会被一条竖线标出来
def draw_zf_bar(draw, power_level, power_level_min, power_level_max,
                x_zero, top, fill_color,
                x_ratio, y_ratio,
                width=120, height=8, center_height=16):
    if power_level_max <= power_level_min:
        return

    zero_ratio = (0 - power_level_min) / (power_level_max - power_level_min)
    left = x_zero - width * zero_ratio
    rect_back = (left,
                 top,
                 left + width,
                 top + height)

    # draw inner
    power_level_ratio = (power_level - power_level_min) / (power_level_max - power_level_min)
    power_level_x = rect_back[0] + width * power_level_ratio
    # draw from x_zero to power_level_x
    rect_inner = None
    if power_level_x * x_ratio - x_zero * x_ratio >= 1:
        rect_inner = (x_zero * x_ratio,
                      rect_back[1] * y_ratio,
                      power_level_x * x_ratio,
                      rect_back[3] * y_ratio)
    elif power_level_x * x_ratio - x_zero * x_ratio <= -1:
        rect_inner = (power_level_x * x_ratio,
                      rect_back[1] * y_ratio,
                      x_zero * x_ratio,
                      rect_back[3] * y_ratio)
    if rect_inner is not None:
        draw.rectangle(rect_inner, fill=fill_color)

    # draw zero line
    center_height_offset = (center_height - height) / 2 * y_ratio
    draw.line((x_zero * x_ratio,
               (rect_back[1] - center_height_offset) * y_ratio,
               x_zero * x_ratio,
               (rect_back[3] + center_height_offset) * y_ratio),
              fill=(0, 0, 0), width=3)


def draw_progress_rect(draw,
                       ratio, rect_left_x, rect_top_y, fill_color,
                       x_ratio, y_ratio,
                       rect_width=12, rect_height_max=80,
                       border_color=(0, 0, 0), border_width=3):
    rect_back = (rect_left_x,
                 rect_top_y,
                 rect_left_x + rect_width,
                 rect_top_y + rect_height_max)

    # draw inner
    throttle_inner_rect_y = rect_top_y + rect_height_max - rect_height_max * ratio
    if (rect_back[3] - throttle_inner_rect_y) * y_ratio >= 1:
        rect_inner = (rect_back[0] * x_ratio,
                      throttle_inner_rect_y * y_ratio,
                      rect_back[2] * x_ratio,
                      rect_back[3] * y_ratio)
        draw.rectangle(rect_inner, fill=fill_color)

    # draw border
    rect_border = (rect_back[0] * x_ratio,
                   rect_back[1] * y_ratio - border_width,
                   rect_back[2] * x_ratio,
                   rect_back[3] * y_ratio)
    draw.rectangle(rect_border, outline=border_color, width=border_width)


def draw_steering_wheel(draw, steer_angle, center_x, center_y, x_ratio, y_ratio, size_ratio,
                        radius=30):
    # draw circle
    # 不会因为画面长宽变化，圆就不是圆了
    draw.ellipse((center_x * x_ratio - radius * size_ratio,
                  center_y * y_ratio - radius * size_ratio,
                  center_x * x_ratio + radius * size_ratio,
                  center_y * y_ratio + radius * size_ratio),
                 outline=(255, 255, 255), width=max(int(5 * size_ratio), 1))

    # draw 3 lines: left, right, down
    angle_left = (steer_angle - 180) / 180 * math.pi
    angle_right = steer_angle / 180 * math.pi
    angle_down = (steer_angle + 90) / 180 * math.pi
    # draw left to right in one line
    # 不会因为画面长宽变化，圆就不是圆了
    draw.line((center_x * x_ratio + radius * size_ratio * math.cos(angle_left),
               center_y * y_ratio + radius * size_ratio * math.sin(angle_left),
               center_x * x_ratio + radius * size_ratio * math.cos(angle_right),
               center_y * y_ratio + radius * size_ratio * math.sin(angle_right)),
              fill=(255, 255, 255), width=max(int(5 * size_ratio), 1))
    draw.line((center_x * x_ratio,
               center_y * y_ratio,
               center_x * x_ratio + radius * size_ratio * math.cos(angle_down),
               center_y * y_ratio + radius * size_ratio * math.sin(angle_down)),
              fill=(255, 255, 255), width=max(int(5 * size_ratio), 1))


def draw_g_force_circle(draw, long_accel, lat_accel, max_accel_length, center_x, center_y, x_ratio, y_ratio, size_ratio,
                        radius, rows_remain=None, sphere_radius=7):
    # draw cross
    # 不会因为画面长宽变化，圆就不是圆了
    length_cross = radius * size_ratio * 1.2
    draw.line((center_x * x_ratio - length_cross,
               center_y * y_ratio,
               center_x * x_ratio + length_cross,
               center_y * y_ratio),
              fill=(255, 255, 255), width=3)
    draw.line((center_x * x_ratio,
               center_y * y_ratio - length_cross,
               center_x * x_ratio,
               center_y * y_ratio + length_cross),
              fill=(255, 255, 255), width=3)

    # draw circle
    # 不会因为画面长宽变化，圆就不是圆了
    draw.ellipse((center_x * x_ratio - radius * size_ratio,
                  center_y * y_ratio - radius * size_ratio,
                  center_x * x_ratio + radius * size_ratio,
                  center_y * y_ratio + radius * size_ratio),
                 outline=(255, 255, 255), width=max(int(5 * size_ratio), 1))

    # draw inner g sphere, max_accel_length对应radius
    # 不会因为画面长宽变化，圆就不是圆了
    # lat_accel是横向加速度，对应x轴，long_accel是纵向加速度，对应y轴
    if not(rows_remain is None or len(rows_remain) <= 1):
        draw_g_force_point_lines(draw, max_accel_length, center_x, center_y, x_ratio, y_ratio, size_ratio, radius, rows_remain)

    draw_g_force_point(draw, lat_accel, long_accel, max_accel_length, center_x, center_y, x_ratio, y_ratio, size_ratio, radius, sphere_radius)        

def draw_g_force_point(draw, lat_accel, long_accel, max_accel_length, center_x, center_y, x_ratio, y_ratio, size_ratio, radius, sphere_radius):
    """在 G 力圆中绘制一个点，表示当前的横向和纵向加速度
    
    Args:
        draw: PIL Draw对象
        lat_accel: 横向加速度
        long_accel: 纵向加速度
        max_accel_length: 最大加速度值
        center_x: 圆心x坐标
        center_y: 圆心y坐标
        x_ratio: x方向缩放比例
        y_ratio: y方向缩放比例
        size_ratio: 大小缩放比例
        radius: G力圆半径
        sphere_radius: G力点半径
    """
    x_offset = lat_accel / max_accel_length * radius * size_ratio
    y_offset = long_accel / max_accel_length * radius * size_ratio
    x_sphere = center_x * x_ratio + x_offset
    y_sphere = center_y * y_ratio + y_offset
    draw.ellipse((x_sphere - sphere_radius * size_ratio,
                y_sphere - sphere_radius * size_ratio,
                x_sphere + sphere_radius * size_ratio,
                y_sphere + sphere_radius * size_ratio),
                fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    
def draw_g_force_point_lines(draw, max_accel_length, center_x, center_y, x_ratio, y_ratio, size_ratio, radius, rows_remain):
    """在 G 力圆中绘制轨迹线，表示历史点之间的轨迹
    
    Args:
        draw: PIL Draw对象
        max_accel_length: 最大加速度值
        center_x: 圆心x坐标
        center_y: 圆心y坐标
        x_ratio: x方向缩放比例
        y_ratio: y方向缩放比例
        size_ratio: 大小缩放比例
        radius: G力圆半径
        rows_remain: 包含历史数据点的列表，每个点包含 [lat_accel, long_accel]
    """
    if not rows_remain or len(rows_remain) < 2:  # 如果没有足够的历史点，直接返回
        return
        
    # 遍历历史点，绘制轨迹线
    for i in range(len(rows_remain) - 1):
        if i >= len(rows_remain) - 1:
            break
        
        row = rows_remain[i]
        next_row = rows_remain[i + 1]
        
        # 计算当前历史点的位置
        lat_accel_current = row[0]
        long_accel_current = row[1]
        x_offset_current = lat_accel_current / max_accel_length * radius * size_ratio
        y_offset_current = long_accel_current / max_accel_length * radius * size_ratio
        x_point_current = center_x * x_ratio + x_offset_current
        y_point_current = center_y * y_ratio + y_offset_current
        
        # 计算下一个历史点的位置
        lat_accel_next = next_row[0]
        long_accel_next = next_row[1]
        x_offset_next = lat_accel_next / max_accel_length * radius * size_ratio
        y_offset_next = long_accel_next / max_accel_length * radius * size_ratio
        x_point_next = center_x * x_ratio + x_offset_next
        y_point_next = center_y * y_ratio + y_offset_next
        
        # 绘制连接线
        draw.line((x_point_current, y_point_current, x_point_next, y_point_next),
                 fill=(255, 255, 255), width=max(int(2 * size_ratio), 1))
    