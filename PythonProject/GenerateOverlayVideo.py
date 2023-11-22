import pandas as pd
import imageio

from AboutDraw import OverlayVideoTool
from Structures import ContinusLaps


def main():
    csv_path = '../SampleData/telemetry-v1-2023-10-28-16_25_58.csv'
    out_video_path = '../SampleOut/overlay_video.mp4'

    continus_lap = ContinusLaps.ContinusLaps(pd.read_csv(csv_path), 100)
    # generate overlay video, background is green
    img_paths = OverlayVideoTool.generate_overlay_video_img_paths(continus_lap, 1280, 960,
                                                                  3,
                                                                  29)
    # save overlay video using ImageIO
    writer = imageio.get_writer(out_video_path, fps=60)
    for i_img_path in range(len(img_paths)):
        reader = imageio.get_reader(img_paths[i_img_path])
        for frame in reader:  # 虽然有for应该就1帧
            writer.append_data(frame)
        if i_img_path % 60 == 0:
            print(f'\rsave overlay video: {i_img_path / len(img_paths) * 100:.0f}%', end='')
    writer.close()
    print(f'\rsave overlay video: 100%')


if __name__ == "__main__":
    main()
