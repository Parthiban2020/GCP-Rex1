import os
from flask import Flask, render_template, send_from_directory, current_app, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, IntegerField, ValidationError, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Optional
from werkzeug.utils import secure_filename
from flask_migrate import Migrate # <--- FIXED: Uncommented this
# from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

# Define the upload folder
# WARNING: In Cloud Run, this folder is temporary. Files are deleted on restart.
UPLOAD_FOLDER = '/tmp/uploads' 
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

# Ensure upload folder exists (Cloud Run starts with an empty filesystem)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# --- Configuration ---
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-default-key") 

# Database Configuration Logic
# 1. Tries to get DATABASE_URL from Environment (Cloud Run)
# 2. Defaults to SQLite for local testing if Env Var is missing
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) 
migrate = Migrate(app, db) # This will now work because the import is fixed

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- MODELS ---
class Projectlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    Returnonexperienceentrymodels = db.relationship('Returnonexperienceentrymodel', backref='project', lazy=True)
    def __repr__(self): return f'<Projectlist "{self.name}">'
    
class Regionlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    Returnonexperienceentrymodels = db.relationship('Returnonexperienceentrymodel', backref='region', lazy=True)
    def __repr__(self): return f'<Regionlist"{self.name}")"'   

class Employeelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    Returnonexperienceentrymodels = db.relationship('Returnonexperienceentrymodel', backref='initiator', lazy=True)
    Mentor_RexCommittee = db.relationship('RexCommitteeModel', backref='Mentor_employeelist', foreign_keys='RexCommitteeModel.Mentor', lazy=True)
    ActionBy_RexCommittee = db.relationship('RexCommitteeModel', backref='ActionBy_employeelist', foreign_keys='RexCommitteeModel.ActionBy', lazy=True)
    QMSSpoc_RexCommittee = db.relationship('RexCommitteeModel', backref='QMSSpoc_employeelist', foreign_keys='RexCommitteeModel.QMSSpoc', lazy=True)
    AttendeesOfRootCause_ActionPlan = db.relationship('ActionPlanModel', backref='AttendeesOfRootCause_employeelist', foreign_keys='ActionPlanModel.AttendeesOfRootCause', lazy=True)
    def __repr__(self): return f'<Employeelist"{self.name}")"'  

class Disciplinelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    initiated_experiences = db.relationship('Returnonexperienceentrymodel', backref='initiating_discipline', foreign_keys='Returnonexperienceentrymodel.REXInitiatingDiscipline_id', lazy=True)
    on_topic_experiences = db.relationship('Returnonexperienceentrymodel', backref='on_topic_discipline', foreign_keys='Returnonexperienceentrymodel.REXOnDiscipline_id', lazy=True)
    def __repr__(self): return f'<Disciplinelist"{self.name}")"' 

class Frequencyofissuelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    ActionPlanModel = db.relationship('ActionPlanModel', backref='frequencyofissue', lazy=True)
    def __repr__(self): return f'<FrequencyofIssue"{self.name}")"' 

class Ehsrisklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    ActionPlanModel = db.relationship('ActionPlanModel', backref='ehsrisklist', lazy=True)
    def __repr__(self): return f'<Ehsrisklist"{self.name}")"'    
    
class Technologylist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    RexCommitteeModel = db.relationship('RexCommitteeModel', backref='technology', lazy=True)
    def __repr__(self): return f'<Technologylist"{self.name}")"'     

class Documenttoupdatelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    ActionPlanModel = db.relationship('ActionPlanModel', backref='documenttoupdatelist', lazy=True)
    def __repr__(self): return f'<Documenttoupdatelist"{self.name}")"'             
    
class Returnonexperienceentrymodel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='RexCommitee')
    ProjectNameAndNumber_id = db.Column(db.Integer, db.ForeignKey('projectlist.id'), nullable=False)
    Region_id = db.Column(db.Integer, db.ForeignKey('regionlist.id'), nullable=False)
    REXInitiator_id = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=False)
    REXOnDiscipline_id = db.Column(db.Integer, db.ForeignKey('disciplinelist.id'), nullable=False)
    REXInitiatingDiscipline_id = db.Column(db.Integer, db.ForeignKey('disciplinelist.id'), nullable=True)
    REXOnTopic = db.Column(db.String(500), nullable=False)
    REXDescription = db.Column(db.String(500), nullable=False)
    Impact = db.Column(db.String(500), nullable=False)
    AttachmentLink = db.Column(db.String(500), nullable=False)
    Recommendation = db.Column(db.String(500), nullable=False)
    
    primary_discipline = db.relationship('Disciplinelist', foreign_keys=[REXOnDiscipline_id])
    secondary_discipline = db.relationship('Disciplinelist', foreign_keys=[REXInitiatingDiscipline_id])
    rexcommitee  = db.relationship('RexCommitteeModel', backref='returnonexperienceentrymodel', lazy=True, cascade='all, delete-orphan')
    actionplan  = db.relationship('ActionPlanModel', backref='returnonexperienceentrymodel', lazy=True, cascade='all, delete-orphan')
    reviewByCommitteeModel  = db.relationship('ReviewByCommitteeModel', backref='returnonexperienceentrymodel', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self): return f"{self.id} - {self.date_created}"    
    
class RexCommitteeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parentid = db.Column(db.Integer, db.ForeignKey('returnonexperienceentrymodel.id'), nullable=False) 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    ReviewCommiteeMember = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=True)
    IsitREX = db.Column(db.String(100), nullable=False)
    Isfurtheranalysisrequired = db.Column(db.String(500), nullable=True)
    Mentor = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=True)
    ActionBy = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=True)
    QMSSpoc = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=True)
    Technology = db.Column(db.Integer, db.ForeignKey('technologylist.id'), nullable=True)
    REXCommitteeComments = db.Column(db.String(500), nullable=False)

    primary_employeelist = db.relationship('Employeelist', foreign_keys=[Mentor])
    secondary_employeelist = db.relationship('Employeelist', foreign_keys=[ActionBy])
    third_employeelist = db.relationship('Employeelist', foreign_keys=[QMSSpoc])
    fourth_employeelist = db.relationship('Employeelist', foreign_keys=[ReviewCommiteeMember])
    
    def __repr__(self): return f"{self.id} - {self.date_created}"    

class ActionPlanModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parentid = db.Column(db.Integer, db.ForeignKey('returnonexperienceentrymodel.id'), nullable=False) 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    AttendeesOfRootCause = db.Column(db.Integer, db.ForeignKey('employeelist.id'), nullable=True)
    Date = db.Column(db.DateTime , nullable=True)
    FrequesncyOfIssue = db.Column(db.Integer, db.ForeignKey('frequencyofissuelist.id'), nullable=True)
    EHSRisk = db.Column(db.Integer, db.ForeignKey('ehsrisklist.id'), nullable=True)
    AddDocumentsLink = db.Column(db.String(500), nullable=True)
    RootCause = db.Column(db.String(500), nullable=True)
    CorrectiveAction = db.Column(db.String(500), nullable=True)
    DocummentToUpdate = db.Column(db.Integer, db.ForeignKey('documenttoupdatelist.id'), nullable=True)
    Remarks = db.Column(db.String(500), nullable=True)
    AttachmentLink = db.Column(db.String(500), nullable=True)
    ReportingManagerConfirmation = db.Column(db.Boolean, nullable=False, default=False)
    primary_employeelist = db.relationship('Employeelist', foreign_keys=[AttendeesOfRootCause])
    def __repr__(self): return f"{self.id} - {self.date_created}"            

class ReviewByCommitteeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parentid = db.Column(db.Integer, db.ForeignKey('returnonexperienceentrymodel.id'), nullable=False) 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    Remarks = db.Column(db.String(500), nullable=False)
    def __repr__(self): return f"{self.id} - {self.date_created}"  

