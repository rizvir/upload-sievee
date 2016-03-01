#!/usr/bin/env python
# Upload Sievee
# by RizviR

# (note that Webix (the JS library used) is GPLv3)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from flask import Flask, render_template, request, url_for, g, json, jsonify, redirect, session
import yaml
import json
import sqlalchemy
import datetime
import os
from random import randint
from sqlalchemy import create_engine,  Table, Column, Integer, String, MetaData, select, and_, or_
from werkzeug import secure_filename
from mailer import Mailer, Message
import re

app = Flask(__name__)

app.config.from_pyfile('settings.cfg')
app.secret_key = app.config['SECRET_KEY']

appdir = os.path.abspath(os.path.dirname(__file__))

@app.before_request
def before_request():
	g.questions = yaml.load(open(os.path.join(appdir, 'questions.yaml'), 'r'))

	try:
		g.engine = create_engine('mysql://{user}:{password}@{ip}/{db}'.format(user=app.config['SQL_USER'], 
			password=app.config['SQL_PASSWORD'], ip=app.config['SQL_IP'], db=app.config['SQL_DB']), strategy='threadlocal', pool_recycle=280)
		meta = MetaData()
		g.candidates = Table('candidates', meta, autoload=True, autoload_with=g.engine)
		g.conn = g.engine.connect()
	except Exception, e:
		app.logger.error("Error connecting to the database: {0}".format(str(e)))
		return "Error connecting to the database. Try again later.", 503
		
@app.teardown_request
def teardown_request(exception):
	conn = getattr(g, 'conn', None)
	if conn is not None:
		conn.invalidate()

@app.route("/")
def intro_page():
	# We don't support mobile yet
	# Taken from http://detectmobilebrowsers.com/
	reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
	reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)

	user_agent = request.headers.get('User-Agent',None)
	if user_agent:
		b = reg_b.search(user_agent)
		v = reg_v.search(user_agent[0:4])
		if b or v:
			return "<html><span style='font-size: 12px'> Please apply for this position on a laptop or a desktop, because it involves writing answers and uploading your CV that may be difficult on a mobile.<br><br>Visit this site again on a desktop/laptop.</span></html>"

	return render_template('intro.html', allowback=1)

@app.route("/not_first_step")
def not_first_step():
	return render_template('not_first_step.html')

@app.route("/information", methods=['GET', 'POST'])
def information():
	if request.method != "POST":
		return render_template('not_first_step.html')
	# Get all the candidate details and save it in the session
	candidate_name = request.form['name']
	candidate_email = request.form['email']
	candidate_phone = request.form['phone']

	session['name'] = candidate_name
	session['email'] = candidate_email
	session['phone'] = candidate_phone
	ipaddress = request.remote_addr
	useragent = request.headers.get('User-Agent')

	# Insert into DB
	result = g.conn.execute (  g.candidates.insert().values(name=candidate_name, 
		email=candidate_email, phone=candidate_phone, ip=ipaddress, 
		useragent=useragent, entry_date=datetime.datetime.now()) )
	candidate_id = result.inserted_primary_key[0]
	session['id'] = candidate_id

	# Create the ID dir in the repo directory
	path = app.config['REPO_DIR'] + '/' + str(candidate_id)
	if not os.path.exists(path):
		os.makedirs(path)

	return render_template('information.html')

def get_question(questionID, section):
	for question in g.questions[section]:
		if question['id'] == questionID:
			return question['question']
	return ""

