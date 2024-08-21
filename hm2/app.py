from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vaccination.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    vaccine = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)

# Initialize the database
db.create_all()

# Routes

@app.route('/register_parent', methods=['POST'])
def register_parent():
    data = request.json
    new_parent = Parent(name=data['name'], email=data['email'])
    db.session.add(new_parent)
    db.session.commit()
    return jsonify({'message': 'Parent registered successfully'})

@app.route('/add_child', methods=['POST'])
def add_child():
    data = request.json
    parent = Parent.query.filter_by(email=data['parent_email']).first()
    if not parent:
        return jsonify({'message': 'Parent not found'}), 404
    
    new_child = Child(name=data['name'], dob=datetime.strptime(data['dob'], '%Y-%m-%d'), parent_id=parent.id)
    db.session.add(new_child)
    db.session.commit()
    return jsonify({'message': 'Child added successfully'})

@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    data = request.json
    child = Child.query.filter_by(name=data['child_name']).first()
    if not child:
        return jsonify({'message': 'Child not found'}), 404
    
    new_appointment = Appointment(child_id=child.id, vaccine=data['vaccine'], date=datetime.strptime(data['date'], '%Y-%m-%d'))
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment scheduled successfully'})

@app.route('/get_appointments', methods=['GET'])
def get_appointments():
    child_name = request.args.get('child_name')
    child = Child.query.filter_by(name=child_name).first()
    if not child:
        return jsonify({'message': 'Child not found'}), 404
    
    appointments = Appointment.query.filter_by(child_id=child.id).all()
    appointment_list = [{'vaccine': appt.vaccine, 'date': appt.date.strftime('%Y-%m-%d')} for appt in appointments]
    return jsonify(appointment_list)

@app.route('/send_reminders', methods=['POST'])
def send_reminders():
    today = datetime.today().date()
    reminders = Appointment.query.filter(Appointment.date == today + timedelta(days=1), Appointment.reminder_sent == False).all()
    
    for appt in reminders:
        child = Child.query.get(appt.child_id)
        parent = Parent.query.get(child.parent_id)
        # Simulate sending an email reminder
        print(f"Reminder: Your child {child.name} has a vaccination appointment for {appt.vaccine} on {appt.date}.")
        
        appt.reminder_sent = True
        db.session.commit()

    return jsonify({'message': 'Reminders sent successfully'})

if __name__ == '__main__':
    app.run(debug=True)
