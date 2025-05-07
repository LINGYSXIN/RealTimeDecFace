import cv2
import os
import numpy as np
import time
 
def detect_people():
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # video_path = os.path.join(current_dir, 'walk2.mp4')
    
    # if not os.path.exists(video_path):
    #     print(f"Error: 视频文件不存在，请确认文件路径: {video_path}")
    #     return
    
    # 创建HOG检测器
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: 无法打开视频文件")
        return
 
    # 设置视频捕获的分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 用于控制检测频率
    frame_count = 0
    detection_interval = 3  # 每隔3帧进行一次检测
    last_boxes = []
 
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break
            
        # 降低分辨率
        frame = cv2.resize(frame, (640, 480))
        
        # 每隔几帧进行一次检测
        if frame_count % detection_interval == 0:
            # 检测人
            boxes, weights = hog.detectMultiScale(frame, 
                                                winStride=(8, 8),
                                                padding=(4, 4),
                                                scale=1.1)
            last_boxes = boxes
        else:
            boxes = last_boxes
            
        # 在图像上绘制边界框
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        # 显示人数
        people_count = len(boxes)
        cv2.putText(frame, f'People Count: {people_count}', 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 0), 2)
        
        # 计算和显示FPS
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(frame, f'FPS: {int(fps)}', 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 0), 2)
        
        # 显示结果
        cv2.imshow('People Detection', frame)
        
        frame_count += 1
        
        # 减小等待时间，提高帧率
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
 
if __name__ == '__main__':
    detect_people()