def is_answer_correct(questionID, answer):
	# Look for the question ID in the questions YAML
	for question in g.questions['basic-questions']:
		if question['id'] == questionID:
			if question['answer'] == answer.strip():
				return True
	# Answer is not correct
	# Record the incorrect attempts in a text file
	path = "{0}/{1}/basic_questions.txt".format(app.config['REPO_DIR'], session['id'])
	if not is_int(session['id']):
		return "Unexpected ID"
	with open(path, 'a') as basic_questions_file:
		for question in g.questions['basic-questions']:
			if question['id'] == questionID:
				question_string = question['question']
				correct_answer = question['answer']
				basic_questions_file.write('Question: {0}\n'.format(question_string))
				basic_questions_file.write('Correct Answer: {0}\n'.format(correct_answer))
				basic_questions_file.write('Incorrect answer given: {0}\n'.format(answer.encode('ascii','ignore').decode('ascii')))
				basic_questions_file.write('\n')
	return False

# Expects something from a javascript POST like
# { question01: "the answer we got for question01",  question02: "another answer" }
def get_incorrect_questions(answers):
	incorrect_questions = []
	for questionID, value in answers.iteritems():
		if not is_answer_correct(questionID, value):
			incorrect_questions.append(questionID);
	return incorrect_questions
	

@app.route("/basic_questions", methods=['GET', 'POST'])
def basic_questions():
	if not 'id' in session:
		return render_template('not_first_step.html')
	
	# We should have just come back from the information page
	# Fill in some stuff
	g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(read_intro=True))
	# Only set the start time if it isn't already there, otherwise it'd be overwritten in a refresh
	existing_basic_questions_start = g.conn.execute( select([g.candidates]).where(g.candidates.c.id == session['id']) ).fetchone()['basic_questions_start']
	if not existing_basic_questions_start:
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(basic_questions_start=datetime.datetime.now()))

	return render_template('basic_questions.html', questions=g.questions['basic-questions'])

def is_int(s):
	try:
		int(s)
		return True
	except:
		return False

@app.route("/basic_questions_check", methods=['GET', 'POST'])
def basic_questions_check():
	if request.method != "POST":
		return render_template('not_first_step.html')
	if not 'id' in session:
		return render_template('not_first_step.html')
	# We're trusting the id value in creating the path
	if not is_int(session['id']):
		return "Unexpected ID"
	incorrect_questions = get_incorrect_questions(request.form)
	
	# Increment the attempts in the DB
	num_incorrect = len(incorrect_questions)
	g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values( basic_questions_incorrect=g.candidates.c.basic_questions_incorrect + num_incorrect ))
	
			
	
	return jsonify( { "incorrect_questions": incorrect_questions } )

@app.route("/basic_questions_check_animation", methods=['GET', 'POST'])
def basic_questions_check_animation():
	if request.method != "POST":
		return "Invalid request"
	if not 'id' in session:
		return render_template('not_first_step.html')


	# 'request.form' is a ImmutableMultiDict, so copy it to make it RW to remove the time
	request_form = request.form.copy()
	# Get the time_away given by the JS script
	try:
		time_away = str(request_form.pop("time_away", None))
	except:
		time_away = 0
	
	# Double check if all answers are correct
	incorrect_questions = get_incorrect_questions(request_form)
	if len(incorrect_questions) == 0:
		# All answers correct. Store the info.
		# The finish time of the basic quetions:
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(basic_questions_end=datetime.datetime.now()))
		# Calculate the total time spent on basic_questions
		start_time = g.conn.execute( select([g.candidates]).where(g.candidates.c.id == session['id']) ).fetchone()['basic_questions_start']
		total_time_datetime = datetime.datetime.now() - start_time
		total_time_seconds = total_time_datetime.total_seconds()
		# Time spent away from the page
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(basic_questions_timeaway=time_away))

		# Now write the time taken to the basic_questions.txt file
		path = "{0}/{1}/basic_questions.txt".format(app.config['REPO_DIR'], session['id'])
		if not is_int(session['id']):
			return "Unexpected ID"
		with open(path, 'a') as basic_questions_file:
			basic_questions_file.write('Total time taken: {0:.2f} seconds\n'.format(float(total_time_seconds)))
			basic_questions_file.write('Total time spent away from page: {0:.2f} seconds\n'.format(float(time_away)))
		

		return render_template('basic_questions_check_animation.html', randomnum=randint(1,999999))
	else:
		return "Having fun fooling around?"


