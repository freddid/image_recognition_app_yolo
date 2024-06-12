from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Загрузка модели YOLOv3
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[int(i) - 1] for i in net.getUnconnectedOutLayers()]

# Функция для обработки изображения с помощью YOLOv3
def process_image(image):
    height, width, channels = image.shape
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"{classes[class_id]}: {confidence:.2f}"
                cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = "static/" + file.filename
        file.save(file_path)
        image = cv2.imread(file_path)
        result_image = process_image(image)
        result_image_path = "static/result.jpg"
        cv2.imwrite(result_image_path, result_image)
        return render_template('result.html', user_image=result_image_path)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    data = request.json['image']
    image_data = base64.b64decode(data.split(',')[1])
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    result_image = process_image(image)
    _, buffer = cv2.imencode('.jpg', result_image)
    result_image_str = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'image': f"data:image/jpeg;base64,{result_image_str}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
