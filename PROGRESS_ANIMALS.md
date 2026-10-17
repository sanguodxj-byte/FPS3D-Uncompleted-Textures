# FPS3D 动物 3D 建模进度看板

> 统计基准：RimWorld 1.7 本体及全 DLC 的 Race 定义（**含机械族与无人机**，仅排除人形与无贴图的伪装实体）。
> 已建模判定：FirstPerson3D 仓库 `viewer/animal_parts_cs.json` 中存在对应物种键。

## 进度概览

- **生物定义总数**：`161` 种（本体 + 全 DLC，含机械族/无人机，排除人形）
- **已建模**：`119` 种（全部为野生/家畜动物，机械族尚未建模）
- **待建模**：`42` 种（本仓库范围）
- **待建模贴图**：`118` 张（扁平存放于根目录，`Animal_*.png`）
- **可立即开工**：`41` 种（三视图齐备）
- **暂缓**：`1` 种（无独立贴图）

| 指标 | 数值 | 覆盖率 |
|---|---|---|
| 生物建模覆盖 | 119 / 161 | 73.9% |
| 待建贴图到位 | 41 / 42 | 97.6% |

## 按 DLC 分布

| DLC | 待建模数 | 三视图齐备 | 暂缓 |
|---|---|---|---|
| Core | 4 | 4 | 0 |
| Biotech | 16 | 16 | 0 |
| Anomaly | 15 | 14 | 1 |
| Odyssey | 7 | 7 | 0 |

## 建模批次

### 机械族（硬边块体）

- **ANIM_BATCH_01**（Biotech，8 种）：园艺机（Mech_Agrihand）、憎恶毒蜂（Mech_Apocriton）、百机长（Mech_Centurion）、清洁机（Mech_Cleansweeper）、建造机（Mech_Constructoid）、炼狱魔王（Mech_Diabolus）、工艺机（Mech_Fabricor）、机械盾卫（Mech_Legionary）
- **ANIM_BATCH_02**（Biotech，8 种）：搬运机（Mech_Lifter）、机械辅兵（Mech_Militor）、救护机（Mech_Paramedic）、机械炽蚕（Mech_Scorcher）、机械哨卫（Mech_Tesseron）、重型机械族（动力爪）（Mech_Tunneler）、战争爪牙（Mech_WarUrchin）、战争女皇（Mech_Warqueen）
- **ANIM_BATCH_03**（Core，8 种）：机械静螳（Mech_Lancer）、机械蝎蝽（Mech_Pikeman）、机械飞螳（Mech_Scyther）、机械白蚁（Mech_Termite）、猎手无人机（Drone_Hunter）、哨兵无人机（Drone_Sentry）、胡蜂无人机（Drone_Wasp）、机械炬瞳（Mech_Cyclops）

### 有机形体（椭球分段）

- **ANIM_BATCH_04**（Anomaly，8 种）：恶臭瘤兽（Bulbfreak）、嵌合兽（Chimera）、吞噬兽（Devourer）、惊惧母兽（Dreadmeld）、独爪兽（Fingerspike）、血肉核心（FleshmassNucleus）、血棘巨人（Gorehulk）、金属怪形（Metalhorror）
- **ANIM_BATCH_05**（Anomaly，6 种）：苦痛之球（Nociosphere）、夜魇（Noctol）、幽魂（Revenant）、隐形魔（Sightstealer）、双爪兽（Toughspike）、三爪兽（Trispike）
- **ANIM_BATCH_06**（Odyssey，3 种）：虫后（HiveQueen）、幼虫（Larva）、蝗虫（Locust）

- **ANIM_BATCH_07**（暂缓，1 种）：爬行者（伪装人形，无独立贴图）（CreepJoiner）

## 待建模动物清单

