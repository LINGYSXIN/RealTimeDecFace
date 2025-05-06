import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsScene,QGraphicsPixmapItem
from Ui_interface import Ui_Form
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import face_recognition


class Manitor(QWidget, Ui_Form):
    def __init__(self):
        super(Manitor, self).__init__()
        self.setupUi(self)
        self.show()
        
        self.btn_start.clicked.connect(self.start)
        self.btn_quit.clicked.connect(self.quit) 
    
    
        self.frame_scene = QGraphicsScene()
        self.graphicsView.setScene(self.frame_scene)
        
    def start(self):
        self.thread_camera = Thread_Camera()
        self.thread_camera.signal_frame.connect(self.frameBackCall) 
        self.thread_camera.start()
        
    def frameBackCall(self, frame):
        # print(frame)
        # 将OpenCV图像(BGR格式)转换为Qt可显示的格式
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
    
    def quit(self):
        pass
        
        
class Thread_Camera(QThread):
    
    signal_frame = pyqtSignal(object)
    frame = None
    flag = 0
    def __init__(self):
        super(Thread_Camera, self).__init__()
        self.thread_dec = Thread_Dec()
        self.thread_dec.signal_face.connect(self.backCall)
        self.thread_dec.start()

  
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
            self.thread_dec.frame = frame
            self.signal_frame.emit(frame)
    
        
        cap.release()
    
    def backCall(self, info):
        if info == 1:
            print('有人员信息')
            cv2.imwrite('{}.jpg'.format(self.flag), self.thread_dec.frame)
            self.flag += 1
    
class Thread_Dec(QThread):
    signal_face = pyqtSignal(int)
    frame: list | None = None
    def __init__(self):
        super(Thread_Dec, self).__init__()

    def run(self):
        while True:
            if self.frame is None:
                continue
            else:
                result = face_recognition.face_locations(self.frame)
                if result != []:
                    self.signal_face.emit(1)
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manitor = Manitor()
    sys.exit(app.exec_())