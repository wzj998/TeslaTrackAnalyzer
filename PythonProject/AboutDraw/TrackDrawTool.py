import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

from Structures import ContinusLaps
from Structures.ContinusLapsConsts import *


def draw_on_ax(ax, df_laps_2_draw_copy, cool_laps_set, start_ms, end_ms, timing_line_x_m, timing_line_y_m):
    if start_ms is None:
        start_ms = df_laps_2_draw_copy[COL_NAME_TOTAL_MS].min()
    if end_ms is None:
        end_ms = df_laps_2_draw_copy[COL_NAME_TOTAL_MS].max()

    # draw gps track
    df_cool_laps = df_laps_2_draw_copy[df_laps_2_draw_copy[COL_NAME_LAP].isin(cool_laps_set)]
    df_push_laps = df_laps_2_draw_copy[~df_laps_2_draw_copy[COL_NAME_LAP].isin(cool_laps_set)]
    # only draw gps track in time range
    df_cool_laps = df_cool_laps[
        (df_cool_laps[COL_NAME_TOTAL_MS] >= start_ms) & (df_cool_laps[COL_NAME_TOTAL_MS] <= end_ms)]
    df_push_laps = df_push_laps[
        (df_push_laps[COL_NAME_TOTAL_MS] >= start_ms) & (df_push_laps[COL_NAME_TOTAL_MS] <= end_ms)]
    # clear ax
    ax.cla()
    ax.plot(df_cool_laps[COL_NAME_X_M], df_cool_laps[COL_NAME_Y_M], color='C0', linewidth=1, zorder=10)
    ax.plot(df_push_laps[COL_NAME_X_M], df_push_laps[COL_NAME_Y_M], color='C1', linewidth=1, zorder=11)
    # draw start point, above gps track
    ax.scatter(timing_line_x_m, timing_line_y_m, marker='v', color='C2', linewidth=6, zorder=12)


def update_slider_text(slider):
    # set slider text ms to datetime
    val_datetime = pd.to_datetime(slider.val, unit='ms')
    slider.valtext.set_text(val_datetime.strftime('%M:%S.%f'))


def draw_gps_track_by_laps_cool_laps_set(df_laps_2_draw,
                                         timing_line_x_m, timing_line_y_m,
                                         cool_laps_set=None):
    if cool_laps_set is None:
        cool_laps_set = set()
    print('push_laps_set:', set(df_laps_2_draw[COL_NAME_LAP].unique()) - cool_laps_set)
    print('cool_laps_set:', cool_laps_set)

    fig, ax = plt.subplots()

    draw_on_ax(ax, df_laps_2_draw, cool_laps_set, None, None, timing_line_x_m, timing_line_y_m)
    set_lims_grid(ax, df_laps_2_draw)

    # 创建滚动条
    axcolor = 'lightgoldenrodyellow'
    ax_slider = plt.axes([0.25, 0.01, 0.55, 0.03], facecolor=axcolor)
    min_total_ms_laps_drawed = df_laps_2_draw[COL_NAME_TOTAL_MS].min()
    max_total_ms_laps_drawed = df_laps_2_draw[COL_NAME_TOTAL_MS].max()
    slider = Slider(ax_slider, 'Time', min_total_ms_laps_drawed, max_total_ms_laps_drawed,
                    valinit=max_total_ms_laps_drawed, valstep=1)
    update_slider_text(slider)

    # 更新图表数据的函数
    slider.on_changed(lambda val: update(slider, ax, df_laps_2_draw,
                                         timing_line_x_m, timing_line_y_m, cool_laps_set))

    return fig, ax, slider


def set_lims_grid(ax, df_laps_2_draw_copy):
    # make x, y axis equal
    x_min = df_laps_2_draw_copy[COL_NAME_X_M].min()
    x_max = df_laps_2_draw_copy[COL_NAME_X_M].max()
    x_center = (x_min + x_max) / 2
    y_min = df_laps_2_draw_copy[COL_NAME_Y_M].min()
    y_max = df_laps_2_draw_copy[COL_NAME_Y_M].max()
    y_center = (y_min + y_max) / 2
    width = (x_max - x_min) * 1.1  # 1.1 is for margin
    height = (y_max - y_min) * 1.1  # 1.1 is for margin
    max_width_height = max(width, height)
    ax.set_xlim(left=x_center - max_width_height / 2, right=x_center + max_width_height / 2)
    ax.set_ylim(bottom=y_center - max_width_height / 2, top=y_center + max_width_height / 2)

    # set grid
    ax.grid()


def draw_gps_track(continus_laps, lap_start, lap_end,
                   b_auto_generate_cool_laps_set, b_contain_first_enter_lap, b_contain_last_back_lap,
                   title='GPS Track'):
    df = continus_laps.df
    df_laps_2_draw = df[(df[COL_NAME_LAP] >= lap_start) & (df[COL_NAME_LAP] <= lap_end)].copy()
    laps_2_draw = df_laps_2_draw[COL_NAME_LAP].unique()
    ContinusLaps.add_x_m_y_m_col(df_laps_2_draw, continus_laps.longtitude_start, continus_laps.latitude_start,
                                 continus_laps.altitude)
    avg_timing_line_x_m, avg_timing_line_y_m = ContinusLaps.get_avg_timing_line_x_y_m(df_laps_2_draw)
    cool_laps_set = None
    if b_auto_generate_cool_laps_set:
        laps_2_kmeans = laps_2_draw.copy()
        if b_contain_first_enter_lap:
            laps_2_kmeans = laps_2_kmeans[1:]
        if b_contain_last_back_lap:
            laps_2_kmeans = laps_2_kmeans[:-1]
        cool_laps_set = ContinusLaps.generate_cool_laps_set(laps_2_kmeans, continus_laps.laptimes)
        if b_contain_first_enter_lap:
            cool_laps_set.add(laps_2_draw[0])
        if b_contain_last_back_lap:
            cool_laps_set.add(laps_2_draw[-1])
    fig, ax, slider = draw_gps_track_by_laps_cool_laps_set(df_laps_2_draw,
                                                           avg_timing_line_x_m, avg_timing_line_y_m,
                                                           cool_laps_set)
    fig.suptitle(title)
    return fig, ax, slider


def update(slider, ax, df_laps_2_draw_copy, timing_line_x_m, timing_line_y_m, cool_laps_set):
    update_slider_text(slider)
    draw_on_ax(ax, df_laps_2_draw_copy, cool_laps_set, None, slider.val, timing_line_x_m, timing_line_y_m)
    set_lims_grid(ax, df_laps_2_draw_copy)
