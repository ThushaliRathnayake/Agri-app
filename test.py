from urllib import response
from flask import Flask, render_template, request, Markup
from keras.models import load_model
from tensorflow.keras.preprocessing import image
from utils.disease import disease_dic
from PIL import Image
import numpy as np
import tensorflow as tf
import cv2
import datetime
import json

from fileinput import filename
from heapq import merge
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate(
    "agri-app1-firebase-adminsdk-li4tm-1313ccb370.json")
farmers = firebase_admin.initialize_app(
    cred, {'storageBucket': 'agri-app1.appspot.com', 'databaseURL': 'https://agri-app1-default-rtdb.firebaseio.com'})

depcred = credentials.Certificate(
    "agri-department1-firebase-adminsdk-r4d7z-f07f65e3b1.json")
department = firebase_admin.initialize_app(depcred, {
                                           'storageBucket': "agri-department1.appspot.com", 'databaseURL': "https://agri-department1-default-rtdb.firebaseio.com"}, name="other")


# import firebase_admin.db
# db = firebase_admin.db.reference(path='/', app=farmers, url="https://agri-app1-default-rtdb.firebaseio.com/")

# db = farmers.db
# from firebase_admin import db
# db = farmers.database('https://secondary_db_url.firebaseio.com')
# firebase_admin.get_app(farmers)
# # db = firebase_admin.db
# storage = farmers.storage

#depdb = firebase_admin.db.reference(path='/', app=department, url="https://agri-app1-default-rtdb.firebaseio.com/")
# depstorage = department.storage


app = Flask(__name__)

