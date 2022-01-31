import os
import pandas as pd
import argparse
import subprocess
import datetime

def create_video_folders(data_root: str, dataset: pd.DataFrame) -> None:
    if 'label' not in dataset.columns:
        print("label-name not in metadata csv")
        exit(1)
    else:
        for col in dataset['label'].unique():
            outpath = os.path.join(data_root, col)
            if not os.path.exists(outpath):
                os.makedirs(outpath)


def extract_clips(data_root: str, dataset: pd.DataFrame, name="truck") -> None:
    idx = 0
    while idx < len(dataset):
        outpath = os.path.join(data_root, dataset["label"][idx], f'{name}_{idx}.mp4')
        print(idx, outpath)
        if os.path.exists(outpath):
            idx += 1
            continue
        fm = "%M:%S.%f" if len(dataset["time_start"][idx].split(".")) > 1 else "%H:%M:%S"
        start = datetime.datetime.strptime(dataset["time_start"][idx], fm)
        duration = datetime.datetime.strptime(dataset["duration"][idx], fm)
        delta = datetime.timedelta(seconds=max(1, duration.second - 4))
        start += delta
        duration += delta
        command = ['ffmpeg',
                   '-i', '"%s"' % dataset["path"][idx],
                   '-ss', str(start.time()),
                   '-t', str(duration.time()),
                   '-c:v', 'libx264', '-c:a', 'copy',
                   '-threads', '1',
                   '-loglevel', 'panic',
                   '"%s"' % outpath]
        command = ' '.join(command)
        msg = ""
        try:
            msg = subprocess.check_output(command, shell=True,
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print(err, msg)
            exit(1)
        idx += 1


def main(input_csv, data_root):
    df = pd.read_csv(input_csv)
    create_video_folders(data_root, df)
    extract_clips(data_root, df)


if __name__ == '__main__':
    description = 'Helper script for exrtact bridge strike video clips from raw online videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--input_csv', type=str,
                   help=('CSV file containing the metadata'))
    p.add_argument('--data_root', type=str,
                   help='Output directory where videos will be saved.')
    main(**vars(p.parse_args()))
