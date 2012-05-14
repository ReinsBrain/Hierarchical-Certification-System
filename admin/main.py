import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import Member


class TemplatesPage(webapp.RequestHandler):
    def get(self):
        template_file = 'anonymous.html'
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            template_values = {'url': url,'url_linktext': url_linktext,}
            if users.is_current_user_admin():
                template_file = 'admin.html'
            else:
                self.redirect("/")
        else:
            self.redirect("/")


application = webapp.WSGIApplication([('/admin/templates', TemplatesPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()