dic = {'Apple___Apple_scab': 0, 'Apple___Black_rot': 1, 'Apple___Cedar_apple_rust': 2, 'Apple___healthy': 3, 'Blueberry___healthy': 4, 'Cherry_(including_sour)___Powdery_mildew': 5, 'Cherry_(including_sour)___healthy': 6, 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 7, 'Corn_(maize)___Common_rust_': 8, 'Corn_(maize)___Northern_Leaf_Blight': 9, 'Corn_(maize)___healthy': 10, 'Grape___Black_rot': 11, 'Grape___Esca_(Black_Measles)': 12, 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 13, 'Grape___healthy': 14, 'Orange___Haunglongbing_(Citrus_greening)': 15, 'Peach___Bacterial_spot': 16, 'Peach___healthy': 17,
       'Pepper,_bell___Bacterial_spot': 18, 'Pepper,_bell___healthy': 19, 'Potato___Early_blight': 20, 'Potato___Late_blight': 21, 'Potato___healthy': 22, 'Raspberry___healthy': 23, 'Soybean___healthy': 24, 'Squash___Powdery_mildew': 25, 'Strawberry___Leaf_scorch': 26, 'Strawberry___healthy': 27, 'Tomato___Bacterial_spot': 28, 'Tomato___Early_blight': 29, 'Tomato___Late_blight': 30, 'Tomato___Leaf_Mold': 31, 'Tomato___Septoria_leaf_spot': 32, 'Tomato___Spider_mites Two-spotted_spider_mite': 33, 'Tomato___Target_Spot': 34, 'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 35, 'Tomato___Tomato_mosaic_virus': 36, 'Tomato___healthy': 37}

model = load_model('train1.h5')

model.make_predict_function()


def predict_label(img_path):
    #i = cv2.imread(img_path)
    #i = tf.io.decode_jpeg(i, channels=3)
    #i = cv2.resize(i,(224,224))
    #i = i/225.0
    i = image.load_img(img_path, target_size=(224, 224))
    i = image.img_to_array(i)/225.0
    i = i.reshape(1, 224, 224, 3)
    p = model.predict(i)
    no = max(p[0])
    print(no)
    indx = list(p[0]).index(no)
    result = dict((new_val, new_k) for new_k, new_val in dic.items()).get(indx)
    return result

@app.route('/service', methods=['POST','GET'])
def service():
    return render_template('service.html')

@app.route('/gallery', methods=['POST','GET'])
def gallery():
    return render_template('gallery.html')

@app.route('/contact', methods=['POST','GET'])
def about():
    return render_template('contact.html')

@app.route('/Crop_Disease', methods=['POST','GET'])
def Crop_Disease():
    return render_template('Crop Disease.html')

@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template("index.html")

@app.route("/his", methods=['GET', 'POST'])
def his():
    return render_template("home_p.html")


################################
@app.route("/iquiry", methods=['POST'])
def depi():
    global current_depuser
    current_depuser = request.form.get("depcustId")
    ref_ = db.reference('department_inquiry/' + current_depuser + '/userdetails/username',app=department, url="https://agri-department1-default-rtdb.firebaseio.com/")
    username_ = ref_.get()
    current_depuser = request.form.get("depcustId")

    postsdep = db.reference('Inquiry').get()
    if postsdep is not None:
        vals = list(postsdep.values())
        postsdep = json.dumps(vals)
    else:
        postsdep = {}    
    print(postsdep)

    return render_template("department_inquiry.html", x = username_, postsdep = postsdep)
################################

@app.route("/submit", methods=['GET', 'POST'])
def get_pred():
    if request.method == 'POST':
        img = request.files['my_image']
        #img_path = 'C:/Users/USER/Desktop/firebase/Scripts/static/'+img.filename
        #img_path= './static/'+img.filename
        img_pathn = 'static/'+img.filename
        img_path = 'static/'+img.filename
        img.save(img_path)
        fileName = img_path
        bucket = storage.bucket(app=farmers)
        p = predict_label(img_path)
        p = Markup(str(disease_dic[p]))

    return render_template("Crop Disease.html", prediction=p, img_pathn=img_pathn)


@app.route("/logged_in", methods=['POST'])
def button():
    global current_user
    current_user = request.form.get("custId")
    ref_ = db.reference('Farmers/' + current_user + '/userdetails/username')
    username_ = ref_.get()
    posts = db.reference('Farmers/' + current_user + '/submissions').get()
    if posts is not None:
        vals = list(posts.values())
        for i in range(len(vals)):
            vals[i]["filename"] = "https://storage.googleapis.com/agri-app1.appspot.com/static/" + vals[i]["filename"]
        posts = json.dumps(vals)
    else:
        posts = {}    
    print(posts)
    return render_template("home.html" , x = username_.upper() , posts = posts)


@app.route("/logged_inD", methods=['POST'])
def dep():
    global current_depuser
    current_depuser = request.form.get("depcustId")
    ref_ = db.reference('Department/' + current_depuser + '/userdetails/username',app=department, url="https://agri-department1-default-rtdb.firebaseio.com/")
    username_ = ref_.get()
    current_depuser = request.form.get("depcustId")

    postsdep = db.reference('Inquiry').get()
    if postsdep is not None:
        vals = list(postsdep.values())
        postsdep = json.dumps(vals)
    else:
        postsdep = {}    
    print(postsdep)

    return render_template("department.html", x = username_, postsdep = postsdep)

@app.route("/uploaded", methods=['POST'])
def loggedD():
    files = request.files.getlist('files[]')
    dname = request.form['fname']
    pname = request.form['pname']
    print(type(dname))
    for file in files:
        img_path = 'static/upload/' + \
            dname+'__'+file.filename
        temp = pname+'__'+dname+'__'+file.filename
        file.save(img_path)

        fileName = img_path
        bucket = storage.bucket(app=department)
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
        blob.make_public()
        print(current_depuser)
        path = 'Department/' + current_depuser
        ref = db.reference(
            path, app=department, url="https://agri-department1-default-rtdb.firebaseio.com/")
        users_ref = ref.child('submissions')
        key = (temp).split(".")[0]
        users_ref.update({key: temp})

    postsdep = db.reference('Inquiry').get()
    if postsdep is not None:
        vals = list(postsdep.values())
        postsdep = json.dumps(vals)
    else:
        postsdep = {}

    #img = request.files['my_images']
    # print(request.files)
    #img_path = 'C:/Users/USER/Desktop/firebase/Scripts/static/'+img.filename
    #img_pathn= 'static/'+img.filename
    msg = "Files Uploaded Successfully"
    return render_template("department.html", postsdep = postsdep, msg = msg)


@app.route("/prediction", methods=['POST'])
def logged():
    img = request.files['my_image']
    img_path = 'static/'+img.filename
    img_pathn ='static/'+img.filename
    img.save(img_path)
    fileName = img_path
    bucket = storage.bucket(app=farmers)
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    blob.make_public()
    ref = db.reference('Farmers/' + current_user, app=farmers,
                       url="https://agri-app1-default-rtdb.firebaseio.com/")
    ref_ = db.reference('Farmers/' + current_user + '/userdetails/username',
                        app=farmers, url="https://agri-app1-default-rtdb.firebaseio.com/")
    username_ = ref_.get()
    print(username_)
    key = (img.filename).split(".")[0]
    users_ref = ref.child('submissions/'+key)
    users_ref.update({"filename": img.filename})
    p = predict_label(img_path)
    p = Markup(str(disease_dic[p]))
    ct = datetime.datetime.now()
    ct = str(ct)
    print(ct)
    users_ref.update({"prediction": p})
    users_ref.update({"date": ct})
    posts = db.reference('Farmers/' + current_user + '/submissions', app=farmers,
                         url="https://agri-app1-default-rtdb.firebaseio.com/").get()

    if posts is not None:
        vals = list(posts.values())
        for i in range(len(vals)):
            vals[i]["filename"] = "https://storage.googleapis.com/agri-app1.appspot.com/static/" + vals[i]["filename"]
        posts = json.dumps(vals)
    else:
        posts = {}
    #vals = list(posts.values())
    
    
    return render_template("home.html", prediction=p, img_pathn=img_pathn, x=username_.upper(), posts=posts, background = "/static/navbar.jpg")

@app.route("/inquire", methods=['POST'])
def inquired():
    img = request.files['inquiry_image']
    name = request.form['username']
    inquiry_path = 'static/'+img.filename
    img.save(inquiry_path)

    fileName = inquiry_path
    bucket = storage.bucket(app=farmers)
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    blob.make_public()

    ref_inquiry = db.reference('Inquiry/' + name)
    ref_inquiry.update({"image": fileName})

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)