# --- FORMS ---
class ReturnOFExperienceForm(FlaskForm):
    ProjectNameAndNumber = SelectField('Project No. & Name',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'}, validators=[DataRequired()])
    Region = SelectField('Region',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'}, validators=[DataRequired()])
    REXInitiatingDiscipline = SelectField('REX Initiating Discipline',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'}, validators=[DataRequired()])
    REXOnDiscipline = SelectField('REX On Discipline',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'} , validators=[DataRequired()])
    REXInitiator = SelectField('REX Initiator',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'},  validators=[DataRequired()])
    REXOnTopic = StringField('REX On Topic',render_kw = {'class':'form-control'}, validators=[DataRequired()])
    REXDescription = TextAreaField('REX Description', validators=[DataRequired(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select"})
    Impact = TextAreaField('Impact', validators=[DataRequired(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select","style":"min-height: 80px;"})
    AttachmentLink = StringField('AttachmentLink',render_kw = {'class':'form-control'}, validators=[DataRequired()])
    Recommendation  = TextAreaField('Recommendation ', validators=[DataRequired(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select" ,"style":"min-height: 80px;"})
    submit = SubmitField('Submit',render_kw = {'class':'float-end'})

class RequiredIfYes(object):
    def __init__(self, other_field_name, message=None):
        self.other_field_name = other_field_name
        self.message = message
    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field.data == 'Yes' and not field.data:
            message = self.message
            if message is None:
                message = f'"{field.label.text}" is required when "{other_field.label.text}" is Yes.'
            raise ValidationError(message)

class RexCommitteeModelForm(FlaskForm):
    IsitREXChoice = [("", "--- Nothing selected ---"), ('Yes', 'Yes'), ('No', 'No'), ('Required more details', 'Required more details')]
    IsfurtheranalysisrequiredChoice = [("", "--- Nothing selected ---"), ('Required', 'Required'), ('NotRequired', 'NotRequired')]
    ReviewCommiteeMember = SelectField('Review Commitee Member',render_kw = {'class':'custom-select selectpicker cust-select' ,'id':'ReviewCommiteeMember','data-live-search':'true'}, validators=[DataRequired()])
    IsitREX = SelectField('Is it REX?',choices=IsitREXChoice,render_kw = {'data-live-search':'true'}, validators=[DataRequired()])
    Isfurtheranalysisrequired = SelectField('Is further analysis required',choices=IsfurtheranalysisrequiredChoice,render_kw = {'class':'custom-select selectpicker cust-select','id':'Isfurtheranalysisrequired' ,'data-live-search':'true'}, validators=[Optional()])
    Mentor = SelectField('Mentor',render_kw = {'class':'custom-select selectpicker cust-select','id':'Mentor', 'data-live-search':'true'} , validators=[Optional(),RequiredIfYes('IsitREX', message="Mentor is mandatory for REX projects.")])
    ActionBy = SelectField('ActionBy',render_kw = {'class':'custom-select selectpicker cust-select','id':'ActionBy', 'data-live-search':'true'},  validators=[Optional()])
    QMSSpoc = SelectField('QMS Spoc',render_kw = {'class':'custom-select selectpicker cust-select','id':'QMSSpoc', 'data-live-search':'true'},  validators=[Optional()])
    Technology = SelectField('Technology',render_kw = {'class':'custom-select selectpicker cust-select','id':'Technology', 'data-live-search':'true'},  validators=[Optional()])
    REXCommitteeComments = TextAreaField('REX Committee Comments', validators=[DataRequired(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select",'id':'REXCommitteeComments'})
    submit = SubmitField('Submit',render_kw = {'class':'float-end'}) 

    def validate(self, extra_validators=None):
        if not super(RexCommitteeModelForm, self).validate(extra_validators): return False
        is_valid = True
        if self.IsitREX.data == 'Yes':
            if not self.Isfurtheranalysisrequired.data:
                self.Isfurtheranalysisrequired.errors.append('Is further analysis required.')
                is_valid = False
            if not self.Mentor.data:
                self.Mentor.errors.append('Mentor is required.')
                is_valid = False
            if not self.ActionBy.data:
                self.ActionBy.errors.append('Action By is required.')
                is_valid = False  
            if not self.QMSSpoc.data:
                self.QMSSpoc.errors.append('QMS Spoc is required.')
                is_valid = False  
            if not self.Technology.data:
                self.Technology.errors.append('Technology is required.')
                is_valid = False            
        return is_valid

class ActionPlanForm(FlaskForm):
    AttendeesOfRootCause = SelectField('Attendees Of RootCause',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'}, validators=[Optional()])
    Date = DateField('Select a Date',render_kw = {'class':'form-control'}, format='%Y-%m-%d', validators=[Optional()])
    FrequesncyOfIssue = SelectField('Frequesncy Of Issue',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'}, validators=[Optional()])
    EHSRisk = SelectField('EHS Risk',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'} , validators=[Optional()])
    AddDocumentsLink = StringField('Add Documents Link',render_kw = {'class':'form-control'}, validators=[Optional()])
    RootCause = TextAreaField('Root Cause', validators=[Optional(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select","style":"min-height: 80px;"})
    CorrectiveAction = TextAreaField('Corrective Action', validators=[Optional(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select","style":"min-height: 80px;"})
    DocummentToUpdate = SelectField('Documment To Update',render_kw = {'class':'custom-select selectpicker cust-select', 'data-live-search':'true'},  validators=[Optional()])
    Remarks = TextAreaField('Remarks', validators=[Optional(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"custom-select","style":"min-height: 80px;"})
    AttachmentLink = StringField('Attachment Link',render_kw = {'class':'form-control'}, validators=[Optional()])
    ReportingManagerConfirmation = BooleanField('Have you discussed with Mentor?', validators=[DataRequired()])
    submit = SubmitField('Submit',render_kw = {'class':'float-end'})  
    
    def __init__(self, *args, external_Isfurtheranalysisrequired_Plan=None, **kwargs):
        super(ActionPlanForm, self).__init__(*args, **kwargs)
        self.external_Isfurtheranalysisrequired = external_Isfurtheranalysisrequired_Plan 

    def validate(self, extra_validators=None):
        if not super(ActionPlanForm, self).validate(extra_validators): return False
        is_valid = True
        if self.external_Isfurtheranalysisrequired == 'Required':
            if not self.AttendeesOfRootCause.data: self.AttendeesOfRootCause.errors.append('Attendees Of RootCause required.'); is_valid = False
            if not self.Date.data: self.Date.errors.append('Date is required.'); is_valid = False
            if not self.FrequesncyOfIssue.data: self.FrequesncyOfIssue.errors.append('Frequesncy Of Issue is required.'); is_valid = False  
            if not self.EHSRisk.data: self.EHSRisk.errors.append('EHS Risk is required.'); is_valid = False  
            if not self.AddDocumentsLink.data: self.AddDocumentsLink.errors.append('Add Documents Link is required.'); is_valid = False   
            if not self.RootCause.data: self.RootCause.errors.append('Root Cause is required.'); is_valid = False   
            if not self.CorrectiveAction.data: self.CorrectiveAction.errors.append('Corrective Action is required.'); is_valid = False 
        elif self.external_Isfurtheranalysisrequired == 'NotRequired':
            if not self.DocummentToUpdate.data: self.DocummentToUpdate.errors.append('Documment To Update Of RootCause required.'); is_valid = False
            if not self.Remarks.data: self.Remarks.errors.append('Remarks is required.'); is_valid = False
            if not self.AttachmentLink.data: self.AttachmentLink.errors.append('Attachment Link Of Issue is required.'); is_valid = False                    
        return is_valid

class ReviewByCommitteeForm(FlaskForm):
    Remarks = TextAreaField('Remarks', validators=[DataRequired(), Length(min=1, max=500)], render_kw={"placeholder": "Provide a detailed","class":"form-control","style":"min-height: 80px;"})
    submit_save = SubmitField('Submit',render_kw = {'class':'float-end'}) 
    submit_sendback = SubmitField('Send Back',render_kw = {'class':'float-end'}) 

# Helper functions for choices
def fetch_dynamic_choices(model):
    try:
        return [("", "--- Nothing selected ---")] + [(item.id, item.name) for item in model.query.order_by(model.name).all()]
    except Exception:
        # Prevents crash during database creation or if table empty
        return [("", "--- Nothing selected ---")]

def get_projectname_choices(): return fetch_dynamic_choices(Projectlist)
def get_region_choices(): return fetch_dynamic_choices(Regionlist)
def get_rexinitiator_choices(): return fetch_dynamic_choices(Employeelist)
def get_rexinitiatingdiscipline_choices(): return fetch_dynamic_choices(Disciplinelist)
def get_rexondiscipline_choices(): return fetch_dynamic_choices(Disciplinelist)
def get_reviewcommiteemember_choices(): return fetch_dynamic_choices(Employeelist)
def get_mentor_choices(): return fetch_dynamic_choices(Employeelist)
def get_actionby_choices(): return fetch_dynamic_choices(Employeelist)
def get_qmsspoc_choices(): return fetch_dynamic_choices(Employeelist)
def get_technology_choices(): return fetch_dynamic_choices(Technologylist)
def get_attendeesofrootcause_choices(): return fetch_dynamic_choices(Employeelist)
def get_frequencyofissue_choices(): return fetch_dynamic_choices(Frequencyofissuelist)
def get_ehsrisk_choices(): return fetch_dynamic_choices(Ehsrisklist)
def get_documenttoupdate_choices(): return fetch_dynamic_choices(Documenttoupdatelist)

# --- IAP User Capture Helper ---
def get_current_user_email():
    iap_email = request.headers.get('X-Goog-Authenticated-User-Email')
    if iap_email:
        if "accounts.google.com:" in iap_email:
            return iap_email.split("accounts.google.com:")[1]
        return iap_email
    return os.getenv("LOCAL_DEV_EMAIL", "local.dev@fallback.com")

@app.context_processor
def inject_global_vars():
    return dict(current_user_email=get_current_user_email())

# --- ROUTES ---
@app.route('/')
def home():
    ReturnOFExperienceList = Returnonexperienceentrymodel.query.order_by(Returnonexperienceentrymodel.date_created.desc()).all()
    return render_template('home.html', ReturnOFExperienceList=ReturnOFExperienceList)

@app.route('/create', methods=['GET', 'POST'])
def Add():
    form = ReturnOFExperienceForm()
    form.ProjectNameAndNumber.choices = get_projectname_choices()
    form.Region.choices = get_region_choices()
    form.REXInitiator.choices = get_rexinitiator_choices()
    form.REXInitiatingDiscipline.choices = get_rexinitiatingdiscipline_choices()
    form.REXOnDiscipline.choices = get_rexondiscipline_choices()
    if request.method == 'POST':
        try:
            returnonexperienceentrymodel = Returnonexperienceentrymodel(
               ProjectNameAndNumber_id=form.ProjectNameAndNumber.data,
               Region_id=form.Region.data,
               REXInitiatingDiscipline_id=form.REXInitiatingDiscipline.data, 
               REXInitiator_id=form.REXInitiator.data,
               REXOnDiscipline_id=form.REXOnDiscipline.data,
               REXOnTopic=form.REXOnTopic.data,
               REXDescription=form.REXDescription.data,
               Impact=form.Impact.data,
               AttachmentLink=form.AttachmentLink.data,
               Recommendation=form.Recommendation.data
            )
            db.session.add(returnonexperienceentrymodel)
            db.session.commit()
            flash(f'Success! Your form has been submitted.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
                db.session.rollback()
                print(f"Error saving objects: {e}") 
                return "There was an issue adding your ReturnOFExperienceForm"
    else:
        return render_template('Add.html', title="Return on Experience", form=form)

def returnonexperiencedatalist(id):
    Returnonexperience_item = Returnonexperienceentrymodel.query.get_or_404(id)
    returnOFExperienceform = ReturnOFExperienceForm(
        ProjectNameAndNumber=Returnonexperience_item.ProjectNameAndNumber_id,
        Region=Returnonexperience_item.Region_id,
        REXInitiator=Returnonexperience_item.REXInitiator_id,
        REXInitiatingDiscipline=Returnonexperience_item.REXInitiatingDiscipline_id,
        REXOnDiscipline=Returnonexperience_item.REXOnDiscipline_id,
        REXOnTopic=Returnonexperience_item.REXOnTopic,
        REXDescription=Returnonexperience_item.REXDescription,
        Impact=Returnonexperience_item.Impact,
        AttachmentLink=Returnonexperience_item.AttachmentLink,
        Recommendation=Returnonexperience_item.Recommendation,
    ) 
    returnOFExperienceform.ProjectNameAndNumber.choices =get_projectname_choices()
    returnOFExperienceform.Region.choices =get_region_choices()
    returnOFExperienceform.REXInitiator.choices = get_rexinitiator_choices()
    returnOFExperienceform.REXInitiatingDiscipline.choices =get_rexinitiatingdiscipline_choices()
    returnOFExperienceform.REXOnDiscipline.choices = get_rexondiscipline_choices()
    return returnOFExperienceform

def rexCommitteedatalist(id):
    RexCommitteeModel_item = RexCommitteeModel.query.filter_by(parentid=id).first()
    rexCommitteeModelForm = RexCommitteeModelForm(obj=RexCommitteeModel_item) if RexCommitteeModel_item else RexCommitteeModelForm()
    rexCommitteeModelForm.ReviewCommiteeMember.choices =get_reviewcommiteemember_choices()
    rexCommitteeModelForm.Mentor.choices =get_mentor_choices()
    rexCommitteeModelForm.ActionBy.choices =get_actionby_choices()
    rexCommitteeModelForm.QMSSpoc.choices =get_qmsspoc_choices()
    rexCommitteeModelForm.Technology.choices =get_technology_choices()
    return rexCommitteeModelForm

def actionplandatalist(id):
    ActionPlanModel_item = ActionPlanModel.query.filter_by(parentid=id).first()
    actionPlanModelForm = ActionPlanForm(obj=ActionPlanModel_item) if ActionPlanModel_item else ActionPlanForm()
    actionPlanModelForm.AttendeesOfRootCause.choices =get_attendeesofrootcause_choices()
    actionPlanModelForm.FrequesncyOfIssue.choices = get_frequencyofissue_choices()
    actionPlanModelForm.EHSRisk.choices = get_ehsrisk_choices()
    actionPlanModelForm.DocummentToUpdate.choices = get_documenttoupdate_choices()
    return actionPlanModelForm

def reviewByCommitteedatalist(id):
    ReviewByCommittee_item = ReviewByCommitteeModel.query.filter_by(parentid=id).first()
    return ReviewByCommitteeForm(obj=ReviewByCommittee_item) if ReviewByCommittee_item else ReviewByCommitteeForm()

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    Returnonexperience_item = Returnonexperienceentrymodel.query.get_or_404(id)
    return render_template('Update.html', 
                           returnOFExperienceform=returnonexperiencedatalist(id),
                           rexCommitteeModelForm=rexCommitteedatalist(id),
                           actionPlanModelForm=actionplandatalist(id),
                           reviewByCommitteeForm=reviewByCommitteedatalist(id),
                           status = Returnonexperience_item.status,id=id)

@app.route('/updateRexEntry/<int:id>', methods=['POST'])
def updateRexEntry(id):
    RexCommitteeModel_item = Returnonexperienceentrymodel.query.get_or_404(id) 
    returnOFExperienceform = ReturnOFExperienceForm()
    returnOFExperienceform.ProjectNameAndNumber.choices =get_projectname_choices()
    returnOFExperienceform.Region.choices =get_region_choices()
    returnOFExperienceform.REXInitiator.choices = get_rexinitiator_choices()
    returnOFExperienceform.REXInitiatingDiscipline.choices =get_rexinitiatingdiscipline_choices()
    returnOFExperienceform.REXOnDiscipline.choices = get_rexondiscipline_choices()

    if returnOFExperienceform.validate_on_submit():     
        if RexCommitteeModel_item:
            RexCommitteeModel_item.ProjectNameAndNumber_id = returnOFExperienceform.ProjectNameAndNumber.data
            RexCommitteeModel_item.Region_id = returnOFExperienceform.Region.data
            RexCommitteeModel_item.REXInitiatingDiscipline_id = returnOFExperienceform.REXInitiatingDiscipline.data
            RexCommitteeModel_item.REXInitiator_id = returnOFExperienceform.REXInitiator.data
            RexCommitteeModel_item.REXOnDiscipline_id = returnOFExperienceform.REXOnDiscipline.data 
            RexCommitteeModel_item.REXOnTopic = returnOFExperienceform.REXOnTopic.data
            RexCommitteeModel_item.REXDescription = returnOFExperienceform.REXDescription.data
            RexCommitteeModel_item.Impact = returnOFExperienceform.Impact.data
            RexCommitteeModel_item.AttachmentLink = returnOFExperienceform.AttachmentLink.data
            RexCommitteeModel_item.Recommendation = returnOFExperienceform.Recommendation.data
            RexCommitteeModel_item.status = "RexCommitee"
        try:
            db.session.commit()
            flash(f'Success! Your form has been submitted.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error saving objects: {e}") 
            flash("There was an issue saving to the database.", 'danger')
    else:
        print("Form not validated or GET request.")
        flash(f'Please fill required field.', 'danger')
        Returnonexperience_item = Returnonexperienceentrymodel.query.get_or_404(id)
        return render_template('update.html', rexCommitteeModelForm=rexCommitteedatalist(id),returnOFExperienceform=returnOFExperienceform,actionPlanModelForm=actionplandatalist(id),reviewByCommitteeForm=reviewByCommitteedatalist(id),status = Returnonexperience_item.status,id=id)

@app.route('/updateRexCommittee/<int:id>', methods=['POST'])
def updateRexCommittee(id):
    returnonexperienceentrymodel = Returnonexperienceentrymodel.query.get_or_404(id) 
    rexCommitteeModelForm = RexCommitteeModelForm()
    rexCommitteeModelForm.ReviewCommiteeMember.choices =get_reviewcommiteemember_choices()
    rexCommitteeModelForm.Mentor.choices =get_mentor_choices()
    rexCommitteeModelForm.ActionBy.choices =get_actionby_choices()
    rexCommitteeModelForm.QMSSpoc.choices =get_qmsspoc_choices()
    rexCommitteeModelForm.Technology.choices =get_technology_choices()

    if rexCommitteeModelForm.validate_on_submit():
        RexCommitteeModel_item = RexCommitteeModel.query.filter_by(parentid=id).first()
        def get_data_or_none(field_data): return field_data if field_data not in ('', None) else None

        Isfurtheranalysisrequired = get_data_or_none(rexCommitteeModelForm.Isfurtheranalysisrequired.data)
        Mentor = get_data_or_none(rexCommitteeModelForm.Mentor.data)
        ActionBy = get_data_or_none(rexCommitteeModelForm.ActionBy.data)
        QMSSpoc = get_data_or_none(rexCommitteeModelForm.QMSSpoc.data)
        Technology = get_data_or_none(rexCommitteeModelForm.Technology.data)

        if RexCommitteeModel_item:
            RexCommitteeModel_item.ReviewCommiteeMember = rexCommitteeModelForm.ReviewCommiteeMember.data
            RexCommitteeModel_item.IsitREX = rexCommitteeModelForm.IsitREX.data
            RexCommitteeModel_item.Isfurtheranalysisrequired = Isfurtheranalysisrequired
            RexCommitteeModel_item.Mentor = Mentor
            RexCommitteeModel_item.ActionBy = ActionBy
            RexCommitteeModel_item.QMSSpoc = QMSSpoc
            RexCommitteeModel_item.Technology = Technology
            RexCommitteeModel_item.REXCommitteeComments = rexCommitteeModelForm.REXCommitteeComments.data
        else:
            RexCommittee_item = RexCommitteeModel(
               returnonexperienceentrymodel=returnonexperienceentrymodel,
               ReviewCommiteeMember = rexCommitteeModelForm.ReviewCommiteeMember.data,
               IsitREX = rexCommitteeModelForm.IsitREX.data,
               Isfurtheranalysisrequired = Isfurtheranalysisrequired,
               Mentor = Mentor,
               ActionBy = ActionBy,
               QMSSpoc = QMSSpoc,
               Technology = Technology,
               REXCommitteeComments = rexCommitteeModelForm.REXCommitteeComments.data,
            )
            db.session.add(RexCommittee_item)
            
        if rexCommitteeModelForm.IsitREX.data == 'Yes': returnonexperienceentrymodel.status = 'ActinPlan'
        elif rexCommitteeModelForm.IsitREX.data == 'No': returnonexperienceentrymodel.status = 'Rejected'
        elif rexCommitteeModelForm.IsitREX.data == 'Required more details': returnonexperienceentrymodel.status = 'RexEntry'
        
        try:
            db.session.commit()
            flash(f'Success! Your form has been submitted.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error saving objects: {e}") 
            flash("There was an issue saving to the database.", 'danger')
    else:
        print("Form not validated.")
        flash(f'Please fill required field.', 'danger')
        Returnonexperience_item = Returnonexperienceentrymodel.query.get_or_404(id)
        return render_template('update.html', rexCommitteeModelForm=rexCommitteeModelForm,returnOFExperienceform=returnonexperiencedatalist(id),actionPlanModelForm=actionplandatalist(id),reviewByCommitteeForm=reviewByCommitteedatalist(id),status = Returnonexperience_item.status,id=id)

@app.route('/updatActionPlan/<int:id>', methods=['POST'])
def updatActionPlan(id):
    returnonexperienceentrymodel = Returnonexperienceentrymodel.query.get_or_404(id) 
    RexCommitteeModel_item = RexCommitteeModel.query.filter_by(parentid=id).first()
    Isfurtheranalysisrequired = RexCommitteeModel_item.Isfurtheranalysisrequired
    actionPlanModelForm = ActionPlanForm(external_Isfurtheranalysisrequired_Plan = Isfurtheranalysisrequired,formdata=request.form) 

    actionPlanModelForm.AttendeesOfRootCause.choices =get_attendeesofrootcause_choices()
    actionPlanModelForm.FrequesncyOfIssue.choices = get_frequencyofissue_choices()
    actionPlanModelForm.EHSRisk.choices = get_ehsrisk_choices()
    actionPlanModelForm.DocummentToUpdate.choices = get_documenttoupdate_choices()
    
    if actionPlanModelForm.validate_on_submit():
        ActionPlanModel_item = ActionPlanModel.query.filter_by(parentid=id).first()
        def get_data_or_none(field_data): return field_data if field_data not in ('', None) else None
        AttendeesOfRootCause = get_data_or_none(actionPlanModelForm.AttendeesOfRootCause.data)
        FrequesncyOfIssue = get_data_or_none(actionPlanModelForm.FrequesncyOfIssue.data)
        EHSRisk = get_data_or_none(actionPlanModelForm.EHSRisk.data)
        DocummentToUpdate = get_data_or_none(actionPlanModelForm.DocummentToUpdate.data)

        if ActionPlanModel_item:
            ActionPlanModel_item.AttendeesOfRootCause = AttendeesOfRootCause
            ActionPlanModel_item.Date = actionPlanModelForm.Date.data
            ActionPlanModel_item.FrequesncyOfIssue = FrequesncyOfIssue
            ActionPlanModel_item.EHSRisk = EHSRisk
            ActionPlanModel_item.AddDocumentsLink = actionPlanModelForm.AddDocumentsLink.data
            ActionPlanModel_item.RootCause = actionPlanModelForm.RootCause.data
            ActionPlanModel_item.CorrectiveAction = actionPlanModelForm.CorrectiveAction.data
            ActionPlanModel_item.DocummentToUpdate = DocummentToUpdate
            ActionPlanModel_item.Remarks = actionPlanModelForm.Remarks.data
            ActionPlanModel_item.AttachmentLink = actionPlanModelForm.AttachmentLink.data
            ActionPlanModel_item.ReportingManagerConfirmation = actionPlanModelForm.ReportingManagerConfirmation.data
        else:
            ActionPlan_item = ActionPlanModel(
               returnonexperienceentrymodel=returnonexperienceentrymodel,
               AttendeesOfRootCause = AttendeesOfRootCause,
               Date = actionPlanModelForm.Date.data,
               FrequesncyOfIssue = FrequesncyOfIssue,
               EHSRisk = EHSRisk,
               AddDocumentsLink = actionPlanModelForm.AddDocumentsLink.data,
               RootCause = actionPlanModelForm.RootCause.data,
               CorrectiveAction = actionPlanModelForm.CorrectiveAction.data,
               DocummentToUpdate = DocummentToUpdate,
               Remarks = actionPlanModelForm.Remarks.data,
               AttachmentLink = actionPlanModelForm.AttachmentLink.data,
               ReportingManagerConfirmation = actionPlanModelForm.ReportingManagerConfirmation.data
            )
            db.session.add(ActionPlan_item)
        try:
            returnonexperienceentrymodel.status = 'ReviewByCommittee'
            db.session.commit()
            flash(f'Success! Your form has been submitted.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error saving objects: {e}") 
            flash("There was an issue saving to the database.", 'danger')
    else:
        print("Form not validated.")
        flash(f'Please fill required field.', 'danger')
        Returnonexperience_item = Returnonexperienceentrymodel.query.get_or_404(id)
        return render_template('update.html', rexCommitteeModelForm=rexCommitteedatalist(id),returnOFExperienceform=returnonexperiencedatalist(id),actionPlanModelForm=actionPlanModelForm,reviewByCommitteeForm=reviewByCommitteedatalist(id),status = Returnonexperience_item.status,id=id)

@app.route('/updatReviewByCommittee/<int:id>', methods=['POST'])
def updatReviewByCommittee(id):
    returnonexperienceentrymodel = Returnonexperienceentrymodel.query.get_or_404(id) 
    form = ReviewByCommitteeForm() 
    if request.method == 'POST':
        ReviewByCommitteeModel_item = ReviewByCommitteeModel.query.filter_by(parentid=id).first()
        if ReviewByCommitteeModel_item:
              ReviewByCommitteeModel_item.Remarks = form.Remarks.data
        else:
            ReviewByCommittee_item = ReviewByCommitteeModel(returnonexperienceentrymodel=returnonexperienceentrymodel, Remarks = form.Remarks.data)
            db.session.add(ReviewByCommittee_item)
        
        if form.submit_save.data: returnonexperienceentrymodel.status = 'Closed'       
        elif form.submit_sendback.data: returnonexperienceentrymodel.status = 'ActinPlan'
        
        try:
            db.session.commit()
            flash(f'Success! Your form has been submitted.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error saving objects: {e}") 
            flash("There was an issue saving to the database.", 'danger')
            return "There was an issue Update your Form"
    else:
        return render_template('Update.html')    

@app.route('/delete/<int:id>')
def delete(id):
    task = Returnonexperienceentrymodel.query.get_or_404(id) 
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception: return 'There was a problem deleting'

@app.route('/upload', methods=['GET'])
def upload_view(): return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: flash('No file part'); return redirect(request.url)
    file = request.files['file']
    if file.filename == '': flash('No selected file'); return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # WARNING: This saves to ephemeral storage!
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully')
        return render_template('upload.html', filename=file.filename)
    else:
        flash('Invalid file type'); return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view_files')
def view_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except:
        files = []
    return render_template('view_files.html', files=files)

@app.errorhandler(404)
def not_found_error(error): return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Only create tables if needed. 
        # For Cloud SQL, it is better to use the script I gave you earlier, 
        # but this is fine for initial dev testing.
        db.create_all() 
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))