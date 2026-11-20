import torch
from torch import nn


class BasicBlock(nn.Module):

    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        # stride=1：保持空间尺寸。
        # stride=2：空间尺寸减半，通常只出现在每个 Stage 的第一个 Block。
        if stride not in (1, 2):
            raise ValueError(f"stride 必须是 1 或 2，当前为 {stride}")

        # 输入： [B, in_channels, H, W]
        # stride=1 输出：[B, out_channels, H, W]
        # stride=2 输出：[B, out_channels, H/2, W/2]
        self.conv1 = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        # 主分支第二层卷积不再改变空间尺寸和通道数。
        self.conv2 = nn.Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 通道数或空间尺寸改变时，旁路需要做线性投影。
        need_projection = stride == 2 or in_channels != out_channels
        if need_projection:
            self.downsample = nn.Sequential(
                nn.Conv2d(
                    in_channels,
                    out_channels,
                    kernel_size=1,
                    stride=stride,
                    padding=0,
                    bias=False,
                ),
                nn.BatchNorm2d(out_channels),
            )
        else:
            self.downsample = nn.Identity()

        # 零初始化残差分支最后一个 BN，使残差块初始时接近恒等映射。
        nn.init.zeros_(self.bn2.weight)
        nn.init.zeros_(self.bn2.bias)

    def forward(self, x):
        # 主分支和旁路最终都必须具有 [B, C, H, W] 形状。
        identity = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out += identity
        out = self.relu(out)
        return out


def make_stage(
    in_channels,
    out_channels,
    num_blocks,
    first_stride,
):
    """用多个 BasicBlock 构建一个 ResNet Stage。"""

    if num_blocks < 1:
        raise ValueError("num_blocks 必须至少为 1")

    if first_stride not in (1, 2):
        raise ValueError("first_stride 必须是 1 或 2")

    blocks = []

    # 第一个 Block 负责通道变化和空间降采样。
    blocks.append(
        BasicBlock(
            in_channels=in_channels,
            out_channels=out_channels,
            stride=first_stride,
        )
    )

    # 后续 Block 保持 Stage 内部的形状不变。
    for _ in range(1, num_blocks):
        blocks.append(
            BasicBlock(
                in_channels=out_channels,
                out_channels=out_channels,
                stride=1,
            )
        )

    return nn.Sequential(*blocks)


class ResNetTiny(nn.Module):
    """面向 64x64 Tiny ImageNet 的 ResNet-18 网络。"""

    def __init__(self, num_classes=200):
        super().__init__()

        # Stem 不降低空间分辨率：
        # [B,3,64,64] -> [B,64,64,64]
        self.stem = nn.Sequential(
            nn.Conv2d(
                in_channels=3,
                out_channels=64,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=64),
            nn.ReLU(inplace=True),
        )

        for module in self.stem.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(
                    module.weight,
                    mode="fan_out",
                    nonlinearity="relu",
                )

        self.stage_1 = make_stage(
            in_channels=64,
            out_channels=64,
            num_blocks=2,
            first_stride=1,
        )
        self.stage_2 = make_stage(
            in_channels=64,
            out_channels=128,
            num_blocks=2,
            first_stride=2,
        )
        self.stage_3 = make_stage(
            in_channels=128,
            out_channels=256,
            num_blocks=2,
            first_stride=2,
        )
        self.stage_4 = make_stage(
            in_channels=256,
            out_channels=512,
            num_blocks=2,
            first_stride=2,
        )

        self.pool = nn.AdaptiveAvgPool2d(output_size=1)
        self.fc = nn.Linear(in_features=512, out_features=num_classes)

    def forward(self, x):
        # x: [B, 3, 64, 64]
        x = self.stem(x)       # [B, 64, 64, 64]
        x = self.stage_1(x)    # [B, 64, 64, 64]
        x = self.stage_2(x)    # [B, 128, 32, 32]
        x = self.stage_3(x)    # [B, 256, 16, 16]
        x = self.stage_4(x)    # [B, 512, 8, 8]
        x = self.pool(x)       # [B, 512, 1, 1]

        x = torch.flatten(x, start_dim=1)  # [B, 512]
        logits = self.fc(x)                # [B, 200]
        return logits
