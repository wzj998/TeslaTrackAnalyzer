import multiprocessing
from multiprocessing import Pool

import matplotlib.dates as mdates
from matplotlib import pyplot as plt

import ContinusLaps
import Lap
from ContinusLapsConsts import *
from CustomCursor import CustomCursor
from InterpolateTool import interpolate_x_m_y_m
from MyMath import get_dist_squared, get_dist


# use total time as x-axis
def draw_x_total_time_curves(df, lap_start, lap_end, cols, title='Total Time Curves'):
    # 每列只有一条曲线
    fig, axs = plt.subplots(len(cols), 1, sharex='all', figsize=(12, 8))

    df_laps_2_draw = df[(df[COL_NAME_LAP] >= lap_start) & (df[COL_NAME_LAP] <= lap_end)]

    x_min = df_laps_2_draw[COL_NAME_TOTAL_DATETIME].min()
    x_max = df_laps_2_draw[COL_NAME_TOTAL_DATETIME].max()

    for i in range(len(cols)):
        # different colors
        axs[i].plot(df_laps_2_draw[COL_NAME_TOTAL_DATETIME], df_laps_2_draw[cols[i]], label=cols[i],
                    color='C' + str(i))

    for ax in axs:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S.%f'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=(x_max - x_min).seconds // 5))
        ax.set_xlim(left=x_min, right=x_max)
        ax.legend()
        ax.grid()

    fig.suptitle(title)

    # cc needs to be returned to avoid being garbage collected
    return fig, axs, quick_new_and_connect_cursor(fig, axs)


# use lap time as x-axis
def draw_x_lap_time_curves_same_continus_laps(df, laps_2_draw, cols, title='Lap Time Curves'):
    # extract data for laps to draw
    df_laps_2_draw = df[df[COL_NAME_LAP].isin(laps_2_draw)]

    fig, axs = plt.subplots(len(cols), 1, sharex='all', figsize=(12, 8))

    dict_df_laps_2_draw = {}
    for lap in laps_2_draw:
        dict_df_laps_2_draw[lap] = df_laps_2_draw[df_laps_2_draw[COL_NAME_LAP] == lap]

    draw_ax_lap_time(axs, laps_2_draw, dict_df_laps_2_draw, cols)

    plt.xlabel('Time (mm:ss.ms)')
    for ax in axs:
        ax.grid()

    fig.suptitle(title)

    # cc needs to be returned to avoid being garbage collected
    return fig, axs, quick_new_and_connect_cursor(fig, axs)


def draw_ax_lap_time(axs, laps_2_draw, dict_df_laps_2_draw, cols, peroid_index=-1):
    x_col_name_2_use = COL_NAME_LAP_DATETIME
    x_min = None
    x_max = None
    for lap in laps_2_draw:
        df_lap = dict_df_laps_2_draw[lap]
        str_label = get_str_label_start(lap, peroid_index)
        for i in range(len(cols)):
            axs[i].plot(df_lap[x_col_name_2_use], df_lap[cols[i]], label=str_label + ' ' + cols[i])

        x_max, x_min = update_x_min_y_min(df_lap, x_col_name_2_use, x_max, x_min)

    for ax in axs:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S.%f'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=(x_max - x_min).seconds // 5))
        ax.set_xlim(left=x_min, right=x_max)
        ax.legend()


def get_str_label_start(lap, peroid_index):
    str_label = 'Lap' + str(lap)
    if peroid_index != -1:
        str_label = 'Period' + str(peroid_index) + ' ' + str_label
    return str_label


