import math


def get_dist_squared(x_m, y_m, x_m_last, y_m_last):
    return (x_m - x_m_last) ** 2 + (y_m - y_m_last) ** 2


def get_dist(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached):
    return math.sqrt(get_dist_squared(x_m, y_m, x_m_checkpoint_reached, y_m_checkpoint_reached))
