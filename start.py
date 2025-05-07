import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsScene,QGraphicsPixmapItem
from Ui_interface import Ui_Form
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import face_recognition

class Manitor(QWidget, Ui_Form):
    originFrame = None
    def __init__(self):
        super(Manitor, self).__init__()
        self.setupUi(self)
        self.show()
        
        self.btn_start.clicked.connect(self.start)
        self.btn_quit.clicked.connect(self.quit) 
    
    
        self.frame_scene = QGraphicsScene()
        self.graphicsView.setScene(self.frame_scene)
        self.thread_dec = Thread_Dec()
        self.thread_dec.signal_frame_people.connect(self.decBackCall)
        self.thread_dec.signal_frame_peoPle_num.connect(self.decNum)
        self.thread_dec.start()
        self.original_pos = self.pos()  # 保存初始位置
        self.is_topmost = False  # 初始状态非置顶
        
    def start(self):
        self.thread_camera = Thread_Camera()
        self.thread_camera.signal_frame.connect(self.frameBackCall) 
        self.thread_camera.start()
        
    def frameBackCall(self, frame):
        self.thread_dec.frame = frame 
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # 创建QPixmap并显示
        pixmap = QPixmap.fromImage(q_image)
        
        # 清除场景并添加新的图像项
        self.frame_scene.clear()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.frame_scene.addItem(pixmap_item)
        
        # 自动调整视图大小以适应图像
        self.graphicsView.fitInView(pixmap_item, Qt.KeepAspectRatio)
    
        
        
    def decBackCall(self, decFrame):
         # 将OpenCV图像(BGR格式)转换为Qt可显示的格式
        pass

    def decNum(self, info):
        if info > 0:
            print('有人员信息')
            self.shake()
            self.toggle_topmost()
        
    
    
    def quit(self):
        pass
    def shake(self):
        """快速左右移动窗口3次"""
        for i in range(0, 2):
            # 向右移动
            QTimer.singleShot(100 * i, lambda: self.move(self.original_pos.x() + 10, self.original_pos.y()))
            # 向左移动
            QTimer.singleShot(100 * i + 50, lambda: self.move(self.original_pos.x() - 10, self.original_pos.y()))
        # 恢复原位
        QTimer.singleShot(350, lambda: self.move(self.original_pos))
        
    
    def toggle_topmost(self):
        """切换置顶状态"""
        self.is_topmost = not self.is_topmost
        # 关键代码：设置窗口置顶标志
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_topmost)
        self.show()  # 必须重新调用show()生效
        
class Thread_Camera(QThread):
    
    signal_frame = pyqtSignal(object)
    frame = None
    flag = 0
    def __init__(self):
        super(Thread_Camera, self).__init__()  
        
    def run(self):
        cap = cv2.VideoCapture("rtsp://admin:hzaub107@192.168.124.8:554/Streaming/Channels/1")
        if not cap.isOpened():
            print('无法打开摄像头')
            return
        while True:  
            ret, frame = cap.read()
            if not ret:
                print('无法获取视频帧')
                break
            self.signal_frame.emit(frame)
        cap.release()
    
    
class Thread_Dec(QThread):
    
    signal_frame_people = pyqtSignal(object)
    signal_frame_peoPle_num = pyqtSignal(int)
    frame = None
    
    def __init__(self):
        super(Thread_Dec, self).__init__()
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
        
    def run(self):
        last_boxes = []
        while True:
            if self.frame is not None:
                boxes, weights = self.hog.detectMultiScale(self.frame, winStride=(8, 8), padding = (4, 4), scale = 1.1, hitThreshold=0.5)
                print('boxes', boxes)
                last_boxes = boxes
                # 在图像上绘制边界框
                for (x, y, w, h) in boxes:
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                self.signal_frame_people.emit(self.frame)
                print('len(boxes)',len(boxes))
                self.signal_frame_peoPle_num.emit(len(boxes))   
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manitor = Manitor()
    sys.exit(app.exec_())