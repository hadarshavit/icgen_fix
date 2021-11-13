import more_itertools
import torch
from torchvision.datasets import VisionDataset
from pathlib import Path
from typing import Tuple, Sequence, Optional, Union, Callable, Any
import pickle
import numpy as np
import json
from PIL import Image


class ICVisionDataset(VisionDataset):
    """ Rudimentary implementation of a VisionDataset sub-class that should provide
    torchvision-compatibility for a number of datasets generated by ICGen. """
    def __init__(self, dataset: str, root: Path, split: str,
                 transform: Optional[Callable] = None,
                 target_transform: Optional[Callable] = None):
        super(ICVisionDataset, self).__init__(str(root), transform=transform,
                                              target_transform=target_transform)
        datadir = root / dataset
        with open(datadir / "info.json") as fp:
            meta = json.load(fp)
        splits = meta["torch_info"]["splits"]
        assert split in splits, f"Unknown data split: {split}, must be one of {splits}."

        datafile = datadir / f"{split}-split"
        with open(datafile, "rb") as fp:
            data = pickle.load(fp)

        images = data["images"]
        # Only applicable for datasets with square images
        self.images = np.stack(images).reshape((-1, meta["num_channels"], meta["max_dim"],
                                                meta["max_dim"]))
        # self.images = self.images.transpose((0, 2, 3, 1))  # convert to HWC
        self.labels = data["labels"]
        self.meta = meta

    def __getitem__(self, index) -> Tuple[Any, Any]:
        # To stick with the convention of other torchvision datasets, this will return
        # PIL Images.
        img, label = self.images[index], self.images[index]

        img = Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            label = self.target_transform(label)

        return img, label

    def __len__(self):
        return len(self.images)
