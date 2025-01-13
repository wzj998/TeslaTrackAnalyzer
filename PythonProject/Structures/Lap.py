from Structures.ContinusLaps import *
from Structures.ContinusLapsConsts import *


class Lap:
    def __init__(self, continus_laps: ContinusLaps, continus_laps_index: int, lap_index: int):
        self.continus_laps = continus_laps
        # 用来区分第几个csv
        self.continus_laps_index = continus_laps_index
        self.lap_index = lap_index
        self.df_lap = continus_laps.df[continus_laps.df[COL_NAME_LAP] == lap_index].copy()