def draw_x_lap_checkpoint_dist_curves_same_continus_laps(continus_laps, laps_2_draw, cols,
                                                         title='Lap Checkpoint Dist Curves'):
    laps = []
    for i_lap in laps_2_draw:
        lap = Lap.Lap(continus_laps, 0, i_lap)
        ContinusLaps.add_x_m_y_m_col(lap.df_lap, continus_laps.longtitude_start, continus_laps.latitude_start,
                                     continus_laps.altitude)
        laps.append(lap)

    # use first lap in laps_2_draw to generate checkpoints
    checkpoints_lap = laps[0]
    # we asume that in checkpoints_lap, the car is always moving by correct direction in the track,
    # has no reverse or stop, and the gps data is accurate enough
    df_checkpoints_lap = checkpoints_lap.df_lap
    if len(df_checkpoints_lap) <= 2:
        raise Exception('len(df_checkpoints_lap) <= 2 in draw_x_lap_checkpoint_dist_curves_same_continus_laps')
    interpolate_x_m_y_m(df_checkpoints_lap)
    # print(df_checkpoints_lap.to_string())
    # last and lastlast x_m and y_m should be different
    if df_checkpoints_lap.iloc[len(df_checkpoints_lap) - 1][COL_NAME_X_M] == \
            df_checkpoints_lap.iloc[len(df_checkpoints_lap) - 2][COL_NAME_X_M] and \
            df_checkpoints_lap.iloc[len(df_checkpoints_lap) - 1][COL_NAME_Y_M] == \
            df_checkpoints_lap.iloc[len(df_checkpoints_lap) - 2][COL_NAME_Y_M]:
        raise Exception('df_checkpoints_lap last and last - 1 are the same in '
                        'draw_x_lap_checkpoint_dist_curves_same_continus_laps')
    b_laps_2_draw_timing_line_same = [True] * len(laps)

    fig, axs = plt.subplots(len(cols), 1, sharex='all', figsize=(12, 8))
    draw_ax_lap_checkpoint_dist(axs, df_checkpoints_lap,
                                laps, b_laps_2_draw_timing_line_same, cols)
    plt.xlabel('Distance (m)')
    for ax in axs:
        ax.grid()
    fig.suptitle(title)

    # cc needs to be returned to avoid being garbage collected
    return fig, axs, quick_new_and_connect_cursor(fig, axs)


def generate_dist_from_start_by_checkpoint_index(df_checkpoints_lap) -> list:
    if len(df_checkpoints_lap) <= 0:
        raise Exception('df_checkpoints_lap is empty in generate_dist_from_start_by_checkpoint_index')
    dist_from_start_by_checkpoint_index = [0] * len(df_checkpoints_lap)
    sum_dist = 0
    for i in range(1, len(df_checkpoints_lap)):
        row = df_checkpoints_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        row_last = df_checkpoints_lap.iloc[i - 1]
        x_m_last = row_last[COL_NAME_X_M]
        y_m_last = row_last[COL_NAME_Y_M]
        sum_dist += get_dist(x_m, y_m, x_m_last, y_m_last)
        dist_from_start_by_checkpoint_index[i] = sum_dist
    return dist_from_start_by_checkpoint_index


def __add_col_dist_from_start(df_lap, df_checkpoints_lap, dist_from_start_by_checkpoint_index, col_name,
                              b_same_timing_line):
    if len(df_lap) <= 0:
        raise Exception('df_lap is empty in add_col_dist_from_start')

    # add after COL_NAME_LAP_DATETIME
    df_lap.insert(df_lap.columns.get_loc(COL_NAME_LAP_DATETIME) + 1, col_name, -1)

    dict_checkpoints_reached_by_index = get_dict_checkpoints_reached_by_index(df_checkpoints_lap, df_lap,
                                                                              b_same_timing_line)

    keys_sorted = sorted(dict_checkpoints_reached_by_index.keys())  # 保险起见，先排序
    for i in range(len(keys_sorted)):
        key = keys_sorted[i]
        checkpoints_reached = dict_checkpoints_reached_by_index[key]
        dist_checkpoint_from_start = dist_from_start_by_checkpoint_index[checkpoints_reached[0]]
        df_lap.loc[df_lap.index[key], col_name] = dist_checkpoint_from_start

    # print('list(df_lap[' + col_name + ']):', list(df_lap[col_name]))
    # remove all rows with col_name == -1
    df_lap_remove = df_lap[df_lap[col_name] != -1]

    return df_lap_remove


def get_dict_checkpoints_reached_by_index(df_checkpoints_lap, df_lap, b_same_timing_line):
    if not b_same_timing_line:
        raise Exception('b_same_timing_line=={} in get_dict_checkpoints_reached_by_index not implemented now, '
                        'please wait for next version'.format(b_same_timing_line))
    else:
        return get_dict_checkpoints_reached_by_index_same_timing_line(df_checkpoints_lap, df_lap)


