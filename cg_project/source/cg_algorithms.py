#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        length = max(abs(x1 - x0), abs(y1 - y0))
        if length == 0:
            return p_list
        dx = (x1 - x0) / length
        dy = (y1 - y0) / length
        x = x0 + 0.5
        y = y0 + 0.5
        for i in range(1, length + 1):
            result.append([int(x), int(y)])
            x = x + dx
            y = y + dy
    elif algorithm == 'Bresenham':
        x = x0
        y = y0
        dx = abs(x1 - x)
        dy = abs(y1 - y)
        s1 = sign(x1 - x0)
        s2 = sign(y1 - y0)
        if dy > dx:
            tmp = dx
            dx = dy
            dy = tmp
            interchange = 1
        else:
            interchange = 0
        e = 2 * dy - dx
        for i in range(0, dx):
            result.append([int(x), int(y)])
            while e > 0:
                if interchange:
                    x = x + s1
                else:
                    y = y + s2
                e = e - 2 * dx
            if interchange:
                y = y + s2
            else:
                x = x + s1
            e = e + 2 * dy

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]

    rx = abs(x1 - x0) / 2
    ry = abs(y1 - y0) / 2
    cx = abs(x1 + x0) / 2
    cy = abs(y1 + y0) / 2

    rx2 = rx * rx
    ry2 = ry * ry

    x = 0
    y = int(ry + 0.5)

    result = []
    p1 = ry2 - rx2 * ry + rx2 / 4
    while ry2 * x < rx2 * y:
        result.append([int(x), int(y)])
        x = x + 1
        if p1 > 0:
            y = y - 1
            p1 = p1 - 2 * rx2 * y
        p1 = p1 + 2 * ry2 * x + ry2

    p2 = ry2 * ((x + 0.5) ** 2) + rx2 * ((y - 1) ** 2) - rx2 * ry2

    while y >= 0:
        result.append([int(x), int(y)])
        y = y - 1
        if p2 < 0:
            x = x + 1
            p2 = p2 + 2 * ry2 * x
        p2 = p2 - 2 * rx2 * y + rx2

    for i in range(len(result)):
        result.append([-result[i][0], -result[i][1]])
        result.append([-result[i][0], result[i][1]])
        result.append([result[i][0], -result[i][1]])

    for i in range(len(result)):
        result[i][0] = int(result[i][0] + cx)
        result[i][1] = int(result[i][1] + cy)

    return result


def get_st(p_list):
    st = []
    x_list = []
    y_list = []
    for i in p_list:
        x_list.append(i[0])
        y_list.append(i[1])
    dx = max(x_list) - min(x_list)
    dy = max(y_list) - min(y_list)
    du = 0.01 / max(dx, dy)
    st = []
    i = 0
    while i <= 1:
        st.append(i)
        i = i + du
    return st


def bezier(p_list):
    result = []
    tmp_point = []
    length = len(p_list)
    for u in get_st(p_list):
        for i in p_list:
            tmp_point.append([i[0], i[1]])

        for i in range(length):
            for j in range(length - i - 1):
                tmp_point[j][0] = (1 - u)*tmp_point[j][0] + u*tmp_point[j + 1][0]
                tmp_point[j][1] = (1 - u) * tmp_point[j][1] + u * tmp_point[j + 1][1]

        result.append([int(tmp_point[j][0]), int(tmp_point[j][1])])

    return result


def special_div(a, b):
    if a == 0 and b == 0:
        return 0
    else:
        return a/b


def deboox_cox(u, i, k, un):
    if k == 1:
        if un[i] <= u < un[i + 1]:
            return 1
        else:
            return 0
    else:
        c1 = special_div(u-un[i], un[i+k-1]-un[i])
        c2 = special_div(un[i+k]-u, un[i+k]-un[i+1])
        return c1 * deboox_cox(u, i, k-1, un) + c2 * deboox_cox(u, i+1, k-1, un)


def b_spline(p_list):
    result = []
    k = 4
    n = len(p_list)
    un = []
    du = 1 / (n+k-1)
    for i in range(n+k):
        un.append(du * i)

    du = 0.001
    u = un[k-1]
    while u <= un[n]:
        x, y = 0, 0
        for i in range(n):
            b = deboox_cox(u, i, k, un)
            x += p_list[i][0] * b
            y += p_list[i][1] * b
        result.append([int(x), int(y)])
        u = u+0.001

    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表

    """
    if algorithm == 'Bezier':
        return bezier(p_list)
    else:
        return b_spline(p_list)


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for i in range(len(p_list)):
        result.append([p_list[i][0] + dx, p_list[i][1] + dy])

    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数

    """
    r = math.radians(r)
    cr = math.cos(r)
    sr = math.sin(r)
    result = []

    for i in range(len(p_list)):
        x0, y0 = p_list[i]
        x1 = x + (x0 - x) * cr - (y0 - y) * sr
        y1 = y + (x0 - x) * sr + (y0 - y) * cr
        result.append([int(x1), int(y1)])

    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for i in range(len(p_list)):
        x0, y0 = p_list[i]
        x1 = x0 * s + x * (1 - s)
        y1 = y0 * s + y * (1 - s)
        result.append([int(x1), int(y1)])

    return result


def get_pos_code(x, y, x_min, x_max, y_min, y_max):
    pos = 0
    pos = pos + (1 if x < x_min else 0)
    pos = pos + (2 if x > x_max else 0)
    pos = pos + (4 if y < y_min else 0)
    pos = pos + (8 if y > y_max else 0)
    return pos


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm == 'Cohen-Sutherland':
        while 1:
            pos0 = get_pos_code(x0, y0, x_min, x_max, y_min, y_max)
            pos1 = get_pos_code(x1, y1, x_min, x_max, y_min, y_max)
            if pos0 | pos1 == 0:
                return [[x0, y0], [x1, y1]]
            elif pos0 & pos1 != 0 or pos0 == pos1:
                return [[0, 0], [0, 0]]
            else:
                if pos0 == 0:
                    x0, x1 = x1, x0
                    y0, y1 = y1, y0
                if pos0 & 1:
                    y0 = int(y0 + ((x_min - x0) * (y0-y1)/(x0-x1)) + 0.5)
                    x0 = x_min
                if pos0 & 2:
                    y0 = int(y0 + ((x_max - x0) * (y0-y1)/(x0-x1)) + 0.5)
                    x0 = x_max
                if pos0 & 4:
                    x0 = int(x0 + ((y_min - y0) * (x0-x1)/(y0-y1)) + 0.5)
                    y0 = y_min
                if pos0 & 8:
                    x0 = int(x0 + ((y_max - y0) * (x0-x1)/(y0-y1)) + 0.5)
                    y0 = y_max

    else:
        dx = x1 - x0
        dy = y1 - y0
        u0 = 0
        u1 = 1
        p = [-dx, dx, -dy, dy]
        q = [x0-x_min, x_max-x0, y0-y_min, y_max-y0]
        for i in range(4):
            if u0 > u1:
                return [[0, 0], [0, 0]]
            else:
                if p[i] < 0:
                    u0 = max(q[i]/p[i], u0)
                elif p[i] > 0:
                    u1 = min(q[i]/p[i], u1)
                elif q[i] < 0:
                    return [[0, 0], [0, 0]]
        return [[int(x0+u0*dx+0.5), int(y0+u0*dy+0.5)], [int(x0+u1*dx+0.5), int(y0+u1*dy+0.5)]]


def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1
