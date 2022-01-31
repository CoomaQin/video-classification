import os
import uuid
import subprocess
import glob
import pandas as pd
from collections import defaultdict


def download_raw_videos(youtube_url: str,
                        tmp_dir: str = '/tmp',
                        num_attempts: int = 5) -> str:
    """
    Download a video from youtube if exists and is not blocked.
    arguments:
    ---------
    url: str
        Unique video url

    start_time: float
        Indicates the begining time in seconds from where the video
        will be trimmed.
    end_time: float
        Indicates the ending time in seconds of the trimmed video.
    """
    # Construct command line for getting the direct video link.
    tmp_filename = os.path.join(tmp_dir,
                                '%s.%%(ext)s' % uuid.uuid4())
    command = ['youtube-dl',
               '--quiet', '--no-warnings',
               '-f', 'mp4',
               '-o', '"%s"' % tmp_filename,
               '"%s"' % (youtube_url)]
    command = ' '.join(command)
    attempts = 0
    while True:
        try:
            _ = subprocess.check_output(command, shell=True,
                                        stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            attempts += 1
            if attempts == num_attempts:
                return err.output
        else:
            break

    tmp_filename = glob.glob('%s*' % tmp_filename.split('.')[0])[0]
    return tmp_filename


def extract_clips(tmp_filename:str, output_filename:str, start_time:str, duration:str) -> None:
    """
        output_filename: str
        File path where the video will be stored.
    """
    status = False
    # Construct command to trim the videos (ffmpeg required).
    command = ['ffmpeg',
               '-i', '"%s"' % tmp_filename,
               '-ss', str(start_time),
               '-t', str(duration),
               '-c:v', 'libx264', '-c:a', 'copy',
               '-threads', '1',
               '-loglevel', 'panic',
               '"%s"' % output_filename]
    command = ' '.join(command)
    try:
        _ = subprocess.check_output(command, shell=True,
                                    stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        return status, err.output

    # Check if the video was successfully saved.
    status = os.path.exists(output_filename)
    os.remove(tmp_filename)
    return status


def main(csv_path):
    video_clip_dict = defaultdict(list)
    df = pd.read_csv(csv_path)
    idx = 1
    while idx < len(df):
        video_clip_dict[df["url"][idx]].append(
            (df["time_start"][idx], df["duration"][idx]))
        idx += 1
    print(video_clip_dict)
    for k in video_clip_dict:
        vn = download_raw_videos(k)
        for c in video_clip_dict[k]:
            extract_clips(vn, f"{vn}-{c[0]}", c[0], c[1])
            break
        break

if __name__ == "__main__":
    main("./sample.csv")
