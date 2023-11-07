import math
import multiprocessing
from multiprocessing import Pool

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

from ContinusLapsConsts import *
from CustomCursor import CustomCursor


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
def draw_x_lap_time_curves_same_continues_laps(df, laps_2_draw, cols, title='Lap Time Curves'):
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


def draw_ax_lap_time(axs, laps_2_draw, dict_df_laps_2_draw, cols):
    x_col_name_2_use = COL_NAME_LAP_DATETIME
    x_min = None
    x_max = None
    for lap in laps_2_draw:
        df_lap = dict_df_laps_2_draw[lap]
        str_label = 'Lap ' + str(lap)
        for i in range(len(cols)):
            axs[i].plot(df_lap[x_col_name_2_use], df_lap[cols[i]], label=str_label + ' ' + cols[i])

        x_max, x_min = update_x_min_y_min(df_lap, x_col_name_2_use, x_max, x_min)

    for ax in axs:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S.%f'))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=(x_max - x_min).seconds // 5))
        ax.set_xlim(left=x_min, right=x_max)
        ax.legend()


def draw_x_lap_checkpoint_dist_curves_same_continues_laps(df, laps_2_draw, cols,
                                                          title='Lap Checkpoint Dist Curves'):
    # extract data for laps to draw
    df_laps_2_draw = df[df[COL_NAME_LAP].isin(laps_2_draw)].copy()  # 保险起见，先复制一份

    fig, axs = plt.subplots(len(cols), 1, sharex='all', figsize=(12, 8))

    dict_df_laps_2_draw = {}
    for lap in laps_2_draw:
        dict_df_laps_2_draw[lap] = df_laps_2_draw[df_laps_2_draw[COL_NAME_LAP] == lap]

    # use first lap in laps_2_draw to generate checkpoints
    checkpoints_lap = laps_2_draw[0]
    # we asume that in checkpoints_lap, the car is always moving by correct direction in the track,
    # has no reverse or stop, and the gps data is accurate enough
    df_checkpoints_lap = interpolate_x_m_y_m(dict_df_laps_2_draw[checkpoints_lap])
    # print(df_checkpoints_lap.to_string())
    draw_ax_lap_checkpoint_dist(axs, df_checkpoints_lap, laps_2_draw, dict_df_laps_2_draw, cols)

    plt.xlabel('Distance (m)')
    for ax in axs:
        ax.grid()

    fig.suptitle(title)

    # cc needs to be returned to avoid being garbage collected
    return fig, axs, quick_new_and_connect_cursor(fig, axs)


def get_dist_squared(x_m, y_m, x_m_last, y_m_last):
    return (x_m - x_m_last) ** 2 + (y_m - y_m_last) ** 2


def get_dist(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached):
    return math.sqrt(get_dist_squared(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached))


def get_max_x_or_y_dist(x_m, y_m, x_m_last, y_m_last):
    return max(abs(x_m - x_m_last), abs(y_m - y_m_last))


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
                              eps=1e-6):
    if len(df_lap) <= 0:
        raise Exception('df_lap is empty in add_col_dist_from_start')

    # add after COL_NAME_LAP_DATETIME
    df_lap.insert(df_lap.columns.get_loc(COL_NAME_LAP_DATETIME) + 1, col_name, -1)

    dict_checkpoints_reached_by_index = get_dict_checkpoints_reached_by_index(df_checkpoints_lap, df_lap)

    keys_sorted = sorted(dict_checkpoints_reached_by_index.keys())  # 保险起见，先排序
    for i_key in range(len(keys_sorted) - 1):
        # 如果一行记录对应多个检查点，除了第一个检查点以外的所有检查点用于给这行记录之后，下个key对应的记录之前的记录插值
        # 首先，第一个检查点归自己
        key = keys_sorted[i_key]
        checkpoint_indexes = dict_checkpoints_reached_by_index[key]
        df_lap.loc[df_lap.index[key], col_name] = dist_from_start_by_checkpoint_index[checkpoint_indexes[0]]

        checkpoints_remain = checkpoint_indexes[1:]
        # 接着，除了第一个检查点以外的所有检查点用于给这行记录之后，下个key对应的记录之前的记录插值
        next_key = keys_sorted[i_key + 1]
        if next_key - key <= 1:
            continue
        # find last same row after key, before next_key
        row_index_last_same = -1
        for i in range(key + 1, next_key):
            row = df_lap.iloc[i]
            x_m = row[COL_NAME_X_M]
            y_m = row[COL_NAME_Y_M]
            row_last = df_lap.iloc[i - 1]
            x_m_last = row_last[COL_NAME_X_M]
            y_m_last = row_last[COL_NAME_Y_M]
            if get_max_x_or_y_dist(x_m, y_m, x_m_last, y_m_last) < eps:
                row_index_last_same = i  # 为什么不从后往前呢，怕遇到中间坐标有变化，后面回来的情况
                break
        if row_index_last_same != -1:
            # 如果next_key和key位置相同，那么就插值了个寂寞
            interpolate_x_m_y_m_between(df_lap, key, row_index_last_same + 1)
        # 剩下的每个检查点，找到离自己最近的那行记录
        for checkpoint_index in checkpoints_remain:
            x_m_checkpoint_reached = df_checkpoints_lap.iloc[checkpoint_index][COL_NAME_X_M]
            y_m_checkpoint_reached = df_checkpoints_lap.iloc[checkpoint_index][COL_NAME_Y_M]
            min_dist_sqr = None
            min_dist_row_index = None
            for i in range(key + 1, next_key):
                row = df_lap.iloc[i]
                x_m = row[COL_NAME_X_M]
                y_m = row[COL_NAME_Y_M]
                dist_sqr = get_dist_squared(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached)
                if min_dist_sqr is None or dist_sqr < min_dist_sqr:
                    min_dist_sqr = dist_sqr
                    min_dist_row_index = i
            if min_dist_row_index is None:
                raise Exception('min_dist_row_index is None in add_col_dist_from_start')
            df_lap.loc[df_lap.index[min_dist_row_index], col_name] = dist_from_start_by_checkpoint_index[
                checkpoint_index]

    # 最后一行记录一定对应最后一个检查点
    df_lap.loc[df_lap.index[len(df_lap) - 1], col_name] = dist_from_start_by_checkpoint_index[
        len(df_checkpoints_lap) - 1]

    # print('list(df_lap[' + col_name + ']):', list(df_lap[col_name]))
    # remove all rows with col_name == -1
    df_lap_remove = df_lap[df_lap[col_name] != -1]

    return df_lap_remove


