
from flask import Flask, request, render_template


app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

cred = credentials.Certificate("C:/Users/Ishan/OneDrive/Desktop/firebase/Scripts/ServiceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["POST"])
def signup():
    if request.method == 'POST':
        user_data = [x for x in request.form.values()]
        user = auth.create_user(
            email=user_data[1],
            uid=user_data[0],
            #phone_number=user_data[3],
            password=user_data[2],
            display_name=user_data[0],
            disabled=False)


        doc_ref = db.collection(user.uid).document('User Details')
        doc_ref.set({
            'name':user.display_name,
            'email': user.email,
            #'phone_number':user.phone_number
        })
    return render_template("home.html")

if __name__ == "__main__":
    app.run()