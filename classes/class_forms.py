import sys
sys.path.append('lib')
import wtforms
#from wtforms import validators

class ClassForm(wtforms.Form):
    studio_name = wtforms.StringField()
    source_page = wtforms.StringField()
    style = wtforms.StringField()
    teacher = wtforms.StringField()
    teacher_link = wtforms.StringField()
    start_time = wtforms.DateTimeField()
    end_time = wtforms.DateTimeField()
    #latitude = wtforms.FloatField()
    #longitude = wtforms.FloatField()
    #scrape_time = wtforms.DateTimeField()
