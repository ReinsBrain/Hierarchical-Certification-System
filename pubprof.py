import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import Member

class PubProfPage(webapp.RequestHandler):
    def get(self):
        template_file = 'templates/pubprof.html'
        profile = self.request.get('profile')
        if profile:
            # parse email from escaped profile parameter
            parsedemail = profile
            member = Member.get_by_key_name(parsedemail)
            for c in member.certifications:
                if c.completed > 0: pass
                else: c.incomplete = True
            template_values = {'member':member}
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/public', PubProfPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()