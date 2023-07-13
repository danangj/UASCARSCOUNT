def frame_detect():
    import cv2
    from datetime import datetime
    import mysql.connector
    from ultralytics import YOLO
    import time

    model_path = 'best.pt'

    # Load a model
    model = YOLO(model_path)  # load a custom model

    threshold = 0.5

    class_name_dict = {0: 'mobil'}

    # camera = 'http://192.168.71.118:4747/video'

    video_path = 'D:\parkirslot\video1.mp4'
    cap = cv2.VideoCapture(video_path) 
    # cap = cv2.VideoCapture(camera)  # use default camera
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    # cv2.namedWindow('Real-time Detection', cv2.WINDOW_NORMAL)

    
    db = mysql.connector.connect(
        host="localhost",  
        user="root",  
        password="",  
        database="uastol2"  
    )

    cursor = db.cursor()

    class_label = ''
    interval = 30
    number = 0
    start_time =time.time()
    current_time = time.time()
    elapsed_time = current_time - start_time  

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        H, W, _ = frame.shape

        results = model(frame)[0]

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
            if score > threshold:
                if class_id == 0:
                    class_label = 'mobil'
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 4)
                    cv2.putText(frame, class_label.upper(), (int(x1), int(y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    
                    # capturing
                    if number == 0:
                        number +=1
                        data = (timestamp, class_label)
                        query = "INSERT INTO data (waktu, kondisi) VALUES (%s, %s)"  

                        cursor.execute(query, data)
                        db.commit()
                        if number >= 1:
                            if elapsed_time >= interval:
                                start_time = time.time()
                                number = 0
                

                    # capturing
                    if number == 0:
                        number +=1
                        data = (timestamp, class_label)
                        query = "INSERT INTO data (waktu, kondisi) VALUES (%s, %s)"  
                        cursor.execute(query, data)
                        db.commit()
                        if number >= 1:
                            if elapsed_time >= interval:
                                start_time = time.time()
                                number = 0

                cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        
        # data = (timestamp, class_label)
        # query = "INSERT INTO data (waktu, kondisi) VALUES (%s, %s)"  

        # cursor.execute(query, data)
        # db.commit()

    #     cv2.imshow('Real-time Detection', frame)

    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cursor.close()
    # db.close()
    # cap.release()
    cv2.destroyAllWindows()