| DefName | 中文标签 | 官方DLC | 贴图 | 状态 |
|---|---|---|---|---|
| `Mech_Lancer` | 机械静螳 | Core | `3 张` | 待建 |
| `Mech_Pikeman` | 机械蝎蝽 | Core | `3 张` | 待建 |
| `Mech_Scyther` | 机械飞螳 | Core | `3 张` | 待建 |
| `Mech_Termite` | 机械白蚁 | Core | `3 张` | 待建 |
| `Mech_Agrihand` | 园艺机 | Biotech | `3 张` | 待建 |
| `Mech_Apocriton` | 憎恶毒蜂 | Biotech | `3 张` | 待建 |
| `Mech_Centurion` | 百机长 | Biotech | `3 张` | 待建 |
| `Mech_Cleansweeper` | 清洁机 | Biotech | `3 张` | 待建 |
| `Mech_Constructoid` | 建造机 | Biotech | `2 张` | 待建 |
| `Mech_Diabolus` | 炼狱魔王 | Biotech | `3 张` | 待建 |
| `Mech_Fabricor` | 工艺机 | Biotech | `3 张` | 待建 |
| `Mech_Legionary` | 机械盾卫 | Biotech | `3 张` | 待建 |
| `Mech_Lifter` | 搬运机 | Biotech | `3 张` | 待建 |
| `Mech_Militor` | 机械辅兵 | Biotech | `3 张` | 待建 |
| `Mech_Paramedic` | 救护机 | Biotech | `3 张` | 待建 |
| `Mech_Scorcher` | 机械炽蚕 | Biotech | `3 张` | 待建 |
| `Mech_Tesseron` | 机械哨卫 | Biotech | `3 张` | 待建 |
| `Mech_Tunneler` | 重型机械族（动力爪） | Biotech | `3 张` | 待建 |
| `Mech_WarUrchin` | 战争爪牙 | Biotech | `3 张` | 待建 |
| `Mech_Warqueen` | 战争女皇 | Biotech | `3 张` | 待建 |
| `Bulbfreak` | 恶臭瘤兽 | Anomaly | `3 张` | 待建 |
| `Chimera` | 嵌合兽 | Anomaly | `3 张` | 待建 |
| `CreepJoiner` | 爬行者（伪装人形，无独立贴图） | Anomaly | — | 暂缓（无独立贴图） |
| `Devourer` | 吞噬兽 | Anomaly | `3 张` | 待建 |
| `Dreadmeld` | 惊惧母兽 | Anomaly | `3 张` | 待建 |
| `Fingerspike` | 独爪兽 | Anomaly | `3 张` | 待建 |
| `FleshmassNucleus` | 血肉核心 | Anomaly | `1 张` | 待建 |
| `Gorehulk` | 血棘巨人 | Anomaly | `3 张` | 待建 |
| `Metalhorror` | 金属怪形 | Anomaly | `3 张` | 待建 |
| `Nociosphere` | 苦痛之球 | Anomaly | `1 张` | 待建 |
| `Noctol` | 夜魇 | Anomaly | `3 张` | 待建 |
| `Revenant` | 幽魂 | Anomaly | `3 张` | 待建 |
| `Sightstealer` | 隐形魔 | Anomaly | `3 张` | 待建 |
| `Toughspike` | 双爪兽 | Anomaly | `3 张` | 待建 |
| `Trispike` | 三爪兽 | Anomaly | `3 张` | 待建 |
| `Drone_Hunter` | 猎手无人机 | Odyssey | `3 张` | 待建 |
| `Drone_Sentry` | 哨兵无人机 | Odyssey | `3 张` | 待建 |
| `Drone_Wasp` | 胡蜂无人机 | Odyssey | `3 张` | 待建 |
| `HiveQueen` | 虫后 | Odyssey | `3 张` | 待建 |
| `Larva` | 幼虫 | Odyssey | `3 张` | 待建 |
| `Locust` | 蝗虫 | Odyssey | `3 张` | 待建 |
| `Mech_Cyclops` | 机械炬瞳 | Odyssey | `3 张` | 待建 |

## 交付规范

模型与贴图的交付要求见 `docs/GLB_SPEC.md`，动物模块额外遵守：

- 动物为有机形体，按 `docs/GLB_SPEC.md` C 节用多段椭球拼装，**禁止竖直堆叠成雪人**；
- 侧影必须与 `Animal_<Def>_east.png` 一致，正视宽度对照 `_south.png`；
- 每个物种出 8 方位印相图，与原版三视图对照审核；
- 建模完成后，需同步登记到 FirstPerson3D 仓库的 `Animal3D.cs` 与 `viewer/animal_parts_cs.json`。

