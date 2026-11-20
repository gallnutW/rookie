from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from config import (
    DATA_ROOT,
    EVAL_BATCH_SIZE,
    IMAGE_SIZE,
    NUM_WORKERS,
    TRAIN_BATCH_SIZE,
)


TRAIN_MEAN = (0.48023694, 0.44806704, 0.39750364)
TRAIN_STD = (0.27643643, 0.26886328, 0.28158993)


def load_class_mapping(data_root=DATA_ROOT):
    """以 wnids.txt 的顺序建立唯一、固定的类别映射。"""

    wnids = []
    text = (data_root / "wnids.txt").read_text(encoding="utf-8")

    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            wnids.append(stripped)

    return {wnid: idx for idx, wnid in enumerate(wnids)}


def build_manifests(data_root=DATA_ROOT):
    """建立训练、验证和测试集清单。"""

    train_root = data_root / "train"
    val_root = data_root / "val"
    test_root = data_root / "test"

    class_to_idx = load_class_mapping(data_root)

    # train/<wnid>/images/xxx.JPEG
    train_samples = []
    for path in sorted(train_root.glob("*/*/*.JPEG")):
        wnid = path.parent.parent.name
        label = class_to_idx[wnid]
        train_samples.append((path.relative_to(data_root), label))

    # val/images/*.JPEG，标签来自 val_annotations.txt 的前两列。
    val_annotation = {}
    annotation_path = val_root / "val_annotations.txt"

    for line in annotation_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        fields = line.split("\t")
        image_name, wnid = fields[0], fields[1]
        val_annotation[image_name] = wnid

    val_paths = sorted((val_root / "images").glob("*.JPEG"))

    val_samples = []
    for path in val_paths:
        wnid = val_annotation[path.name]
        label = class_to_idx[wnid]
        val_samples.append((path.relative_to(data_root), label))

    # 官方测试集没有标签。
    test_paths = [
        path.relative_to(data_root)
        for path in sorted((test_root / "images").glob("*.JPEG"))
    ]

    return train_samples, val_samples, test_paths


def build_transforms():
    """创建训练增强和确定性评估 Transform。"""

    train_transform = transforms.Compose([
        transforms.RandomCrop(
            size=IMAGE_SIZE,
            padding=4,
            padding_mode="reflect",
        ),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ToTensor(),
        transforms.Normalize(mean=TRAIN_MEAN, std=TRAIN_STD),
    ])

    eval_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=TRAIN_MEAN, std=TRAIN_STD),
    ])

    return train_transform, eval_transform


class ImageClassificationDataset(Dataset):
    """把 (相对路径, 整数标签) 清单映射成 (Tensor, 标量标签)。"""

    def __init__(self, samples, data_root, transform):
        self.samples = samples
        self.data_root = data_root
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        relative_path, label = self.samples[index]
        image_path = self.data_root / relative_path

        if not image_path.is_file():
            raise FileNotFoundError(f"找不到图片：{image_path}")

        with Image.open(image_path) as image:
            # 数据集中包含 RGB 和灰度 JPEG，统一转换成三个通道。
            image = image.convert("RGB")
            image = self.transform(image)  # [64,64,3] -> [3,64,64]

        target = torch.tensor(label, dtype=torch.long)
        return image, target


class ImageTestDataset(Dataset):
    """测试集没有标签，因此返回 (图像 Tensor, 相对路径)。"""

    def __init__(self, paths, data_root, transform):
        self.paths = paths
        self.data_root = data_root
        self.transform = transform

        if len(self.paths) == 0:
            raise ValueError("paths 不能为空。")

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, index):
        relative_path = self.paths[index]
        image_path = self.data_root / relative_path

        if not image_path.is_file():
            raise FileNotFoundError(f"找不到图片：{image_path}")

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = self.transform(image)

        return image, str(relative_path)


def select_balanced_subset(samples, train_per_class):
    """每个类别只保留前 train_per_class 张图片。"""

    class_counts = {}
    selected_samples = []

    for sample in samples:
        label = sample[1]
        count = class_counts.get(label, 0)

        if count < train_per_class:
            selected_samples.append(sample)
            class_counts[label] = count + 1

    return selected_samples


def build_dataloaders(
    train_samples,
    val_samples,
    test_paths,
    *,
    data_root=DATA_ROOT,
    train_transform,
    eval_transform,
    train_batch_size=TRAIN_BATCH_SIZE,
    eval_batch_size=EVAL_BATCH_SIZE,
    num_workers=NUM_WORKERS,
):
    """根据三份清单创建 train/val/test DataLoader。"""

    train_dataset = ImageClassificationDataset(
        samples=train_samples,
        data_root=data_root,
        transform=train_transform,
    )
    val_dataset = ImageClassificationDataset(
        samples=val_samples,
        data_root=data_root,
        transform=eval_transform,
    )
    test_dataset = ImageTestDataset(
        paths=test_paths,
        data_root=data_root,
        transform=eval_transform,
    )

    common_loader_args = {
        "num_workers": num_workers,
        "pin_memory": torch.cuda.is_available(),
        "persistent_workers": num_workers > 0,
    }

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=train_batch_size,
        shuffle=True,
        drop_last=False,
        **common_loader_args,
    )
    val_loader = DataLoader(
        dataset=val_dataset,
        batch_size=eval_batch_size,
        shuffle=False,
        drop_last=False,
        **common_loader_args,
    )
    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=eval_batch_size,
        shuffle=False,
        drop_last=False,
        **common_loader_args,
    )

    return train_loader, val_loader, test_loader
