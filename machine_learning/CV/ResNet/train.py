import random

import numpy as np
import torch
from torch import nn

from config import (
    BEST_MODEL_PATH,
    DATA_ROOT,
    EPOCHS,
    EVAL_BATCH_SIZE,
    LABEL_SMOOTHING,
    LEARNING_RATE,
    NUM_CLASSES,
    NUM_WORKERS,
    RUN_DIR,
    SEED,
    TRAIN_BATCH_SIZE,
    TRAIN_PER_CLASS,
    WEIGHT_DECAY,
)
from data import (
    build_dataloaders,
    build_manifests,
    build_transforms,
    select_balanced_subset,
)
from model import ResNetTiny


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def train_one_epoch(
    model,
    loader,
    criterion,
    optimizer,
    scaler,
    device,
    amp_enabled,
):
    model.train()

    total_loss = 0.0
    correct_top1 = 0
    correct_top5 = 0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        # [B, 3, 64, 64] -> [B, 200]
        with torch.amp.autocast(
            device_type="cuda" if amp_enabled else "cpu",
            dtype=torch.float16,
            enabled=amp_enabled,
        ):
            logits = model(images)
            loss = criterion(logits, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        batch_size = labels.size(0)
        top5_predictions = logits.detach().topk(5, dim=1).indices

        total_loss += loss.item() * batch_size
        correct_top1 += (
            logits.detach().argmax(dim=1) == labels
        ).sum().item()
        correct_top5 += top5_predictions.eq(
            labels.unsqueeze(1)
        ).any(dim=1).sum().item()
        total_samples += batch_size

    return {
        "loss": total_loss / total_samples,
        "top1": correct_top1 / total_samples,
        "top5": correct_top5 / total_samples,
    }


@torch.inference_mode()
def evaluate(model, loader, criterion, device, amp_enabled):
    model.eval()

    total_loss = 0.0
    correct_top1 = 0
    correct_top5 = 0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with torch.amp.autocast(
            device_type="cuda" if amp_enabled else "cpu",
            dtype=torch.float16,
            enabled=amp_enabled,
        ):
            logits = model(images)
            loss = criterion(logits, labels)

        batch_size = labels.size(0)
        top5_predictions = logits.topk(5, dim=1).indices

        total_loss += loss.item() * batch_size
        correct_top1 += (
            logits.argmax(dim=1) == labels
        ).sum().item()
        correct_top5 += top5_predictions.eq(
            labels.unsqueeze(1)
        ).any(dim=1).sum().item()
        total_samples += batch_size

    return {
        "loss": total_loss / total_samples,
        "top1": correct_top1 / total_samples,
        "top5": correct_top5 / total_samples,
    }


def main():
    seed_everything(SEED)

    device = select_device()
    amp_enabled = device.type == "cuda"

    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True

    print("device:", device)
    print("amp_enabled:", amp_enabled)

    train_samples, val_samples, test_paths = build_manifests(DATA_ROOT)
    small_train_samples = select_balanced_subset(
        train_samples,
        TRAIN_PER_CLASS,
    )

    train_transform, eval_transform = build_transforms()

    train_loader, val_loader, test_loader = build_dataloaders(
        train_samples=small_train_samples,
        val_samples=val_samples,
        test_paths=test_paths,
        data_root=DATA_ROOT,
        train_transform=train_transform,
        eval_transform=eval_transform,
        train_batch_size=TRAIN_BATCH_SIZE,
        eval_batch_size=EVAL_BATCH_SIZE,
        num_workers=NUM_WORKERS,
    )

    print(f"train samples: {len(train_loader.dataset):,}")
    print(f"train batches: {len(train_loader):,}")
    print(f"validation samples: {len(val_loader.dataset):,}")

    RUN_DIR.mkdir(parents=True, exist_ok=True)

    model = ResNetTiny(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)

    best_val_top1 = -1.0

    for epoch in range(1, EPOCHS + 1):
        train_metrics = train_one_epoch(
            model=model,
            loader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            scaler=scaler,
            device=device,
            amp_enabled=amp_enabled,
        )

        val_metrics = evaluate(
            model=model,
            loader=val_loader,
            criterion=criterion,
            device=device,
            amp_enabled=amp_enabled,
        )

        if val_metrics["top1"] > best_val_top1:
            best_val_top1 = val_metrics["top1"]
            best_state_dict = {
                name: tensor.detach().cpu()
                for name, tensor in model.state_dict().items()
            }
            torch.save(best_state_dict, BEST_MODEL_PATH)

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"train_loss={train_metrics['loss']:.4f} | "
            f"train_top1={train_metrics['top1']:.2%} | "
            f"val_loss={val_metrics['loss']:.4f} | "
            f"val_top1={val_metrics['top1']:.2%} | "
            f"val_top5={val_metrics['top5']:.2%}"
        )

    best_state_dict = torch.load(
        BEST_MODEL_PATH,
        map_location=device,
        weights_only=True,
    )
    model.load_state_dict(best_state_dict)

    print(f"最佳模型已保存并加载：{BEST_MODEL_PATH}")
    print(f"Best validation Top-1: {best_val_top1:.2%}")


if __name__ == "__main__":
    main()
