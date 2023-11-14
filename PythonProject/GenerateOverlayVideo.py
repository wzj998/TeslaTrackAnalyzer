import multiprocessing

import pandas as pd

from Structures import ContinusLaps
from AboutDraw import OverlayVideoTool


def main():
    csv_path = '../SampleData/telemetry-v1-2023-10-28-16_25_58.csv'
    continus_lap = ContinusLaps.ContinusLaps(pd.read_csv(csv_path), 100)
    # generate overlay video, background is transparent
    overlay_video = OverlayVideoTool.generate_overlay_video(continus_lap, 1280, 960, 100)
    # save overlay video
    overlay_video.write_videofile('../SampleOut/overlay_video.mp4', fps=60,
                                  codec='libx264', threads=multiprocessing.cpu_count())


if __name__ == "__main__":
    main()