def get_dict_checkpoints_reached_by_index(df_checkpoints_lap, df_lap):
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
            dist_sqr_next_2_checkpoint = get_dist_squared(x_m_next, y_m_next, x_m_checkpoint_reached, y_m_checkpoint_reached)

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
    # 我们认为终点一定到达了最后一个检查点
    # if df_checkpoints_lap last and last - 1 in same position, 说明预处理工作没做好
    if df_lap.iloc[len(df_lap) - 1][COL_NAME_X_M] == \
            df_lap.iloc[len(df_lap) - 2][COL_NAME_X_M] and \
            df_lap.iloc[len(df_lap) - 1][COL_NAME_Y_M] == \
            df_lap.iloc[len(df_lap) - 2][COL_NAME_Y_M]:
        raise Exception('df_checkpoints_lap last and last - 1 are the same in add_col_dist_from_start')
    # if index_checkpoint_will_reach < len(df_checkpoints_lap) - 1
    # add index_checkpoint_will_reach~len(df_checkpoints_lap) - 1 to dict_checkpoints_reached_by_index
    if index_checkpoint_will_reach < len(df_checkpoints_lap) - 1:
        dict_checkpoints_reached_by_index[len(df_lap) - 1] = list(range(index_checkpoint_will_reach,
                                                                        len(df_checkpoints_lap)))
    # print('len(df_checkpoints_lap) =', len(df_checkpoints_lap), 'len(df_lap) =', len(df_lap))
    # print('dict_checkpoints_reached_by_index:', dict_checkpoints_reached_by_index)
    return dict_checkpoints_reached_by_index


def draw_ax_lap_checkpoint_dist(axs, df_checkpoints_lap, laps_2_draw, dict_df_laps_2_draw, cols):
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
    num_process = min(multiprocessing.cpu_count(), len(laps_2_draw))
    pool = Pool(num_process)
    # 使用进程池并行处理 lap
    results = [pool.apply_async(__process_lap, args=(
        lap, df_checkpoints_lap, dict_df_laps_2_draw[lap], dist_from_start_by_checkpoint_index))
               for lap in laps_2_draw]
    # 等待所有lap处理完成
    for result in results:
        result.get()
    # 关闭进程池
    pool.close()
    pool.join()
    # change dict by results
    for result in results:
        lap, df_lap = result.get()
        dict_df_laps_2_draw[lap] = df_lap
    print("All laps processed.")

    for lap in laps_2_draw:
        df_lap = dict_df_laps_2_draw[lap]
        str_label = 'Lap ' + str(lap)
        for i in range(len(cols)):
            axs[i].plot(df_lap[x_col_name_2_use], df_lap[cols[i]], label=str_label + ' ' + cols[i])

        x_max, x_min = update_x_min_y_min(df_lap, x_col_name_2_use, x_max, x_min)

    for ax in axs:
        ax.set_xlim(left=x_min, right=x_max)
        ax.legend()


