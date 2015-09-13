import base_servlet
from . import class_models
from . import class_forms

class ClassUploadHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
     return False

    def post(self):
        studio_class = class_models.StudioClass()
        form = class_forms.ClassForm(self.request.POST)
        print self.request.POST
        print form.validate(), form.errors
        if self.request.POST and form.validate():
            form.populate_obj(studio_class)
            studio_class.put()
            return '200'
