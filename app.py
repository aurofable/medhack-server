import os

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from twilio import twiml
from twilio.util import TwilioCapability
from twilio.rest import TwilioRestClient

import string
import random

from datetime import datetime

# Declare and configure application
app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('local_settings.py')
db = SQLAlchemy(app)


# Class for DB
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    aux = db.Column(db.Text)
    pic1 = db.Column(db.Text)
    pic2 = db.Column(db.Text)
    pic3 = db.Column(db.Text)

    def __init__(self, first_name, last_name, aux, pic1, pic2, pic3):
        self.first_name = first_name
        self.last_name = last_name
        self.aux = aux
        self.pic1 = pic1
        self.pic2 = pic2
        self.pic3 = pic3
    
    def __repr__(self):
        return "('id', '%s'), ('first_name', '%s'), ('last_name', '%s'), ('aux','%s'), ('pic1', '%s'), ('pic2', '%s'), ('pic3', '%s')" % (self.id, self.first_name, self.last_name, self.aux, self.pic1, self.pic2, self.pic3)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id'        : self.id,
            'first_name': self.first_name,
            'last_name' : self.last_name,
            'aux'       : self.aux,
            'pic1'      : self.pic1,
            'pic2'      : self.pic2,
            'pic3'      : self.pic3
        }



# Voice Request URL
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    caller_id = "+16099526377"
    actionURL = '/trans'
    if request.method == 'GET':
        from_client_number = request.args.get('PhoneNumber')
        #recurl = request.args.get('recurl')
    else:
        from_client_number = request.form['PhoneNumber']
        #recurl = request.form['recurl']

    #print 'RECURL is ' + str(recurl)
    #Native working now!

    response = twiml.Response()
    response.say("Logged In")
    response.dial(action = actionURL, callerId = caller_id, number = from_client_number, record = True)
    print 'Phone number from client is ' + str(from_client_number)
    return str(response)


# SMS Request URL
@app.route('/sms', methods=['GET', 'POST'])
def sms():
    response = twiml.Response()
    response.sms("Congratulations! You deployed the Twilio Hackpack" \
            " for Heroku and Flask.")
    return str(response)


# Twilio Client demo template
@app.route('/clientOLD')
def client():
    configuration_error = None
    for key in ('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_APP_SID',
            'TWILIO_CALLER_ID'):
        if not app.config[key]:
            configuration_error = "Missing from local_settings.py: " \
                    "%s" % key
            token = None
    if not configuration_error:
        capability = TwilioCapability(app.config['TWILIO_ACCOUNT_SID'],
            app.config['TWILIO_AUTH_TOKEN'])
        capability.allow_client_incoming("joey_ramone")
        capability.allow_client_outgoing(app.config['TWILIO_APP_SID'])
        token = capability.generate()
    return render_template('client.html', token=token,
            configuration_error=configuration_error)

# Twilio Authentication for iOS Client
@app.route('/auth')
def auth():
    capability = TwilioCapability(app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN'])
    capability.allow_client_incoming("swarm_user")
    capability.allow_client_outgoing(app.config['TWILIO_APP_SID'])
    token = capability.generate()
    return str(token)


# Transcription
@app.route('/trans', methods=['GET', 'POST'])
def trans():
    print 'Trans called!'
    if request.method == 'GET':
        recURL = request.args.get('RecordingUrl')
        duration = request.args.get('DialCallDuration')
        sid = request.args.get('DialCallSid')
        status = request.args.get('DialCallStatus')
    else:
        recURL = request.form['RecordingUrl']
        duration = request.form['DialCallDuration']
        sid = request.form['DialCallSid']
        status = request.form['DialCallStatus']

    dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    if (recURL == None): 
        recURL = "asdfsadfadsfasdasd"
    if (duration == None):
        duration = 5
    if (sid == None):
        sid = ''.join(random.choice(chars) for x in range(10))
    if (status == None):
        status = "Error"
    
    note = Note(sid, status, duration, recURL, dateTime)
    db.session.add(note)
    db.session.commit()

    response = twiml.Response()
    response.say("Recorded")
    return str(response)

# Register Form
@app.route('/for-patients', methods=['GET', 'POST'])
def reg():
  return 'WORK IN PROGRESS'

# Get Data Route
@app.route('/profile/<int:profID>', methods=['GET', 'POST'])
def prof(profID):
  prof = Profile.query.filter(Profile.id == profID);
  #return 'You Looked at profile ' + str(profID);
  return jsonify(values=[i.serialize for i in prof])
   
# Database
@app.route('/data', methods=['GET', 'POST'])
def data():
    if (len(Profile.query.all()) == 0):
        return 'Database empty'
    return jsonify(values=[i.serialize for i in Profile.query.all()])

# Clear Database
@app.route('/clear', methods=['GET', 'POST'])
def clear():
   for note in Note.query.all():
       db.session.delete(note)
   db.session.commit()
   return 'Database Cleared'

# Reset Database
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return 'Database Reset'


# Dummy Data
@app.route('/dummy', methods=['GET', 'POST'])
def dummy():
    first_name = 'John'
    last_name = 'Smith'
    aux = 'Lorem Ipsum'
    pic1 = 'http://www.google.com'
    pic2 = 'http://www.google.com'
    pic3 = 'http://www.google.com'
    prof = Profile(first_name, last_name, aux, pic1, pic2, pic3)
    db.session.add(prof)

    first_name = 'Jane'
    last_name = 'Smith'
    aux = 'Lorem Ipsum'
    pic1 = 'http://www.google.com'
    pic2 = 'http://www.google.com'
    pic3 = 'http://www.google.com'
    prof = Profile(first_name, last_name, aux, pic1, pic2, pic3)
    db.session.add(prof)
    db.session.commit()

    accnt_sid = app.config['TWILIO_ACCOUNT_SID']
    auth_token = app.config['TWILIO_AUTH_TOKEN']

    client = TwilioRestClient(accnt_sid, auth_token)
    messsage = client.sms.messages.create(to="+14124252207", from_="+16099526377", body="HELP!")
    return 'Dummy Data Added!'

# Debug
@app.route('/client/<int:clientID>', methods=['GET', 'POST'])
def client(clientID):
  prof = Profile.query.filter(Profile.id == clientID);
  param = prof[0].serialize
  print str(param)
  print 'asdfasdfasdf'
  return render_template('client.html', param)

# Index page
@app.route('/')
def index():
  '''  
  params = {
        'voice_request_url': url_for('.voice', _external=True),
        'client_url': url_for('.client', _external=True),
        'auth_url': url_for('.auth', _external=True),
        'trans_url': url_for('.trans', _external=True),
        'data_url' : url_for('.data', _external=True)}
        
    return render_template('index.html', params=params) '''
  return render_template('index.html')

# If PORT not specified by environment, assume development config.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.debug = True
    app.run(host='0.0.0.0', port=port)
    #db.create_all()
