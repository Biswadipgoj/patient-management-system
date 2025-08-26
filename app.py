from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    screening_no = db.Column(db.String(20))
    screening_date = db.Column(db.String(15))
    age = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    residence = db.Column(db.String(200))
    contact_no = db.Column(db.String(20))
    duration_mc = db.Column(db.String(50))
    co_morbidities = db.Column(db.Text)
    risk_factors = db.Column(db.Text)
    treatment_taken = db.Column(db.Text)
    weight_kg = db.Column(db.String(10))
    height_cm = db.Column(db.String(10))
    education_status = db.Column(db.String(50))
    socio_economic_status = db.Column(db.String(50))
    baseline_treatment = db.relationship('BaselineTreatment', backref='patient', uselist=False, lazy=True)
    outcome_assessments = db.relationship('OutcomeAssessment', backref='patient', lazy=True)

class BaselineTreatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.String(15))
    present_complaint = db.Column(db.Text)
    prescription = db.Column(db.Text)
    miasm_data = db.Column(db.Text)
    susceptibility_data = db.Column(db.Text)

class OutcomeAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    assessment_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(15), nullable=False)
    brief_notes = db.Column(db.Text)
    prescription = db.Column(db.Text)
    oridl_main_complaint = db.Column(db.Text)
    oridl_wellbeing = db.Column(db.Text)
    miasm_data = db.Column(db.Text)
    susceptibility_data = db.Column(db.Text)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        reg_no = request.form['reg_no']
        existing_patient = Patient.query.filter_by(reg_no=reg_no).first()
        if existing_patient:
            return render_template('add_patient.html', error="Registration number already exists. Please check the number or search for the existing patient.")
        
        new_patient = Patient(
            reg_no=reg_no,
            name=request.form['name'],
            screening_no=request.form['screening_no'],
            screening_date=request.form['screening_date'],
            age=request.form['age'],
            sex=request.form['sex'],
            residence=request.form['residence'],
            contact_no=request.form['contact_no'],
            duration_mc=request.form['duration_mc'],
            co_morbidities=request.form['co_morbidities'],
            risk_factors=request.form['risk_factors'],
            treatment_taken=request.form['treatment_taken'],
            weight_kg=request.form['weight_kg'],
            height_cm=request.form['height_cm'],
            education_status=request.form['education_status'],
            socio_economic_status=request.form['socio_economic_status']
        )
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('add_baseline_treatment', patient_id=new_patient.id))
    return render_template('add_patient.html')

@app.route('/add_baseline_treatment/<int:patient_id>', methods=['GET', 'POST'])
def add_baseline_treatment(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_baseline = BaselineTreatment(
            patient_id=patient.id,
            date=request.form['date'],
            present_complaint=request.form['present_complaint'],
            prescription=request.form['prescription'],
            miasm_data = request.form.get('miasm_data', None),
            susceptibility_data = request.form.get('susceptibility_data', None)
        )
        db.session.add(new_baseline)
        db.session.commit()
        return render_template('success.html', message="Baseline Treatment details entered successfully.")

    return render_template('add_baseline_treatment.html', patient=patient)

@app.route('/patient_details', methods=['GET'])
def patient_details():
    search_query = request.args.get('search_query')
    patient = Patient.query.filter((Patient.reg_no == search_query) | (Patient.screening_no == search_query)).first()
    if patient:
        return render_template('patient_details.html', patient=patient, assessments=patient.outcome_assessments)
    return render_template('index.html', error="Patient not found.")

@app.route('/add_outcome_assessment/<int:patient_id>', methods=['GET', 'POST'])
def add_outcome_assessment(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient or len(patient.outcome_assessments) >= 6:
        return redirect(url_for('index'))

    assessment_number = len(patient.outcome_assessments) + 1
    
    if request.method == 'POST':
        new_assessment = OutcomeAssessment(
            patient_id=patient.id,
            assessment_number=assessment_number,
            date=request.form['date'],
            brief_notes=request.form['brief_notes'],
            prescription=request.form['prescription'],
            oridl_main_complaint=request.form['oridl_main_complaint'],
            oridl_wellbeing=request.form['oridl_wellbeing'],
            miasm_data=request.form.get('miasm_data', None) if assessment_number == 6 else None,
            susceptibility_data=request.form.get('susceptibility_data', None) if assessment_number == 6 else None
        )
        db.session.add(new_assessment)
        db.session.commit()
        return redirect(url_for('patient_details', search_query=patient.reg_no))

    return render_template('add_outcome_assessment.html', patient=patient, assessment_number=assessment_number, show_pdf_forms=(assessment_number == 6))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