@app.route("/extra_questions", methods=['GET', 'POST'])
def extra_questions():
	if not 'id' in session:
		return render_template('not_first_step.html')
	request_form = request.form.copy()
	if request.method == "POST":
		# We got the answers.
		# First pop the time_away variable
		try:
			time_away = str(request_form.pop("time_away", None))
		except:
			time_away = 0

		# Then save the time
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(extra_questions_end=datetime.datetime.now()))
		# Calculate total time
		start_time = g.conn.execute( select([g.candidates]).where(g.candidates.c.id == session['id']) ).fetchone()['extra_questions_start']
		total_time_datetime = datetime.datetime.now() - start_time
		total_time_seconds = total_time_datetime.total_seconds()
		# Time spent away from the page
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(extra_questions_timeaway=time_away))
		
		# Save the questions into a text file
		path = "{0}/{1}/extra_questions.txt".format(app.config['REPO_DIR'], session['id'])
		if not is_int(session['id']):
			return "Unexpected ID"
		with open(path, 'a') as extra_questions_file:
			for questionID, value in request_form.iteritems():
				extra_questions_file.write('Question: {0}\n'.format( get_question(questionID, 'extra-questions') ) )
				extra_questions_file.write('Answer: {0}\n'.format( value.encode('ascii','ignore').decode('ascii') ) )
				extra_questions_file.write('\n' )
			extra_questions_file.write('Total time taken: {0:.2f} seconds\n'.format(float(total_time_seconds)))
			extra_questions_file.write('Total time spent away from page: {0:.2f} seconds\n'.format(float(time_away)))

		# Done, now redirect to nontech questions
		return redirect( url_for('nontech_questions'))

	else:
		# Record time
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(extra_questions_start=datetime.datetime.now()))
		return render_template('extra_questions.html', questions=g.questions['extra-questions'])
	

@app.route("/nontech_questions", methods=['GET', 'POST'])
def nontech_questions():
	if not 'id' in session:
		return render_template('not_first_step.html')
	if request.method == "POST":
		# Save the questions into a text file
		path = "{0}/{1}/nontech_questions.txt".format(app.config['REPO_DIR'], session['id'])
		with open(path, 'a') as nontech_questions_file:
			for questionID, value in request.form.iteritems():
				nontech_questions_file.write('Question: {0}\n'.format( get_question(questionID, 'nontech-questions') ) )
				nontech_questions_file.write('Answer: {0}\n'.format( value.encode('ascii','ignore').decode('ascii') ) )
				nontech_questions_file.write('\n' )

		# Now redirect to CV upload page
		return redirect( url_for('cv_upload'))
	else:
		return render_template('nontech_questions.html', questions=g.questions['nontech-questions'])

@app.route("/cv_upload", methods=['GET', 'POST'])
def cv_upload():
	if not 'id' in session:
		return render_template('not_first_step.html')
	if request.method == "POST":
		# Getting a file upload
		path = "{0}/{1}/cv_upload".format(app.config['REPO_DIR'], session['id'])
		# Check if this makes sense
		if not os.path.realpath(path).startswith(app.config['REPO_DIR']):
			return "403", 403
		if not is_int(session['id']):
			return "Unexpected ID", 403
		if not os.path.exists(path):
			os.makedirs(path)
		f = request.files['upload']
		if not app.config['DEMO_MODE']:
			f.save(path + "/" + secure_filename(f.filename))
		
		# Record that everything is completed
		g.conn.execute( g.candidates.update().where(g.candidates.c.id == session['id']).values(cv_uploaded=True))
		
		return "{ status: 'server'}"
	else:
		return render_template('cv_upload.html')

@app.route("/finished")
def finished():
	if not 'id' in session:
		return render_template('not_first_step.html')
	report = send_email(session['id'])
	return render_template('finished.html', randomnum=randint(1,999999), report=report, demo_mode=app.config['DEMO_MODE'])
	