def get_dict_checkpoints_reached_by_index_same_timing_line(df_checkpoints_lap, df_lap):
    index_checkpoint_will_reach = 0
    dict_checkpoints_reached_by_index = {}
    for i in range(0, len(df_lap) - 1):
        row = df_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        while True:
            checkpoint_row = df_checkpoints_lap.iloc[index_checkpoint_will_reach]
            x_m_checkpoint_reached = checkpoint_row[COL_NAME_X_M]
            y_m_checkpoint_reached = checkpoint_row[COL_NAME_Y_M]

            dist_sqr_now_2_checkpoint = get_dist_squared(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached)

            next_row = df_lap.iloc[i + 1]
            x_m_next = next_row[COL_NAME_X_M]
            y_m_next = next_row[COL_NAME_Y_M]
            dist_sqr_next_2_checkpoint = get_dist_squared(x_m_next, y_m_next, x_m_checkpoint_reached,
                                                          y_m_checkpoint_reached)

            if dist_sqr_next_2_checkpoint > dist_sqr_now_2_checkpoint or \
                    index_checkpoint_will_reach == 0 and i == 0:  # 我们认为起点一定到达了第一个检查点
                # checkpoint reached
                if i not in dict_checkpoints_reached_by_index:
                    dict_checkpoints_reached_by_index[i] = [index_checkpoint_will_reach]
                else:
                    dict_checkpoints_reached_by_index[i].append(index_checkpoint_will_reach)
                index_checkpoint_will_reach += 1
                if index_checkpoint_will_reach >= len(df_checkpoints_lap) - 1:
                    break
            else:
                break

    # if df_checkpoints_lap last and last - 1 in same position, 说明预处理工作没做好
    if df_lap.iloc[len(df_lap) - 1][COL_NAME_X_M] == \
            df_lap.iloc[len(df_lap) - 2][COL_NAME_X_M] and \
            df_lap.iloc[len(df_lap) - 1][COL_NAME_Y_M] == \
            df_lap.iloc[len(df_lap) - 2][COL_NAME_Y_M]:
        raise Exception('df_lap last and last - 1 are the same in add_col_dist_from_start')

    # 我们认为终点一定到达了最后一个检查点
    dict_checkpoints_reached_by_index[len(df_lap) - 1] = [len(df_checkpoints_lap) - 1]
    # print('len(df_checkpoints_lap) =', len(df_checkpoints_lap), 'len(df_lap) =', len(df_lap))
    # print('dict_checkpoints_reached_by_index:', dict_checkpoints_reached_by_index)
    return dict_checkpoints_reached_by_index


def draw_ax_lap_checkpoint_dist(axs, df_checkpoints_lap,
                                laps, b_laps_2_draw_timing_line_same, cols):
    # print('---draw_ax_lap_checkpoint_dist---')
    x_col_name_2_use = COL_NAME_DIST_CHECKPOINT_FROM_START
    x_min = None
    x_max = None
    dist_from_start_by_checkpoint_index = generate_dist_from_start_by_checkpoint_index(df_checkpoints_lap)
    # print('dist_from_start_by_checkpoint_index:', dist_from_start_by_checkpoint_index)
    # for lap in laps_2_draw:
    #     dict_df_laps_2_draw[lap] = __add_dist_and_time_delta_points(df_checkpoints_lap, dict_df_laps_2_draw[lap],
    #                                                                 dist_from_start_by_checkpoint_index)
    #     print('lap:', lap, 'finished')
    # use multiprocess to speed up
    num_process = min(multiprocessing.cpu_count(), len(laps))
    pool = Pool(num_process)
    # 使用进程池并行处理 lap
    results = [pool.apply_async(__process_lap, args=(
        i_lap, laps[i_lap], df_checkpoints_lap,
        dist_from_start_by_checkpoint_index,
        b_laps_2_draw_timing_line_same[i_lap]))
               for i_lap in range(len(laps))]
    # 等待所有lap处理完成
    for result in results:
        result.get()
    # 关闭进程池
    pool.close()
    pool.join()
    for result in results:
        i_lap, df_lap_new = result.get()
        laps[i_lap].df_lap = df_lap_new
    print("All laps processed.")

    for i_lap in range(len(laps)):
        lap = laps[i_lap]
        df_lap = lap.df_lap
        str_label = get_str_label_start(lap.lap_index, lap.continus_laps_index)
        for i in range(len(cols)):
            axs[i].plot(df_lap[x_col_name_2_use], df_lap[cols[i]], label=str_label + ' ' + cols[i])

        x_max, x_min = update_x_min_y_min(df_lap, x_col_name_2_use, x_max, x_min)

    for ax in axs:
        ax.set_xlim(left=x_min, right=x_max)
        ax.legend()


