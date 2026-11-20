# ResNet-18 Tiny ImageNet 训练项目

项目代码参考 `ResNet_18.ipynb`，模型、数据处理和快速训练逻辑保持不变。

## 项目结构

```text
ResNet/
├── config.py          # 路径、超参数和输出目录
├── data.py            # 数据清单、Transform、Dataset、DataLoader
├── model.py           # BasicBlock、Stage、ResNetTiny
├── train.py           # 训练、验证、最佳权重保存与加载
├── requirements.txt   # Python 依赖
├── ResNet_18.ipynb    # 原始学习版 notebook
├── Tiny_Images/       # Tiny ImageNet 数据集
└── runs/
    └── resnet18_py/
        └── best.pth   # 训练后生成
```

## 模块职责

```text
config.py
    -> 统一保存路径和超参数

data.py
    -> wnids 类别映射
    -> train/val/test 清单
    -> 图像增强与标准化
    -> Dataset、DataLoader

model.py
    -> BasicBlock
    -> Stage 组合
    -> ResNet-18 (64x64 variant)

train.py
    -> 随机种子和设备
    -> 分层抽取训练子集
    -> 训练循环
    -> 验证
    -> 保存并重新加载 best.pth
```

## 运行

先激活环境：

```powershell
conda activate rookie_env
```

然后在项目目录运行：

```powershell
python train.py
```

也可以不激活环境，直接用 conda 运行：

```powershell
conda run -n rookie_env python train.py
```

## 当前训练配置

```text
训练样本：每类 100 张，共 20,000 张
训练轮数：3
训练 Batch：64
验证 Batch：256
优化器：AdamW
学习率：3e-4
混合精度：CUDA 时自动启用
```

训练结果保存到：

```text
runs/resnet18_py/best.pth
```
