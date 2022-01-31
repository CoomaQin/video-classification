from traceback import print_tb
import torch
import json
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
from pytorchvideo.data.encoded_video import EncodedVideo
from torchvision.transforms import (
    Compose,
    Lambda,
    RandomCrop,
    RandomHorizontalFlip
)
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
    Normalize,
    RandomShortSideScale,
    ShortSideScale,
    UniformTemporalSubsample
)
from typing import Dict
from model import VideoClassificationLightningModule

side_size = 256
mean = [0.45, 0.45, 0.45]
std = [0.225, 0.225, 0.225]
crop_size = 256
num_frames = 32
sampling_rate = 2
frames_per_second = 30
alpha = 4


class PackPathway(torch.nn.Module):
    """
    Transform for converting video frames as a list of tensors.
    """

    def __init__(self):
        super().__init__()

    def forward(self, frames: torch.Tensor):
        fast_pathway = frames
        # Perform temporal sampling from the fast pathway.
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // alpha
            ).long(),
        )
        frame_list = [slow_pathway, fast_pathway]
        return frame_list


transform = ApplyTransformToKey(
    key="video",
    transform=Compose(
        [
            UniformTemporalSubsample(num_frames),
            Lambda(lambda x: x/255.0),
            NormalizeVideo(mean, std),
            ShortSideScale(
                size=side_size
            ),
            CenterCropVideo(crop_size),
            PackPathway()
        ]
    ),
)

train_transform = Compose(
    [
        ApplyTransformToKey(
            key="video",
            transform=Compose(
                [
                    UniformTemporalSubsample(8),
                    Lambda(lambda x: x / 255.0),
                    Normalize((0.45, 0.45, 0.45),
                              (0.225, 0.225, 0.225)),
                    RandomShortSideScale(
                        min_size=256, max_size=320),
                    RandomCrop(244),
                    RandomHorizontalFlip(p=0.5),
                ]
            ),
        ),
    ]
)


if __name__ == "__main__":
    # Load the trained model
    weight_path = "./lightning_logs/version_6/checkpoints/epoch=24-step=8049.ckpt"
    device = torch.device("cuda:0") if torch.cuda.is_available() else "cpu"
    model = VideoClassificationLightningModule.load_from_checkpoint(
        weight_path)
    video_path = "./data/bridge_strike/train/positive/truck_4.mp4"
    model.freeze()
    model = model.to(device)

    # Load the example video

    # Select the duration of the clip to load by specifying the start and end duration
    # The start_sec should correspond to where the action occurs in the video
    start_sec = 0
    end_sec = start_sec + 5

    # Initialize an EncodedVideo helper class
    video = EncodedVideo.from_path(video_path)

    # Load the desired clip
    video_data = video.get_clip(start_sec=start_sec, end_sec=end_sec)

    # Apply a transform to normalize the video input
    print(video_data["video"].shape)
    video_data = transform(video_data)
    inputs = video_data["video"]
    # TODO figure out why video_data["video"] is a 2-element array
    # Move the inputs to the desired device
    inputs = [i.to(device)[None, ...] for i in inputs]
    print(inputs[0].shape)
    # Pass the input clip through the model
    with torch.no_grad():
        preds = model(inputs[0])
        print(preds)
