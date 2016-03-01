Ever put up a technical job posting and be inundated with CVs from people who claim to know a lot but actually could hardly even spell what they profess to be good at? 

Upload Sievee (pronounced "Upload CV") is a simple open source job application/CV uploading site, designed to sift candidates by asking them a set of compulsory questions (which they have to answer in order to continue). It's not unduly strict, in that it allows for an unlimited amount of retries as well as feedback of which particular question was answered wrong, but each incorrect attempt is noted in the final report. It's divided into three sections:
- Timed compulsory questions with fixed answers
- Timed optional free-form questions with no particular answers
- Untimed optional free-form or radio-selection questions with no answers
before finally allowing the candidate to upload their CV or any additional files. You then get their report and CV via email (there is no admin web interface to view previous applicants, it's email only)
It has some basic anti-cheating measures in the sense that it could try to guess if the candidate looked at the questions before, but it's far from perfect.


#### Installation:

```
git clone ...
sudo yum install mysql-devel # or mariadb-devel
virtualenv env
source env/bin/activate
pip install -r requirements.txt 
# Then create a MySQL/MariaDB database according to create_db.mysql
mv settings.cfg.example settings.cfg
# Edit settings.cfg with your details.
python upload_sievee.py # Test
# Go to a web browser and check http://yourserver:5000
# or deploy to your webserver via the wsgi file.
```

Customize the text and links on the site by editing `templates/customize.html`, and change the questions by editing the `questions.yaml` file.

