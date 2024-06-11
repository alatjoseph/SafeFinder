import os
import random
import secrets
import sqlite3
import string
import uuid

import face_recognition
import geocoder
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_mail import Mail, Message
from geopy.geocoders import Nominatim
from werkzeug.utils import secure_filename

app = Flask(__name__)
mail = Mail(app)
# Route to display the user registration page
app.config['UPLOAD_FOLDER'] = 'static/admin_img'
app.config['INSERT_FOLDER']='static/user_img'
app.secret_key="ass"


@app.route('/display2')
def display_data2():
    # Retrieve the JSON data from the query parameter

    parsed_data=session["c2"]
    # Parse the JSON data

    # Render a template and pass the parsed data to it
    return render_template('d2.html', match_data=parsed_data)
@app.route('/display')
def display_data():
    # Retrieve the JSON data from the query parameter

    parsed_data=session["check"]
    # Parse the JSON data

    # Render a template and pass the parsed data to it
    return render_template('detail.html', data=parsed_data)

@app.route("/get_data/<name>")
def get_data(name):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE name=?", (name,))
    matched_data = c.fetchall()
    conn.close()
    session["check"]=matched_data
    
    return jsonify({"data": matched_data})

@app.route("/get_data2/<name>")
def get_data2(name):
    conn = sqlite3.connect('match_db.db')
    c = conn.cursor()
    c.execute("SELECT * FROM match_db WHERE admin_name=?", (name,))
    matched_data = c.fetchall()
    conn.close()
    session["c2"]=matched_data
    print(matched_data)
    return jsonify({"data": matched_data})


# @app.route('/home')
# def home():
#      render_template('login.html')

@app.route('/')
def initial():
    
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute("SELECT name FROM admin")
    children = c.fetchall()
    conn.close()

    conn = sqlite3.connect('match_db.db')
    c = conn.cursor()
    c.execute("SELECT admin_name FROM match_db")
    match = c.fetchall()
    return render_template('index.html', children=children, match=match)

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/homepg.html')
def home_page():
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute("SELECT name FROM admin")
    children = c.fetchall()
    conn.close()

    conn = sqlite3.connect('match_db.db')
    c = conn.cursor()
    c.execute("SELECT admin_name FROM match_db")
    match = c.fetchall()
    return render_template('homepg.html', children=children, match=match)
    

@app.route('/user.html')
def user_page():
    return render_template('user.html')

