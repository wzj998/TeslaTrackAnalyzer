# convert csv to new csv
# Distance	Speed	Lateral Acceleration
# m	km/h	m/s^2

import pandas as pd
import math
from Structures.ContinusLapsConsts import *
from Structures import ContinusLaps, ContinusLapsPrepare, Lap
from Utils.WheelUtil import calculate_wheel_diameter

COL_NAME_DIST_CONVERTED = 'Distance'
COL_NAME_SPEED_CONVERTED = 'Speed'
COL_NAME_LAT_ACCEL_CONVERTED = 'Lateral Acceleration'

def do_convert(lap):
    rows_converted = []
    dist = 0
    df = lap.df_lap

    for i in range(len(df)):
        row = df.iloc[i].copy()
        if i > 0:
            row_last = df.iloc[i - 1].copy()
            dist += math.sqrt((row[COL_NAME_X_M] - row_last[COL_NAME_X_M]) ** 2 + (row[COL_NAME_Y_M] - row_last[COL_NAME_Y_M]) ** 2)
        row[COL_NAME_DIST_CONVERTED] = dist
        row[COL_NAME_SPEED_CONVERTED] = row[COL_NAME_SPEED_KMH]
        row[COL_NAME_LAT_ACCEL_CONVERTED] = row[COL_NAME_LAT_ACCEL]
        rows_converted.append(row)

    return rows_converted

def main():
    csv_path = '../SampleData/telemetry-v1-2025-01-11-15_44_35.csv'
    df = pd.read_csv(csv_path)

    continus_lapss = []
    longtitude_start = None
    latitude_start = None
    if longtitude_start is None:
        longtitude_start = df[COL_NAME_LONGITUDE].iloc[0]
        latitude_start = df[COL_NAME_LATITUDE].iloc[0]
    original_wheel_diameter = calculate_wheel_diameter(235, 40, 19)
    altitude = 4
    continus_laps = ContinusLaps.ContinusLaps(df,
                                                    calculate_wheel_diameter(295, 35, 18) / original_wheel_diameter,
                                                    longtitude_start, latitude_start,
                                                    altitude)    
    
    lap_indexes_2_fastest = list(continus_laps.validlap_times_dict_sorted.keys())[0]
    lap_fastest = Lap.Lap(continus_laps, 0, lap_indexes_2_fastest)

    rows_converted = do_convert(lap_fastest)
    df_converted = pd.DataFrame(rows_converted, columns=[COL_NAME_DIST_CONVERTED, COL_NAME_SPEED_CONVERTED, COL_NAME_LAT_ACCEL_CONVERTED])
    # df_converted.to_csv('../SampleOut/converted.csv', index=False)
    # second line write units
    with open('../SampleOut/converted.csv', 'w') as f:
        f.write('Distance,Speed,Lateral Acceleration\n')
        f.write('m,km/h,m/s^2\n')
        for row in rows_converted:
            f.write(f'{row[COL_NAME_DIST_CONVERTED]},{row[COL_NAME_SPEED_CONVERTED]},{row[COL_NAME_LAT_ACCEL_CONVERTED]}\n')

if __name__ == '__main__':
    main()
