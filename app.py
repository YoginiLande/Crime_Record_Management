from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from database.db import get_connection
from flask import redirect
from flask import send_file
from reportlab.pdfgen import canvas

app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
     return render_template('index.html')
   

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/police-dashboard')
def police_dashboard():
    return render_template('police_dashboard.html')

@app.route('/add-case')
def add_case_page():
    return render_template('add_case.html')

@app.route('/admin-dashboard')
def admin_dashboard():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT crime_type,
               COUNT(*) AS total
        FROM cases
        GROUP BY crime_type
    """)

    crime_stats = cursor.fetchall()

    print(crime_stats)   # Debug line

    cursor.close()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        crime_stats=crime_stats
    )
@app.route('/add-criminal')
def add_criminal_page():
    return render_template('add_criminal.html')

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    fullname = data['fullname']
    email = data['email']
    password = data['password']
    role = data['role']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Email already exists"
        }), 400

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode('utf-8')

    name = data['fullname']

    cursor.execute("""
      INSERT INTO users(name,email,password,role)
      VALUES(%s,%s,%s,%s)
      """,
      (name, email, hashed_password, role))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "User Registered Successfully"
    })
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data['email']
    password = data['password']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if bcrypt.check_password_hash(user['password'], password):

        return jsonify({
            "message": "Login Successful",
            "role": user['role']
        })

    return jsonify({
        "message": "Invalid Password"
    }), 401

@app.route('/add-case', methods=['POST'])
def add_case():

    crime_type = request.form['crime_type']
    description = request.form['description']
    location = request.form['location']
    status = request.form['status']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cases
        (crime_type, description, location, case_status)
        VALUES (%s,%s,%s,%s)
    """,
    (crime_type, description, location, status))

    conn.commit()

    cursor.close()
    conn.close()

    return "Case Added Successfully"

@app.route('/view-cases')
def view_cases():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cases")

    cases = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_cases.html',
        cases=cases
    )

@app.route('/edit-case/<int:case_id>')
def edit_case(case_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM cases WHERE case_id=%s",
        (case_id,)
    )

    case = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'edit_case.html',
        case=case
    )

@app.route('/update-case/<int:case_id>', methods=['POST'])
def update_case(case_id):

    status = request.form['status']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE cases
        SET status=%s
        WHERE case_id=%s
        """,
        (status, case_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/view-cases')

@app.route('/add-criminal', methods=['POST'])
def add_criminal():

    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    crime_history = request.form['crime_history']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO criminals
        (name, age, gender,crime_history)
        VALUES (%s,%s,%s,%s)
    """,
    (name, age, gender, crime_history))

    conn.commit()

    cursor.close()
    conn.close()

    return "Criminal Added Successfully 🚔"

@app.route('/view-criminals')
def view_criminals():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM criminals")

    criminals = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_criminals.html',
        criminals=criminals
    )

@app.route('/generate-report/<int:case_id>')
def generate_report(case_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM cases WHERE case_id=%s",
        (case_id,)
    )

    case = cursor.fetchone()

    cursor.close()
    conn.close()

    if not case:
        return "Case not found"

    pdf_file = f"case_report_{case_id}.pdf"

    c = canvas.Canvas(pdf_file)

    c.drawString(100, 800, "Crime Record Management System")
    c.drawString(100, 770, f"Case ID: {case['case_id']}")
    c.drawString(100, 740, f"Crime Type: {case['crime_type']}")
    c.drawString(100, 710, f"Location: {case['location']}")
    c.drawString(100, 680, f"Status: {case['status']}")
    c.drawString(100, 650, f"Description: {case['description']}")

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route('/test')
def test():
    return "TEST ROUTE WORKING"

if __name__ == "__main__":
    app.run(debug=True)