def create_table():
    conn = sqlite3.connect('user1.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user1
             (sid INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             phone TEXT NOT NULL,
             address TEXT NOT NULL,
             pstation TEXT NOT NULL,
             aclocation TEXT NOT NULL,
             location TEXT NOT NULL,
             photo TEXT)''')  # Ensure the column names match the insertion query
    conn.commit()
    conn.close()


    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admin
             (sid INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              age INT NOT NULL,
              height FLOAT NOT NULL,
              gender TEXT NOT NULL,
              address VARCHAR(250) NOT NULL,
              pname TEXT NOT NULL,
              pnum INT NOT NULL,
              police_station_name TEXT NOT NULL,
              station_number INT NOT NULL,
              photo1 TEXT,
              photo2 TEXT,
              photo3 TEXT,
              email TEXT)''')

 # Ensure the column names match the insertion query
    conn.commit()
    conn.close()

    conn = sqlite3.connect('match_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS match_db
             (sid INTEGER PRIMARY KEY AUTOINCREMENT,
             user_name TEXT NOT NULL,
             user_phone TEXT NOT NULL,
             user_address TEXT NOT NULL,
             user_pstation TEXT NOT NULL,
             user_aclocation TEXT NOT NULL,
             user_location TEXT NOT NULL,
             user_photo TEXT,
             admin_name TEXT NOT NULL,
             admin_age INT NOT NULL,
             admin_height FLOAT NOT NULL,
             admin_gender TEXT NOT NULL,
             admin_address VARCHAR(250) NOT NULL,
             admin_pname TEXT NOT NULL,
             admin_pnum INT NOT NULL,
             pstation_name TEXT NOT NULL,
             station_number INT NOT NULL,
             admin_photo1 TEXT,
             admin_photo2 TEXT,
             admin_photo3 TEXT,
             admin_email TEXT)''')
    conn.commit()
    conn.close()
# Route to handle the user registration form submission
@app.route('/user_register', methods=['POST'])
def user_register():
    location = geocoder.ip('me')
    latitude, longitude = location.latlng
    print(latitude)
    print(longitude)

    lat=latitude+0.79382
    long=longitude-0.411893
    # lat=12.041820
    # long=75.368507
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.reverse((lat, long))
    place_name = location.address
    print("Place Name:", place_name)
    
    render_file_name=''
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        pstation = request.form['pstation']
        acloc = request.form['loc']
        
        location=place_name    
        # location='chemperi'
        print(location)
        # Store the photo into the database
        conn = sqlite3.connect('user1.db')
        c = conn.cursor()
        if 'image' in request.files:
            image = request.files['image']
            filename1 = str(uuid.uuid4()) + os.path.splitext(image.filename)[1] 
            # filename = image1.filename
            image.save(os.path.join(app.config['INSERT_FOLDER'], filename1))
            print("inserted data = "+filename1)
        else:
            filename1 = None
            
        c.execute("INSERT INTO user1(name, phone,address,pstation,aclocation,location,photo) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, phone,address,pstation,acloc,location,filename1))
        conn.commit()
        conn.close()
        cname = ""
        cage = ""
        cheight =""
        cgender = ""
        caddress = ""
        cpname = ""
        cpnum = ""
        cpic1 = ""
        cpic2 = ""
        cpic3 = ""
        p_station=''
        p_station_num=''
        

        best_match_name=''
        if filename1!='':
            best_match_name=perform_face_comparison(filename1)
    if best_match_name =='':
        print("no data match-----------------")
        render_file_name='no_match.html'
    else:
        render_file_name='match.html'
        conn = sqlite3.connect('admin.db')
        print('connecion established')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE photo1=? OR photo2=? OR photo3=?", (best_match_name, best_match_name, best_match_name))
        match_data = c.fetchall()
        print(match_data)

        if match_data:
            print("Match data found:", match_data)
            for row in match_data:
                print("Row:", row)
                cname = row[1]
                cage = row[2]
                cheight = row[3]
                cgender = row[4]
                caddress = row[5]
                cpname = row[6]
                cpnum = row[7]
                cpic1 = row[10]
                cpic2 = row[11]
                cpic3 = row[12]
                p_station=row[8]
                p_station_num=row[9]
                ad_mail=row[13]
        else:
            print("No match data found")

        conn.commit()
        conn.close()
        print("user details")
        print(cname,caddress)
        if match_data:
            
            conn = sqlite3.connect('match_db.db')
            c = conn.cursor()       
                
            c.execute('''INSERT INTO match_db 
                (user_name, user_phone, user_address, user_pstation, user_aclocation, user_location, user_photo,
                admin_name, admin_age, admin_height, admin_gender, admin_address, admin_pname, admin_pnum, pstation_name, station_number, admin_photo1, admin_photo2, admin_photo3, admin_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (name,phone, address, pstation, acloc, location, filename1,
                cname, cage, cheight, cgender, caddress, cpname, cpnum, p_station, p_station_num, cpic1, cpic2, cpic3, ad_mail))
    
                
                
            conn.commit()
            conn.close()  
        conn = sqlite3.connect('match_db.db')
        c = conn.cursor()
        c.execute("SELECT admin_name FROM match_db")
        match = c.fetchall()
        conn.close()
        
        conn = sqlite3.connect('match_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM match_db WHERE user_photo=?", (filename1,))
        details = c.fetchall()
        conn.close()
        
        
       
        
        conn = sqlite3.connect('match_db.db')
        c = conn.cursor()
        c.execute("SELECT user_name, user_phone, user_address, user_location, admin_name, admin_age, admin_gender, admin_address, admin_email FROM match_db WHERE user_photo=?", (filename1,))
        data = c.fetchall()
        # Initialize variables with empty strings
        u_name, u_phone, u_address, u_location, ch_name, ch_age, c_gender, c_address, cp_email = '', '', '', '', '', '', '', '', ''



        recipient_email=cp_email
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = 'missingchilddetectionportal8@gmail.com' # Your Gmail email address
        app.config['MAIL_PASSWORD'] = 'qkpw rvfn lksa nkre'  # Your Gmail password or app-specific password

# Initialize Flask-Mail
        mail = Mail(app)  # Use your generated app-specific password here

        if data:
            u_name, u_phone, u_address, u_location, ch_name, ch_age, c_gender, c_address, cp_email = data[0]
            print(data)
            
            print(type)
                # Define email content
            recipient_email = cp_email
            subject = 'Match Found: Missing Child'
            message_body = f"""Dear Officer,\n
            We are writing to inform you that we have found a match for the missing child case registered at your station.\n
            Name: {ch_name}\n
            Age: {ch_age}\n
            Gender: {c_gender}\n
            Address: {c_address}\n
                
            The details of the uploaded person are as follows:\n

            Name: {u_name}\n
            Phone: {u_phone}\n
            Address: {u_address}\n
            Location: {u_location}\n
            """

            try:
                # Create a message
                msg = Message(subject, sender='your-email@gmail.com', recipients=[recipient_email])
                msg.body = message_body

                # Send the message
                mail.send(msg)
                print("Email sent successfully!")
            except Exception as e:
                print(f"Error sending email: {str(e)}")
        else:
            print("No data found for the provided filename.")
        return render_template('match.html', match=match,data=details)
    return render_template(render_file_name)




import os

import cv2
import face_recognition


def perform_face_comparison(fname,):
    user_image_path = os.path.join("static", "user_img", fname)
    known_faces_directory= "static/admin_img"
    def encode_face(image):
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0]
        else:
            return None

    def compare_faces(known_face_encoding, unknown_face_encoding):
        if known_face_encoding is not None and unknown_face_encoding is not None:
            match = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)[0]
            return match
        else:
            return False

    def calculate_accuracy(known_face_encoding, unknown_face_encoding):
        if known_face_encoding is not None and unknown_face_encoding is not None:
            distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding)
            accuracy = (1 - distance[0]) * 100
            return accuracy
        else:
            return 0.0

    # Load known faces
    known_face_encodings = []
    known_face_names = []

    # Load and encode known faces from a directory
    for filename in os.listdir(known_faces_directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(known_faces_directory, filename)
            image = cv2.imread(image_path)
            face_encoding = encode_face(image)
            if face_encoding is not None:
                known_face_encodings.append(face_encoding)
                known_face_names.append(os.path.splitext(filename)[0])

    # Load the user image to be compared
    unknown_image = cv2.imread(user_image_path)

    # Encode the unknown face
    unknown_face_encoding = encode_face(unknown_image)

    best_match_name = ""
    best_match_accuracy = 0.0

    # Compare the unknown face with known faces
    for known_face_encoding, name in zip(known_face_encodings, known_face_names):
        match = compare_faces(known_face_encoding, unknown_face_encoding)
        if match:
            accuracy = calculate_accuracy(known_face_encoding, unknown_face_encoding)
            if accuracy > best_match_accuracy:
                best_match_accuracy = accuracy
                best_match_name = name+'.jpg'

    # Return the best match
    if best_match_accuracy > 50:
        print(f"Best match: Name - {best_match_name}, Accuracy - {best_match_accuracy:.2f}%")
        return best_match_name
    else:
        return ""
    







@app.route('/admin_register', methods=['POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        height = request.form['height']
        gender = request.form['gender']
        address = request.form['address']
        pname = request.form['pname']
        pnum = request.form['pnum']
        station_name=request.form['sname']
        station_num=request.form['snum']
        station_mail=request.form['smail']
        conn = sqlite3.connect('admin.db')
        c = conn.cursor()
            # Handle file uploads
        if 'image1' in request.files:
            image1 = request.files['image1']
            filename1 = str(uuid.uuid4()) + os.path.splitext(image1.filename)[1] 
            # filename = image1.filename
            image1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            print(filename1)
        else:
            filename1 = None
            print(filename1)
        if 'image2' in request.files:
            image2 = request.files['image2']
            filename2 = str(uuid.uuid4()) + os.path.splitext(image2.filename)[1] 
            image2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            print(filename2)
        else:
            filename2 = None
            print(filename2)
        if 'image3' in request.files:
            image3 = request.files['image3']
            filename3 = str(uuid.uuid4()) + os.path.splitext(image3.filename)[1] 
            image3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
            print(filename3)
        else:
            filename3= None
            print(filename3)

    
    # Save image filenames to the database

        c.execute("INSERT INTO admin (name, age, height, gender, address, pname, pnum, police_station_name, station_number, photo1, photo2, photo3, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, age, height, gender, address, pname, pnum, station_name, station_num, filename1, filename2, filename3, station_mail))
        conn.commit()
        c.execute("SELECT name FROM admin")
        children = c.fetchall()
        conn.close()
        
    return render_template('homepg.html',children=children)





if __name__ == '__main__':
    create_table()
    # registered_case()
    #match_case()
    app.run(debug=True)
