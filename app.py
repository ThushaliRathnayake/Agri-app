from flask import Flask, render_template, request
from keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import tensorflow as tf
import cv2

app= Flask(__name__)

dic = {'Apple___Apple_scab': 0, 'Apple___Black_rot': 1, 'Apple___Cedar_apple_rust': 2, 'Apple___healthy': 3, 'Blueberry___healthy': 4, 'Cherry_(including_sour)___Powdery_mildew': 5, 'Cherry_(including_sour)___healthy': 6, 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 7, 'Corn_(maize)___Common_rust_': 8, 'Corn_(maize)___Northern_Leaf_Blight': 9, 'Corn_(maize)___healthy': 10, 'Grape___Black_rot': 11, 'Grape___Esca_(Black_Measles)': 12, 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 13, 'Grape___healthy': 14, 'Orange___Haunglongbing_(Citrus_greening)': 15, 'Peach___Bacterial_spot': 16, 'Peach___healthy': 17, 'Pepper,_bell___Bacterial_spot': 18, 'Pepper,_bell___healthy': 19, 'Potato___Early_blight': 20, 'Potato___Late_blight': 21, 'Potato___healthy': 22, 'Raspberry___healthy': 23, 'Soybean___healthy': 24, 'Squash___Powdery_mildew': 25, 'Strawberry___Leaf_scorch': 26, 'Strawberry___healthy': 27, 'Tomato___Bacterial_spot': 28, 'Tomato___Early_blight': 29, 'Tomato___Late_blight': 30, 'Tomato___Leaf_Mold': 31, 'Tomato___Septoria_leaf_spot': 32, 'Tomato___Spider_mites Two-spotted_spider_mite': 33, 'Tomato___Target_Spot': 34, 'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 35, 'Tomato___Tomato_mosaic_virus': 36, 'Tomato___healthy': 37}

model = load_model('train1.h5')

model.make_predict_function()

def predict_label(img_path):
    #i = cv2.imread(img_path)
    #i = tf.io.decode_jpeg(i, channels=3)
    #i = cv2.resize(i,(224,224))
    #i = i/225.0
    i = image.load_img(img_path,target_size=(224,224))
    i = image.img_to_array(i)/225.0
    i = i.reshape(1,224,224,3)
    p = model.predict(i)
    no = max(p[0])
    indx = list(p[0]).index(no) 
    result= dict((new_val,new_k) for new_k,new_val in dic.items()).get(indx)
    return result

#routes

@app.route("/", methods=['GET','POST'])
def main():
    return render_template("index.html")

@app.route("/submit",methods=['GET','POST'])
def get_pred():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = 'static/'+img.filename
        img.save(img_path)
        p = predict_label(img_path)

    return render_template("index.html", prediction = p , img_path=img_path)

if __name__ == '__main__':
    app.run(debug = True)


