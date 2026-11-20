from pathlib import Path


# 项目目录就是本文件所在目录，避免把电脑上的绝对路径写死在代码里。
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_ROOT = PROJECT_ROOT / "Tiny_Images" / "tiny-imagenet-200"

IMAGE_SIZE = 64

# 快速训练配置，与 ResNet_18.ipynb 保持一致。
SEED = 42
EPOCHS = 3
TRAIN_PER_CLASS = 100
TRAIN_BATCH_SIZE = 64
EVAL_BATCH_SIZE = 256
NUM_WORKERS = 0

LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.05
LABEL_SMOOTHING = 0.1

NUM_CLASSES = 200

RUN_DIR = PROJECT_ROOT / "runs" / "resnet18_py"
BEST_MODEL_PATH = RUN_DIR / "best.pth"