def __process_lap(lap, df_checkpoints_lap, df_lap, dist_from_start_by_checkpoint_index):
    df_lap = __add_dist_and_time_delta_points(df_checkpoints_lap, df_lap, dist_from_start_by_checkpoint_index)
    print('lap:', lap, 'finished')
    return lap, df_lap


def __add_dist_and_time_delta_points(df_checkpoints_lap, df_lap, dist_from_start_by_checkpoint_index):
    df_lap = remove_last_same_pos(df_lap)
    df_lap = __add_col_dist_from_start(df_lap, df_checkpoints_lap,
                                       dist_from_start_by_checkpoint_index,
                                       COL_NAME_DIST_CHECKPOINT_FROM_START)
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


def remove_last_same_pos(df_lap):
    if len(df_lap) <= 0:
        raise Exception('df_lap is empty in remove_last_same_pos')
    row_last = df_lap.iloc[len(df_lap) - 1]
    x_m_last = row_last[COL_NAME_X_M]
    y_m_last = row_last[COL_NAME_Y_M]
    for i in range(len(df_lap) - 2, -1, -1):
        row = df_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        if x_m != x_m_last or y_m != y_m_last:
            break
        else:
            df_lap = df_lap.drop(df_lap.index[i], inplace=False)
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


def interpolate_x_m_y_m(df_checkpoints_lap):
    if len(df_checkpoints_lap) <= 0:
        raise Exception('df_checkpoints_lap is empty in interpolate_x_m_y_m')
    # get first index of df_checkpoints_lap
    row_index_last = 0
    x_m_last = df_checkpoints_lap.iloc[row_index_last][COL_NAME_X_M]
    y_m_last = df_checkpoints_lap.iloc[row_index_last][COL_NAME_Y_M]
    # for row in df_checkpoints_lap, if x_m or y_m change, interpolate x_m and y_m before
    for i in range(len(df_checkpoints_lap)):
        row = df_checkpoints_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        if x_m != x_m_last or y_m != y_m_last:
            # interpolate rows before
            interpolate_x_m_y_m_between(df_checkpoints_lap, row_index_last, i)
            row_index_last = i
            x_m_last = x_m
            y_m_last = y_m
    # remove final rows
    df_checkpoints_lap = df_checkpoints_lap.drop(df_checkpoints_lap.index[row_index_last + 1:], inplace=False)

    # 如果还是有相邻若干行的x_m和y_m都相同，那么移除后面的行
    rows_final = []
    rows_index_still_need_remove = []
    for i in range(len(df_checkpoints_lap)):
        row = df_checkpoints_lap.iloc[i]
        x_m = row[COL_NAME_X_M]
        y_m = row[COL_NAME_Y_M]
        if i == 0:
            rows_final.append(row)
        else:
            row_last = rows_final[-1]
            x_m_last = row_last[COL_NAME_X_M]
            y_m_last = row_last[COL_NAME_Y_M]
            if x_m != x_m_last or y_m != y_m_last:
                rows_final.append(row)
            else:
                rows_index_still_need_remove.append(i)
    if len(rows_index_still_need_remove) > 0:
        print('interpolate_x_m_y_m rows_index_still_need_remove:', rows_index_still_need_remove)
        # convert rows_final to df
        return pd.DataFrame(rows_final, columns=df_checkpoints_lap.columns)
    else:
        return df_checkpoints_lap


def interpolate_x_m_y_m_between(df_checkpoints_lap, row_index_last, row_index):
    if row_index_last >= row_index:
        raise Exception('row_index_last >= row_index in interpolate_x_m_y_m_between')
    row_last = df_checkpoints_lap.iloc[row_index_last]
    row = df_checkpoints_lap.iloc[row_index]
    x_m_last = row_last[COL_NAME_X_M]
    y_m_last = row_last[COL_NAME_Y_M]
    x_m = row[COL_NAME_X_M]
    y_m = row[COL_NAME_Y_M]
    x_m_delta = x_m - x_m_last
    y_m_delta = y_m - y_m_last
    row_index_delta = row_index - row_index_last
    for i in range(1, row_index_delta):
        row_index_i = row_index_last + i
        x_m_i = x_m_last + x_m_delta / row_index_delta * i
        y_m_i = y_m_last + y_m_delta / row_index_delta * i
        df_checkpoints_lap.loc[df_checkpoints_lap.index[row_index_i], COL_NAME_X_M] = x_m_i
        df_checkpoints_lap.loc[df_checkpoints_lap.index[row_index_i], COL_NAME_Y_M] = y_m_i


def quick_new_and_connect_cursor(fig, axs):
    # Add cursor
    cc = CustomCursor(axs, color='blue', xlimits=[0, 100], ylimits=[0, 100])
    fig.canvas.mpl_connect('motion_notify_event', cc.show_xy)
    fig.canvas.mpl_connect('axes_leave_event', cc.hide_y)
    return cc
