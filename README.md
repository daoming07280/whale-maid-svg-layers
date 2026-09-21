# 鲸鱼女仆：SVG 重绘与拆分素材

蓝色大肥鲸女仆角色的矢量重绘与 Live2D 向分层素材包。

## 效果一览

| 提示词配套参考图（输入） | SVG 重绘结果（输出） |
|:---:|:---:|
| ![prompt reference](prompt-reference.png) | ![SVG preview](whale-maid.png) |
| `prompt-reference.png` | `whale-maid.svg` / `whale-maid.png` |

矢量对照与部件总览：

| 参考 vs 矢量 | 部件接触表 |
|:---:|:---:|
| ![comparison](comparison.png) | ![parts](parts-contact-sheet.png) |

> 完整矢量文件：[`whale-maid.svg`](whale-maid.svg)（59 个命名部件组，Inkscape 图层；约 41MB，浏览器直接打开可能较慢，建议下载后用 Inkscape / Illustrator 查看）。
> 独立部件 SVG 见 [`parts/svg/`](parts/svg/)。

## 生成与目标

- **生成模型**：GPT-6-Astra
- **生成提示词**：`我给你这张图片，请你重新绘制一张svg+拆分。`
- **提示词配套参考图**：[`prompt-reference.png`](prompt-reference.png)（上表左侧，本次重绘所依据的角色图）
- **高分辨率参考**：[`reference.png`](reference.png)（1229×1536，管线中用于描摹与校验）
- **管线目标**：将分层 PSD / SVG 通过 **[psd2live](https://github.com/tsunehimatoi/psd2live)** 制作成 Live2D 的 `.cmo3` / `.moc3` 系列文件
- **当前状态**：**SVG 重绘 + 59 层拆分 + psd2live → moc3 系列均已完成**。Live2D 运行时模型见 [`live2d/whale_maid/`](live2d/whale_maid/)。

本稿依据用户提供的角色参考图制作。身体、头发与服装采用轮廓、色块转路径及部件边界划分；脸底、眼白、眉毛和嘴部另用原生曲线与渐变重画，使脸底不携带原先被遮挡位置的眉眼和发边。尽量保留原图比例、表情、色彩与装饰，但部分光影和线条会有所简化。SVG 中不嵌入位图。为保留原图细节，路径数量较多，并非极简线稿。

## 关于 psd2live

**psd2live**（[tsunehimatoi/psd2live](https://github.com/tsunehimatoi/psd2live)）是一个开源的 Live2D 自动建模流水线与桌面应用：输入**分层 PSD**，自动完成图层语义识别、连通域双侧拆分、自适应三角网格、九轴面部变形器、头发物理与待机动作，一键导出可在 Cubism Modeler 中继续编辑的 `.cmo3`，以及运行时 `.moc3` 文件族（含 `model3.json` / `physics3.json` / `idle.motion3.json` / 贴图集）。

| 项目 | 说明 |
|---|---|
| 仓库 | https://github.com/tsunehimatoi/psd2live |
| 许可 | GPL-3.0（独立开源项目，与 Live2D Inc. 无隶属关系） |
| 运行环境 | JDK 21+；Windows / Linux / macOS |
| 输入 | 分层 PSD（建议按其语义命名规范：`face` / `eyewhite` / `irides` / `eyelash` / `mouth` / `front hair` / `back hair` / `tail` 等） |
| 输出 | `.cmo3` + `.moc3` + `.model3.json` + `.physics3.json` + `.idle.motion3.json` + 纹理集 |
| GUI | Windows 下运行 `run-gui.bat`；`Ctrl+O` 打开 PSD → `Ctrl+R` 分析 → `Ctrl+G` 生成导出 |
| CLI 示例 | `gradlew -p ./psd2live run --args="--input sample.psd --output ./out --atlas 4096 --mesh-spacing 48"` |

### 本仓库与 psd2live 的衔接

完整链路已在本机跑通，**moc3 系列已收入本仓库**：

```text
prompt-reference.png / reference.png
        │  GPT-6-Astra 提示词：重绘 SVG + 拆分
        ▼
whale-maid.svg  +  parts/svg/*  +  parts/png/*
        │  栅格化 / 图层语义映射（去编号 → psd2live 层名）
        ▼
whale-maid-layered.psd  →  live2d/whale_maid/source_psd.psd
        │  psd2live 导出（2026-09-18）
        ▼
live2d/whale_maid/whale-maid-live2d.moc3  +  .cmo3  +  physics/motion/贴图
```

原始 59 层名带编号（如 `39 face`），直接喂 psd2live 会失败；导出前做了语义映射（`face` / `mouth` / `front hair` / `back hair` / `handwear` 等），映射后的 PSD 为 `live2d/whale_maid/source_psd.psd`。VTS 结构检查：EyeBlink / LipSync 齐全。

相关流水线实验记录见：[daoming07280/live2d-auto-pipeline](https://github.com/daoming07280/live2d-auto-pipeline)。

## Live2D 模型包（psd2live 导出）

目录：[`live2d/whale_maid/`](live2d/whale_maid/)

| 文件 | 说明 |
|---|---|
| **`whale-maid-live2d.moc3`** | 运行时模型（约 5.0 MB） |
| `whale-maid-live2d.cmo3` | Cubism Modeler 可编辑工程（约 10.2 MB） |
| `whale-maid-live2d.model3.json` | 加载清单 |
| `whale-maid-live2d.physics3.json` | 物理（发 / 眼等） |
| `whale-maid-live2d.cdi3.json` | 显示名称元数据 |
| `idle / blink / nod / shake.motion3.json` | 待机、眨眼、点头、摇头 |
| `whale-maid-live2d.4096/texture_00–09.png` | 10 张 4096 贴图集 |
| `whale-maid-live2d.psd2live.json` | 诊断与映射元数据 |
| `source_psd.psd` | 语义映射后的 Live2D 输入 PSD |
| `original_layered.psd` | 原始 59 层 PSD 备份 |
| `source_preview.png` | 导出时的源预览 |

### 在 VTube Studio 中使用

将整个 `live2d/whale_maid/` 文件夹拷入：

```text
VTube Studio/VTube Studio_Data/StreamingAssets/Live2DModels/
```

即可在 VTS 中加载。自动绑骨为初版；闭眼、口型、大角度转头仍建议用 Cubism 打开 `.cmo3` 精修。

## 文件

| 文件 | 用途 |
|---|---|
| `whale-maid.svg` | **完整角色 SVG**，59 个命名部件组，支持 Inkscape 图层 |
| `whale-maid.png` | 透明底合成图（SVG 渲染预览） |
| `whale-maid-layered.psd` | 59 层栅格绘图素材，保留层序和位置（psd2live 原始输入） |
| `live2d/whale_maid/` | **psd2live 导出的 moc3 系列**（运行时 + cmo3 + 贴图 + 动作） |
| `parts/svg/` | 59 个独立部件 SVG |
| `parts/png/` | 59 个独立透明部件 PNG |
| `prompt-reference.png` | **提示词配套参考图**（GPT-6-Astra 输入侧） |
| `reference.png` | 高分辨率重绘参考（1229×1536） |
| `comparison.png` | 参考图与矢量结果并排对照 |
| `parts-contact-sheet.png` | 部件放大总览；展示时缩放，实际文件保持对齐 |
| `manifest.json` | 每层中文说明、文件名、顺序、边界及补绘面积 |
| `validation.json` | 画布、层数、路径数与校验误差 |
| `build/` | 从参考图到分层 SVG/PSD 的复现脚本 |

## 坐标与拆分

- 整图、独立 SVG 和 PNG 均为 **1229 × 1536**，左上角为原点。导入时保持原位置，不按内容居中。
- 文件名前缀从底层到顶层递增。PSD 层边界按内容裁切，但保留原画布坐标偏移。
- `r` 为角色右侧，即画面左侧；`l` 反之。
- 头部包括：脸底、左右眼白、左右虹膜、左右上睫毛、眉毛、张口、刘海、侧卷发、后发、呆毛、鳍耳、头饰与发侧蝴蝶结。
- 身体包括：脖颈、上衣底、胸前衬衣与花边、领结和宝石、蓬袖、小臂袖、袖边、手、手腕花边、腰封、裙身与裙摆花边、围裙、鲸鱼图案、裙饰、腿、袜口、袜饰、鞋及鲸尾。

## 遮挡补绘

脸底、眼白、后发、侧发根、身体衣料、围裙底、脖颈、手腕、腿和尾根有推测的补绘余量。`*-visible` 为可见部分的描摹，`*-reconstructed` 为遮挡区域补绘，`*-redrawn` 为重新绘制的完整五官或脸底，可分别编辑。

补绘范围限制在中立姿势被其他部件遮挡的区域，避免改变合成外观。隐藏区域没有真实参考，因此主要用于后续小幅调整和建模起稿；大角度转头、转身以及大幅摆动需要继续补绘和检查接缝。

## Live2D 接续工作

**psd2live 自动导出已完成**，运行时模型与 `.cmo3` 工程在 [`live2d/whale_maid/`](live2d/whale_maid/)。自动绑骨为初版：已含 EyeBlink / LipSync 结构、物理与 idle/blink/nod/shake 动作；闭眼差分、自然口型与大角度转头仍可能需要在 Cubism Modeler 打开 `.cmo3` 精修。

精修建议顺序：

1. 用 Cubism 打开 `live2d/whale_maid/whale-maid-live2d.cmo3`，检查层序与遮挡
2. 核对参数：眼部开合与视线 → 头部小幅转向 → 呼吸 → 头发、鳍耳与鲸尾物理
3. 小角度验证补绘边缘后，再扩大动作范围
4. 如需重跑自动导出：用 `source_psd.psd`（语义层名）再喂 psd2live；原始编号层为 `original_layered.psd` / 仓库根目录 `whale-maid-layered.psd`

## 复现

Python 依赖：Pillow、NumPy、SciPy、vtracer、psd-tools；Node 依赖：sharp。脚本保留在 `build/` 中。将脚本放到素材根目录后依次运行 `prepare.py`、`masks.cjs`、`partition.py`、`build-vectors.py`、`apply-native-face.py`、`render.cjs`、`package-assets.py`。临时 `work/` 与 `masks/` 不列入交付包。
