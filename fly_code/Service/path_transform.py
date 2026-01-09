# -*- coding: UTF-8 -*-
"""
路径转换工具（仅用于生成 & 打印）
支持 step 为:
- (dir, p, yaw)
- (dir, p, yaw, shoot_flag)
"""

# =========================================================
# 从 target_paths 导入原始 PATH_MAP（0 起飞）
# =========================================================
from target_paths import PATH_MAP


# =========================================================
# 坐标变换（8x8 网格；每行步长=20，每列步长=1）
# =========================================================
def mirror_point_lr(p: int) -> int:
    """左右镜像：col -> 7-col"""
    row = p // 20
    col = p % 20
    return row * 20 + (7 - col)

def mirror_point_ud(p: int) -> int:
    """上下镜像：row -> 7-row"""
    row = p // 20
    col = p % 20
    return (7 - row) * 20 + col


# =========================================================
# 方向映射
# 1前 2后 3左 4右
# =========================================================
# 左右镜像：左右互换，前后不变
DIR_LR_SWAP = {1: 1, 2: 2, 3: 4, 4: 3}

# 上下镜像：前后互换，左右不变
DIR_UD_SWAP = {1: 2, 2: 1, 3: 3, 4: 4}


# =========================================================
# yaw 变换（度）
# =========================================================
def yaw_lr(yaw: float) -> float:
    """左右镜像：左转<->右转"""
    return -yaw

def yaw_ud(yaw: float) -> float:
    """
    上下镜像：按你给的规则
    - yaw>=0: 180 - yaw
    - yaw<0 : -180 - yaw
    """
    return (180 - yaw) if yaw >= 0 else (-180 - yaw)


# =========================================================
# 路径变换（支持三元组/四元组）
# =========================================================
def transform_step(step, point_func, dir_map, yaw_func):
    """
    step:
      (d, p, yaw) 或 (d, p, yaw, shoot_flag)
    return:
      (new_d, new_p, new_yaw, shoot_flag)
    """
    if len(step) == 3:
        d, p, yaw = step
        shoot_flag = 1
    else:
        d, p, yaw, shoot_flag = step

    new_d = dir_map[d]
    new_p = point_func(p)
    new_yaw = yaw_func(yaw)
    return (new_d, new_p, new_yaw, shoot_flag)

def transform_path(path, point_func, dir_map, yaw_func):
    return [transform_step(step, point_func, dir_map, yaw_func) for step in path]

def transform_path_map(path_map, point_func, dir_map, yaw_func):
    new_map = {}
    for target, path in path_map.items():
        new_target = point_func(target)
        new_map[new_target] = transform_path(path, point_func, dir_map, yaw_func)
    return new_map


# =========================================================
# 可读格式打印（用于粘贴）
# =========================================================
def pretty_print_path_map(path_map, name="PATH_MAP"):
    print(f"{name} = {{")
    for target in sorted(path_map.keys(), reverse=True):
        path = path_map[target]
        print(f"    {target}: [  # 共{len(path)}点")
        for step in path:
            print(f"        {step},")
        print("    ],\n")
    print("}")


# =========================================================
# 主入口
# =========================================================
if __name__ == "__main__":

    # 记录原始已有的 target（你当前 target_paths 里已经有很多）
    original_keys = set(PATH_MAP.keys())

    map_7 = transform_path_map(PATH_MAP, mirror_point_lr, DIR_LR_SWAP, yaw_lr)
    map_140 = transform_path_map(PATH_MAP, mirror_point_ud, DIR_UD_SWAP, yaw_ud)
    map_147 = transform_path_map(map_140, mirror_point_lr, DIR_LR_SWAP, yaw_lr)

    # 只保留“原来没有的 key”（也就是新生成的）
    final_map = {}
    for m in (map_7, map_140, map_147):
        for k, v in m.items():
            if k not in original_keys:
                final_map[k] = v

    pretty_print_path_map(final_map)