# Reads the repo filesystem and fetches the answers to a question
# 'filename' can be basic_questions.txt, extra_questions.txt, etc
def get_answers(ID, filename):
	path = "{0}/{1}/{2}".format(app.config['REPO_DIR'], ID, filename)
	try:
		with open(path, 'r') as f:
			return f.read()
	except: 
		return ""
	

def send_email(ID):
	# Construct email, this is a biggie
	body = ""
	this_candidate_info = dict( g.conn.execute( select([g.candidates]).where(g.candidates.c.id == ID) ).fetchone().items() )

	# We have to figure out if this potential devil saw the questions before
	# This isn't fool proof of course, but can catch most attempts where they 
	# see the questions, close the window, research the answers, and try again.

	# Get a list of IDs that match the candidates email address, phone number
	# or (hesitated on this one) IP, and crucially those IDs in the DB that 
	# haven't completed the submission
	this_candidate_email = this_candidate_info['email']
	this_candidate_phone = this_candidate_info['phone']
	this_candidate_ip = this_candidate_info['ip']
	subject = "[Candidate] {0}".format(this_candidate_email)
	
	possible_candidates = g.conn.execute( select(['*']).where(
		and_(
			g.candidates.c.cv_uploaded == False,
			or_(
				g.candidates.c.email == this_candidate_email,
				g.candidates.c.phone == this_candidate_phone,
				g.candidates.c.ip    == this_candidate_ip,
			)
		)
	))
	
	attempts = []
	for candidate in possible_candidates:
		attempts.append( dict(candidate.items()) )

	attempts.append(this_candidate_info)
	# At this points, attempts[] has all the candidates attempts

	multiple_attempts = True if len(attempts) > 1 else False

	body += "Candidate info:\n"
	for attempt in attempts:
		if multiple_attempts:
			body += "--- Attempt ID {0} ---\n".format(attempt['id'])
		body += "- Name: {0}\n".format(attempt['name'])
		body += "- Email: {0}\n".format(attempt['email'])
		body += "- Phone: {0}\n".format(attempt['phone'])
		body += "- IP address: {0}\n".format(attempt['ip'])
		body += "- Browser: {0}\n".format(attempt['useragent'])
		body += "- Time: {0}\n".format(attempt['entry_date'])
		body += "\n"

	
	for code,title in [ ('basic_questions','Basic Questions'),  ('extra_questions','Extra Questions'), ('nontech_questions', 'Nontech Questions') ]:
		body += "_" * 60
		body += "\n"
		body += "{0}:\n\n".format(title)
		for attempt in attempts:
			if multiple_attempts:
				body += "--- Attempt ID {0} ---\n".format(attempt['id'])
			if attempt.get('{0}_start'.format(code), None)  and not attempt.get('{0}_end'.format(code), None):
				body += "The candidate saw the questions without attempting any on {0}\n\n".format(attempt['basic_questions_start'])
				continue
			# Now copy the .txt for this ID blindly
			body += get_answers(attempt['id'], '{0}.txt'.format(code))
			body += "\n"

	app.logger.debug(body)

	# Actually send the email:
	if not app.config['DEMO_MODE']:
		message = Message(From=app.config['MAIL_FROM'], To=app.config['MAIL_TO'])
		message.Subject = subject
		message.Body = body
		# Get attachments, all files in the repo ID
		path = "{0}/{1}/cv_upload".format(app.config['REPO_DIR'], this_candidate_info['id'])
		for filename in os.listdir(path):
			file_location = "{0}/{1}".format(path, filename)
			message.attach(file_location)
			app.logger.debug("Attaching {0}".format(file_location))
		sender = Mailer(app.config['MAIL_SERVER'])
		sender.send(message)
		return ""
	else:
		return body


if __name__ == "__main__":
	app.debug = True
	app.run(host="0.0.0.0")

