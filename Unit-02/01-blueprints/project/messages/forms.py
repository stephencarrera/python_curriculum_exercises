from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators



class MessageForm(FlaskForm):
	content=TextAreaField('Content', [validators.DataRequired()], render_kw={"rows": 3, "cols": 30})

class DeleteForm(FlaskForm):
	pass