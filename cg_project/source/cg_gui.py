#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QInputDialog
)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.edit_status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = [0, 0, 0]

    def change_status(self, status):
        if self.temp_item is not None:
            if self.status == 'curve' or self.status == 'polygon':
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
            elif self.status == 'edit':
                self.temp_item.edit_type = ''
        self.status = status

    def start_draw_line(self, algorithm, item_id):
        self.change_status('line')
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.change_status('polygon')
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_ellipse(self, item_id):
        self.change_status('ellipse')
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.change_status('curve')
        self.temp_id = item_id
        self.temp_algorithm = algorithm
        self.temp_item = None

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):

        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].edit_type = ''
        self.selected_id = selected
        self.status = ''
        if selected != '':
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'edit':
            if self.selected_id == '':
                self.status = ''
                self.edit_status = ''
                self.main_window.statusBar().showMessage('请选择图元后，重新编辑')
            else:
                self.temp_item = self.item_dict[self.selected_id]
                if self.edit_status == 'translate' or self.edit_status == 'clip':
                    self.temp_item.edit_list = [[x, y], [x, y]]
                    self.temp_item.edit_type = self.edit_status
                else:
                    self.temp_item.edit_type = ''
                    self.temp_item.edit_list = [[x, y]]
        else:
            if self.status == 'line' or self.status == 'ellipse':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color)
                self.scene().addItem(self.temp_item)
            else:
                if self.temp_item is None:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.color)
                    self.scene().addItem(self.temp_item)
                else:
                    self.temp_item.p_list.append([x, y])

        if self.status != 'edit' or self.edit_status == 'translate':
            self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' or self.status == 'curve':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'edit':
            if self.edit_status == 'translate' or self.edit_status == 'clip':
                self.temp_item.edit_list[1] = [x, y]
            else:
                self.temp_item.edit_list[0] = [x, y]
        if self.status != 'edit' or self.edit_status == 'translate':
            self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        if self.status == 'line' or self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon' or self.status == 'curve':
            x = int(pos.x())
            y = int(pos.y())
            self.temp_item.p_list[-1] = [x, y]
            self.updateScene([self.sceneRect()])
        else:
            if self.edit_status == 'rotate':
                ok = 0
                while not ok:
                    text, ok = QInputDialog.getDouble(self, 'Double Input Dialog', '请输入旋转度数')
                self.temp_item.edit_type = self.edit_status
                self.temp_item.edit_param = text
                self.updateScene([self.sceneRect()])
            elif self.edit_status == 'scale':
                ok = 0
                while not ok:
                    text, ok = QInputDialog.getDouble(self, 'Double Input Dialog', '请输入缩放系数')
                self.temp_item.edit_param = text
                self.temp_item.edit_type = self.edit_status
                self.updateScene([self.sceneRect()])
            elif self.edit_status == 'clip':
                self.temp_item.edit_algorithm = self.temp_algorithm
                self.updateScene([self.sceneRect()])

        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color=None, parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        if color is None:
            color = [0, 0, 0]
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.edit_type = ''
        self.edit_list = []
        self.edit_param = 0
        self.edit_algorithm = ''
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.edit_type == 'translate':
            x0, y0 = self.edit_list[0]
            x1, y1 = self.edit_list[1]
            self.p_list = alg.translate(self.p_list, x1 - x0, y1 - y0)
        elif self.edit_type == 'rotate':
            x0, y0 = self.edit_list[0]
            self.p_list = alg.rotate(self.p_list, x0, y0, self.edit_param)
        elif self.edit_type == 'scale':
            x0, y0 = self.edit_list[0]
            self.p_list = alg.scale(self.p_list, x0, y0, self.edit_param)
        elif self.edit_type == 'clip':
            x0, y0 = self.edit_list[0]
            x1, y1 = self.edit_list[1]
            self.p_list = alg.clip(self.p_list, x0, y0, x1, y1, self.edit_algorithm)

        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            if len(self.p_list) >= 2:
                item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            else:
                item_pixels = []
        else:
            item_pixels = []

        for p in item_pixels:
            painter.setPen(QColor(self.color[0], self.color[1], self.color[2]))
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

        if self.edit_type == 'translate':
            self.edit_list = [[x1, y1], [x1, y1]]

    def boundingRect(self) -> QRectF:
        if self.item_type == 'polygon' or self.item_type == 'curve':
            x_list = []
            y_list = []
            for i in self.p_list:
                x_list.append(i[0])
                y_list.append(i[1])
            x = min(x_list)
            y = min(y_list)
            w = max(x_list) - x
            h = max(y_list) - y
        elif self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
        else:
            x = 1
            y = 1
            w = 0
            h = 0
        return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(602, 602)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        set_pen_act.triggered.connect(self.set_pen_action)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_cat)

        ellipse_act.triggered.connect(self.ellipse_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        ok = 0
        while not ok:
            text, ok = QInputDialog.getInt(self, 'Double Input Int', '请输入R')
        r = text
        ok = 0
        while not ok:
            text, ok = QInputDialog.getInt(self, 'Double Input Int', '请输入G')
        g = text
        ok = 0
        while not ok:
            text, ok = QInputDialog.getInt(self, 'Double Input Int', '请输入B')
        b = text
        self.canvas_widget.color = [r, g, b]

    def reset_canvas_action(self):
        self.scene.clear()
        self.canvas_widget.selection_changed('')
        self.canvas_widget.color = [0, 0, 0]
        self.canvas_widget.status = ''
        self.canvas_widget.temp_item = None
        self.canvas_widget.temp_id = ''
        self.canvas_widget.edit_status = ''
        self.canvas_widget.temp_algorithm = ''
        self.canvas_widget.list_widget.clear()
        self.canvas_widget.item_dict.clear()


    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('Bresenham算法椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_cat(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.change_status('edit')
        self.canvas_widget.edit_status = 'translate'
        self.statusBar().showMessage('平移变换')

    def rotate_action(self):
        self.canvas_widget.change_status('edit')
        self.canvas_widget.edit_status = 'rotate'
        self.statusBar().showMessage('旋转变换,请选择旋转中心')

    def scale_action(self):
        self.canvas_widget.change_status('edit')
        self.canvas_widget.edit_status = 'scale'
        self.statusBar().showMessage('缩放变换,请选择缩放中心')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.change_status('edit')
        self.canvas_widget.edit_status = 'clip'
        self.canvas_widget.temp_algorithm = 'Cohen-Sutherland'
        self.statusBar().showMessage('cohen-sutherland 剪裁变换')

    def clip_liang_barsky_action(self):
        self.canvas_widget.change_status('edit')
        self.canvas_widget.edit_status = 'clip'
        self.canvas_widget.temp_algorithm = 'Liang-Barsky'
        self.statusBar().showMessage('Liang-Barsky 剪裁变换')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
