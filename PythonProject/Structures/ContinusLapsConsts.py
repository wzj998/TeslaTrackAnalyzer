# Index(['Lap', 'Elapsed Time (ms)', 'Elapsed Time (mm:ss.ms)',
#        'Total Time (ms)', 'Total Time (mm:ss.ms)', 'Speed (MPH)',
#        'Speed (KMH)', 'Latitude (decimal)', 'Longitude (decimal)',
#        'Lateral Acceleration (m/s^2)', 'Longitudinal Acceleration (m/s^2)',
#        'Throttle Position (%)', 'Brake Pressure (bar)', 'Steering Angle (deg)',
#        'Steering Angle Rate (deg/s)', 'Yaw Rate (rad/s)', 'Power Level (KW)',
#        'State of Charge (%)', 'Tire Pressure Front Left (bar)',
#        'Tire Pressure Front Right (bar)', 'Tire Pressure Rear Left (bar)',
#        'Tire Pressure Rear Right (bar)',
#        'Brake Temperature Front Left (% est.)',
#        'Brake Temperature Front Right (% est.)',
#        'Brake Temperature Rear Left (% est.)',
#        'Brake Temperature Rear Right (% est.)', 'Front Inverter Temp (%)',
#        'Rear Inverter Temp (%)', 'Battery Temp (%)',
#        'Tire Slip Front Left (% est.)', 'Tire Slip Front Right (% est.)',
#        'Tire Slip Rear Left (% est.)', 'Tire Slip Rear Right (% est.)'],
#       dtype='object')

COL_NAME_LAP = 'Lap'

COL_NAME_LAP_MS = 'Elapsed Time (ms)'
COL_NAME_LAP_DATETIME = 'Elapsed Time (mm:ss.ms)'
COL_NAME_DIST_CHECKPOINT_FROM_START = 'Distance from Start (m)'  # only in copy of df
COL_NAME_TIME_DELTA = 'Time Delta (s)'  # only in copy of df
COL_NAME_TOTAL_MS = 'Total Time (ms)'
COL_NAME_TOTAL_DATETIME = 'Total Time (mm:ss.ms)'

COL_NAME_LATITUDE = 'Latitude (decimal)'
COL_NAME_LONGITUDE = 'Longitude (decimal)'
COL_NAME_Y_M = 'y (m)'  # only in copy of df
COL_NAME_X_M = 'x (m)'  # only in copy of df

COL_NAME_SPEED_MPH = 'Speed (MPH)'
COL_NAME_SPEED_KMH = 'Speed (KMH)'

COL_NAME_BRAKE = 'Brake Pressure (bar)'
COL_NAME_THROTTLE = 'Throttle Position (%)'

COL_NAME_STEER_ANGLE = 'Steering Angle (deg)'

COL_NAME_LAT_ACCEL = 'Lateral Acceleration (m/s^2)'
COL_NAME_LONG_ACCEL = 'Longitudinal Acceleration (m/s^2)'

COL_NAME_POWER_LEVEL = 'Power Level (KW)'

COL_NAME_STATE_OF_CHARGE = 'State of Charge (%)'

COL_NAME_TIRE_SLIP_FRONT_LEFT = 'Tire Slip Front Left (% est.)'
COL_NAME_TIRE_SLIP_FRONT_RIGHT = 'Tire Slip Front Right (% est.)'
COL_NAME_TIRE_SLIP_REAR_LEFT = 'Tire Slip Rear Left (% est.)'
COL_NAME_TIRE_SLIP_REAR_RIGHT = 'Tire Slip Rear Right (% est.)'

COL_NAME_BRAKE_TEMP_FRONT_LEFT = 'Brake Temperature Front Left (% est.)'
COL_NAME_BRAKE_TEMP_FRONT_RIGHT = 'Brake Temperature Front Right (% est.)'

COL_NAME_REAR_INVERTER_TEMP = 'Rear Inverter Temp (%)'
COL_NAME_BATTERY_TEMP = 'Battery Temp (%)'
