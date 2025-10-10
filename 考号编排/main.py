"""
Created on 2024/10/12 下午2:04 
Author: Shuijing
Description: 
"""
import json
from pprint import pprint

# 打开并读取 txt files
file_path = 'students.txt'

# 定义一个空字典来存储班级和学生
students_by_class = {}

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # 按照空格分割行，分成班级和学生信息
        class_id_str, student_id = line.strip().split()

        # 将班级编号转换为 int
        class_id = int(class_id_str)

        # 将学生信息添加到对应的班级
        if class_id not in students_by_class:
            students_by_class[class_id] = []

        students_by_class[class_id].append(student_id)

# 输出结果
pprint(students_by_class)

# 找到最大班级编号
max_class = max(students_by_class.keys())

# 结果列表
result = []

# 当前需要处理的索引
index = 0

# 标记是否还有学生未轮完
has_more_students = True

# 循环提取数据
while has_more_students:
    has_more_students = False  # 默认假设所有班级学生都轮完了

    for class_id in range(1, max_class + 1):
        if class_id in students_by_class and index < len(students_by_class[class_id]):
            # 如果该班级还有学生，则取出第 index 个学生
            result.append(students_by_class[class_id][index])
            has_more_students = True  # 说明还有班级有学生

    # 处理完一轮后，增加 index
    index += 1

# 将结果写入 学籍卡id.txt files
with open('out.txt', 'w', encoding='utf-8') as file:
    for student_id in result:
        file.write(student_id + '\n')

print("数据已写入 学籍卡id.txt files")
