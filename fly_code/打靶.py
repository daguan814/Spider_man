# -*- coding: UTF-8 -*-

from helloFly import fly
from Service.target_paths import get_path_points

# ================= 参数 =================
CHECK_TAG = 83           # 靶标编号

# ================= 初始化 =================
fh = fly()
fh.lockDir(0, 0)

# 等待开始
print("按下k2起飞！")
while not fh.getKeyPress(2):  # 按下 K2 起飞
    fh.sleep(0.01)

fh.xySpeed(0, 65)   # 设置横向移动速度
fh.zSpeed(0, 50)    # 设置飞行速度

fh.ledCtrl(0, 0, [0, 255, 0])  # 绿灯起飞
fh.takeOff(0, 100)

# ================= 获取靶标路径 =================
path_points = get_path_points(CHECK_TAG)

if not path_points:
    print("⚠ 未配置该靶标路径，终止任务")
    fh.ledCtrl(0, 0, [255, 255, 0])  # 黄灯警告
    fh.flyCtrl(0, 0)
    exit()

# ================= 打靶流程 =================
for index, step in enumerate(path_points):
    # 兼容：旧格式(3项) -> 默认 shoot_flag=1
    if len(step) == 3:
        direction, tag_id, rotate_angle = step
        shoot_flag = 1
    else:
        direction, tag_id, rotate_angle, shoot_flag = step

    print(f"[Step {index+1}] dir={direction}, tag={tag_id}, rot={rotate_angle}, shoot={shoot_flag}")

    # 1) 移动并寻找标签（无论是否打靶，都要走到这一步对应的位置）
    fh.moveSearchTag(
        id=0,
        dir=direction,
        distance=50,
        tagID=tag_id
    )

    # 2) 是否打靶：0 直接跳过（不旋转、不发射、不转回）
    if int(shoot_flag) == 0:
        continue

    # 3) 射击前旋转
    if rotate_angle != 0:
        fh.rotation(0, rotate_angle)

    # 4) 发射激光
    fh.shootCtrl(0, 0)
    if CHECK_TAG < 80:
        fh.sleep(5)

    # 5) 转回原方向
    if rotate_angle != 0:
        fh.rotation(0, -rotate_angle)

# ================= 结束 =================
fh.ledCtrl(0, 0, [255, 0, 0])  # 红灯
fh.flyHigh(0, 40)
fh.flyCtrl(0, 0)