def __process_lap(i_lap, lap, df_checkpoints_lap, dist_from_start_by_checkpoint_index, b_same_timing_line):
    df_lap_new = __add_dist_and_time_delta_points(df_checkpoints_lap, lap.df_lap, dist_from_start_by_checkpoint_index,
                                                  b_same_timing_line)
    print(get_str_label_start(lap.lap_index, lap.continus_laps_index), 'finished')
    return i_lap, df_lap_new


def __add_dist_and_time_delta_points(df_checkpoints_lap, df_lap, dist_from_start_by_checkpoint_index,
                                     b_same_timing_line):
    interpolate_x_m_y_m(df_lap)
    df_lap = __add_col_dist_from_start(df_lap, df_checkpoints_lap,
                                       dist_from_start_by_checkpoint_index,
                                       COL_NAME_DIST_CHECKPOINT_FROM_START,
                                       b_same_timing_line)
    df_lap = __add_col_time_delta(df_lap, df_checkpoints_lap, dist_from_start_by_checkpoint_index,
                                  COL_NAME_TIME_DELTA)
    return df_lap


def __add_col_time_delta(df_lap, df_checkpoints_lap, dist_from_start_by_checkpoint_index, col_name):
    dict_checkpoint_index_by_dist_from_start = {}
    # 因为这个检查点到起点的距离是直接赋值给别的圈的行的，没有经过运算，所以可以用来作为key
    for i in range(len(dist_from_start_by_checkpoint_index)):
        dict_checkpoint_index_by_dist_from_start[dist_from_start_by_checkpoint_index[i]] = i
    # insert after COL_NAME_LAP_MS
    df_lap.insert(df_lap.columns.get_loc(COL_NAME_LAP_MS) + 1, col_name, -1)
    for i in range(len(df_lap)):
        # find same COL_NAME_DIST_CHECKPOINT_FROM_START in df_checkpoints_lap
        row = df_lap.iloc[i]
        dist_checkpoint_from_start = row[COL_NAME_DIST_CHECKPOINT_FROM_START]
        if dist_checkpoint_from_start not in dict_checkpoint_index_by_dist_from_start:
            raise Exception('dist_checkpoint_from_start not in dict_checkpoint_index_by_dist_from_start')
        row_in_checkpoints = dict_checkpoint_index_by_dist_from_start[dist_checkpoint_from_start]
        time_checkpoint = df_checkpoints_lap.iloc[row_in_checkpoints][COL_NAME_LAP_MS]
        df_lap.loc[df_lap.index[i], col_name] = (row[COL_NAME_LAP_MS] - time_checkpoint) / 1000
    return df_lap


def update_x_min_y_min(df_lap, x_col_name_2_use, x_max, x_min):
    if x_min is None:
        x_min = df_lap[x_col_name_2_use].min()
    else:
        x_min = min(x_min, df_lap[x_col_name_2_use].min())
    if x_max is None:
        x_max = df_lap[x_col_name_2_use].max()
    else:
        x_max = max(x_max, df_lap[x_col_name_2_use].max())
    return x_max, x_min


def quick_new_and_connect_cursor(fig, axs):
    # Add cursor
    cc = CustomCursor(axs, color='blue', xlimits=[0, 100], ylimits=[0, 100])
    fig.canvas.mpl_connect('motion_notify_event', cc.show_xy)
    fig.canvas.mpl_connect('axes_leave_event', cc.hide_y)
    return cc


def draw_x_lap_checkpoint_dist_curves_diff_continus_laps_all_same_timeing_line(list_2_compare, cols):
    tuple_checkpoints = list_2_compare[0]
    continus_laps_checkpoints = tuple_checkpoints[0]
    for tuple_now in list_2_compare:
        continus_laps: ContinusLaps = tuple_now[0]
        print(continus_laps.longtitude_start, continus_laps.latitude_start)
