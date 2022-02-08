from torchvision.transforms import (
    Compose,
    Lambda,
    RandomCrop,
    RandomHorizontalFlip
)
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
import os
import pytorch_lightning
import pytorchvideo.data
import torch.utils.data
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    Normalize,
    RemoveKey,
    ShortSideScale,
    RandomShortSideScale,
    UniformTemporalSubsample
)
import torch
from model import VideoClassificationLightningModule


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


class BridgeStrikeDataModule(pytorch_lightning.LightningDataModule):

    def __init__(self) -> None:
        super().__init__()
        self._DATA_PATH = "./data/bridge_strike"
        self._CLIP_DURATION = 1  # Duration of sampled clip for each video
        self._BATCH_SIZE = 1
        self._NUM_WORKERS = 0  # Number of parallel processes fetching data
        self._SAMPLE_RATE = 16

    def train_dataloader(self):
        """
        Create the Kinetics train partition from the list of video labels
        in {self._DATA_PATH}/train
        """
    #     train_dataset = pytorchvideo.data.Kinetics(
    #         data_path=os.path.join(self._DATA_PATH, "train"),
    #         clip_sampler=pytorchvideo.data.make_clip_sampler(
    #             "random", self._CLIP_DURATION),
    #         decode_audio=False,
    #     )
    #     return torch.utils.data.DataLoader(
    #         train_dataset,
    #         batch_size=self._BATCH_SIZE,
    #         num_workers=self._NUM_WORKERS,
    #     )

    # def val_dataloader(self):
    #     """
    #     Create the Kinetics validation partition from the list of video labels
    #     in {self._DATA_PATH}/val
    #     """
    #     val_dataset = pytorchvideo.data.Kinetics(
    #         data_path=os.path.join(self._DATA_PATH, "val"),
    #         clip_sampler=pytorchvideo.data.make_clip_sampler(
    #             "uniform", self._CLIP_DURATION),
    #         decode_audio=False,
    #     )
    #     return torch.utils.data.DataLoader(
    #         val_dataset,
    #         batch_size=self._BATCH_SIZE,
    #         num_workers=self._NUM_WORKERS,
    #     )

    def train_dataloader(self):
        """
          Create the Kinetics train partition from the list of video labels
          in {self._DATA_PATH}/train.csv. Add transform that subsamples and
          normalizes the video before applying the scale, crop and flip augmentations.
          """
        transform = ApplyTransformToKey(
            key="video",
            transform=Compose(
                [
                    UniformTemporalSubsample(self._SAMPLE_RATE),
                    Lambda(lambda x: x / 255.0),
                    Normalize((0.45, 0.45, 0.45), (0.225, 0.225, 0.225)),
                    RandomShortSideScale(min_size=640, max_size=720),
                    RandomCrop(320),
                    RandomHorizontalFlip(p=0.5),
                ]
            ),
        )
        train_dataset = pytorchvideo.data.Kinetics(
            data_path=os.path.join(self._DATA_PATH, "train.csv"),
            clip_sampler=pytorchvideo.data.make_clip_sampler(
                "random", self._CLIP_DURATION),
            transform=transform
        )
        train_dataset = pytorchvideo.data.Kinetics(
            data_path=os.path.join(self._DATA_PATH, "val.csv"),
            clip_sampler=pytorchvideo.data.make_clip_sampler(
                "random", self._CLIP_DURATION),
            transform=transform
        )
        return torch.utils.data.DataLoader(
            train_dataset,
            batch_size=self._BATCH_SIZE,
            num_workers=self._NUM_WORKERS,
        )


if __name__ == "__main__":
    classification_module = VideoClassificationLightningModule()
    data_module = BridgeStrikeDataModule()
    # dl = data_module.train_dataloader()
    # print(dl.dataset._labeled_videos[0])
    # print(dl.dataset.__next__()["video"].shape)
    trainer = pytorch_lightning.Trainer(gpus=1, max_epochs=300)
    trainer.fit(classification_module, data_module)
