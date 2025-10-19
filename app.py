import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Optional

# Load environment variables from .env file for local development
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") # No dev default here; must be set
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) # Initialize SQLAlchemy directly with the app

# --- Database Models (all defined directly here) ---
class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationships handled by other models' backrefs or direct relationship
    def __repr__(self):
        return f"Discipline('{self.name}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"Project('{self.name}')"

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Region('{self.name}')"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    manager_email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='employee')

    ve_entries_submitted = db.relationship('VEEntry', foreign_keys='VEEntry.submitter_email', backref='submitter_employee', lazy=True)
    peo_role_mappings = db.relationship('PEOMapping', foreign_keys='PEOMapping.peo_email', backref='peo_employee_obj', lazy=True)

    def __repr__(self):
        return f"Employee('{self.name}', '{self.email}', Role: '{self.role}')"

class PEOMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=False)
    peo_email = db.Column(db.String(120), db.ForeignKey('employee.email'), nullable=False)
    
    discipline = db.relationship('Discipline', backref='peo_mappings', uselist=False)

    def __repr__(self):
        return f"PEOMapping(Discipline: '{self.discipline.name}', PEO: '{self.peo_email}')"

class VEEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    submitter_email = db.Column(db.String(120), db.ForeignKey('employee.email'), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    direct_cost_savings = db.Column(db.Float, nullable=False)
    hours_saved = db.Column(db.Integer, nullable=False)
    approved_by_region = db.Column(db.Boolean, nullable=False, default=False)

    discipline = db.relationship('Discipline', backref='ve_entries_discipline', lazy=True)
    project = db.relationship('Project', backref='ve_entries_project', lazy=True)
    region = db.relationship('Region', backref='ve_entries_region', lazy=True)

    status = db.Column(db.String(50), nullable=False, default='Pending Manager Approval')
    
    manager_email = db.Column(db.String(120), db.ForeignKey('employee.email'), nullable=True)
    manager_approval_date = db.Column(db.DateTime, nullable=True)
    manager_approval_status = db.Column(db.String(20), nullable=True)
    manager_comment = db.Column(db.Text, nullable=True)

    peo_email = db.Column(db.String(120), db.ForeignKey('employee.email'), nullable=True)
    peo_approval_date = db.Column(db.DateTime, nullable=True)
    peo_approval_status = db.Column(db.String(20), nullable=True)
    peo_comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"VEEntry(ID:{self.id}, Submitter:'{self.submitter_email}', Status:'{self.status}')"


# --- Web Forms (all defined directly here) ---
class VEEntryForm(FlaskForm):
    discipline = SelectField('Discipline', validators=[DataRequired()])
    project_name = SelectField('Project Name', validators=[DataRequired()])
    region = SelectField('Region', validators=[DataRequired()])
    
    description = TextAreaField('Description of VE', validators=[DataRequired(), Length(min=10, max=500)],
                                render_kw={"placeholder": "Provide a detailed description of the Value Engineering idea"})
    
    direct_cost_savings = FloatField('Direct Cost Savings ($)', validators=[DataRequired(), NumberRange(min=0.0)],
                                    render_kw={"placeholder": "e.g., 1500.50"})
    hours_saved = IntegerField('# Hours Saved', validators=[DataRequired(), NumberRange(min=0)],
                                render_kw={"placeholder": "e.g., 80"})
    approved_by_region = BooleanField('Approved by Region (Initial Review)')
    
    submit = SubmitField('Submit VE Entry')

class ManagerApprovalForm(FlaskForm):
    manager_approval_status = SelectField('Manager Approval', choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')],
                                        validators=[DataRequired()])
    manager_comment = TextAreaField('Manager Comment', validators=[Optional(), Length(max=500)],
                                    render_kw={"placeholder": "Enter your comments here (optional)"})
    submit = SubmitField('Submit Manager Approval')

class PEOApprovalForm(FlaskForm):
    peo_approval_status = SelectField('PEO Approval', choices=[('Approved', 'Approved'), ('Hold', 'Hold')],
                                    validators=[DataRequired()])
    peo_comment = TextAreaField('PEO Comment', validators=[Optional(), Length(max=500)],
                                render_kw={"placeholder": "Enter your comments here (optional)"})
    submit = SubmitField('Submit PEO Approval')


# --- IAP User Capture Helper ---
def get_current_user_email():
    iap_email = request.headers.get('X-Goog-Authenticated-User-Email')
    if iap_email:
        if "accounts.google.com:" in iap_email:
            return iap_email.split("accounts.google.com:")[1]
        return iap_email
    return os.getenv("LOCAL_DEV_EMAIL", "local.dev@fallback.com")
# --- Context Processor for Global Template Variables ---
@app.context_processor
def inject_global_vars():
    return dict(current_user_email=get_current_user_email())

# --- Routes ---
@app.route('/')
def home():
    employees = Employee.query.all()
    
    ve_entries_summary = db.session.query(
        VEEntry.id,
        Employee.name.label('submitter_name'),
        Discipline.name.label('discipline_name'),
        Project.name.label('project_name'),
        Region.name.label('region_name'),
        VEEntry.status,
        VEEntry.manager_approval_status,
        VEEntry.peo_approval_status
    ).join(Employee, VEEntry.submitter_email == Employee.email) \
     .join(Discipline, VEEntry.discipline_id == Discipline.id) \
     .join(Project, VEEntry.project_id == Project.id) \
     .join(Region, VEEntry.region_id == Region.id) \
     .order_by(VEEntry.creation_date.desc()).all() 

    return render_template('home.html', 
                           message="Welcome to Value Engineering App!", 
                           employees=employees, 
                           ve_entries_summary=ve_entries_summary)

@app.route('/create', methods=['GET', 'POST'])
def create_entry():
    form = VEEntryForm()

    form.discipline.choices = [(d.id, d.name) for d in Discipline.query.order_by(Discipline.name).all()]
    form.project_name.choices = [(p.id, p.name) for p in Project.query.order_by(Project.name).all()]
    form.region.choices = [(r.id, r.name) for r in Region.query.order_by(Region.name).all()]

    if form.validate_on_submit():
        submitter_email = get_current_user_email()

        submitter = Employee.query.filter_by(email=submitter_email).first()
        if not submitter:
            flash('Error: Your employee profile not found. Please contact admin.', 'danger')
            return redirect(url_for('home'))
        
        manager_for_approval = Employee.query.filter_by(email=submitter.manager_email).first()
        manager_email_for_entry = manager_for_approval.email if manager_for_approval else None

        new_entry = VEEntry(
            submitter_email=submitter_email,
            discipline_id=form.discipline.data,
            project_id=form.project_name.data,
            region_id=form.region.data,
            description=form.description.data,
            direct_cost_savings=form.direct_cost_savings.data,
            hours_saved=form.hours_saved.data,
            approved_by_region=form.approved_by_region.data,
            manager_email=manager_email_for_entry
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Your Value Engineering entry has been submitted!', 'success')
        return redirect(url_for('home'))

    return render_template('create_entry.html', 
                           title="Create New VE Entry", 
                           form=form, 
                           current_user_email=get_current_user_email())

# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# --- Database Seeding (can be run directly from app.py for simplicity now) ---
def seed_data():
    with app.app_context():
        db.create_all() # Ensure tables are created (idempotent)

        # --- Create Lookup Data if not exists ---
        if not Discipline.query.first():
            print("Seeding Disciplines...")
            disciplines = [
                Discipline(name='Mechanical'),
                Discipline(name='Electrical'),
                Discipline(name='Civil'),
                Discipline(name='Chemical'),
                Discipline(name='Software')
            ]
            db.session.add_all(disciplines)
            db.session.commit()
            print(f"Added {len(disciplines)} disciplines.")

        if not Project.query.first():
            print("Seeding Projects...")
            projects = [
                Project(name='Project Alpha'),
                Project(name='Project Beta'),
                Project(name='Project Gamma'),
                Project(name='Project Delta'),
                Project(name='Project Epsilon')
            ]
            db.session.add_all(projects)
            db.session.commit()
            print(f"Added {len(projects)} projects.")

        if not Region.query.first():
            print("Seeding Regions...")
            regions = [
                Region(name='North America'),
                Region(name='Europe'),
                Region(name='Asia Pacific'),
                Region(name='Middle East'),
                Region(name='South America')
            ]
            db.session.add_all(regions)
            db.session.commit()
            print(f"Added {len(regions)} regions.")

        # --- Create Sample Employees with Roles if not exists ---
        if not Employee.query.first():
            print("Seeding Employees...")
            
            emp1 = Employee(email='parthiban.k.ext@veolia.com', name='Parthiban K', manager_email='manager.us@veolia.com', role='employee')
            emp2 = Employee(email='employee.eu@veolia.com', name='Employee EU', manager_email='manager.eu@veolia.com', role='employee')

            mgr_us = Employee(email='manager.us@veolia.com', name='Manager US', manager_email='peo.mechanical@veolia.com', role='manager')
            mgr_eu = Employee(email='manager.eu@veolia.com', name='Manager EU', manager_email='peo.electrical@veolia.com', role='manager')

            peo_mech = Employee(email='peo.mechanical@veolia.com', name='PEO Mechanical', role='peo')
            peo_elec = Employee(email='peo.electrical@veolia.com', name='PEO Electrical', role='peo')
            peo_civil = Employee(email='peo.civil@veolia.com', name='PEO Civil', role='peo')

            db.session.add_all([emp1, emp2, mgr_us, mgr_eu, peo_mech, peo_elec, peo_civil])
            db.session.commit()
            print(f"Added {Employee.query.count()} employees.")

            # --- Create PEO Mappings if not exists ---
            print("Seeding PEO Mappings...")
            
            discipline_mech = Discipline.query.filter_by(name='Mechanical').first()
            discipline_elec = Discipline.query.filter_by(name='Electrical').first()
            discipline_civil = Discipline.query.filter_by(name='Civil').first()

            if discipline_mech and not PEOMapping.query.filter_by(discipline_id=discipline_mech.id).first():
                db.session.add(PEOMapping(discipline_id=discipline_mech.id, peo_email=peo_mech.email))
            if discipline_elec and not PEOMapping.query.filter_by(discipline_id=discipline_elec.id).first():
                db.session.add(PEOMapping(discipline_id=discipline_elec.id, peo_email=peo_elec.email))
            if discipline_civil and not PEOMapping.query.filter_by(discipline_id=discipline_civil.id).first():
                db.session.add(PEOMapping(discipline_id=discipline_civil.id, peo_email=peo_civil.email))
            
            db.session.commit()
            print(f"Added {PEOMapping.query.count()} PEO mappings.")

        print("Database seeding complete!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ensure tables are created (will create site.db if not present)
        print("Database tables created or confirmed existing!")
        seed_data() # Seed initial data
        print("Initial data seeded or confirmed existing!")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))