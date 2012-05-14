import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import Member

class RegisterPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                #redirect
                pass
            else:
                #check member database and pull member.level
                q = db.GqlQuery("SELECT * FROM Member WHERE user = :1", user)
                member = q.get()
                if member:
                    #redirect
                    pass
                else:
                    # a google user but not registered
                    url = users.create_login_url(self.request.uri)
                    url_linktext = 'Login'
                    template_file = 'templates/register.html'
                    template_values = {'url': url,'url_linktext': url_linktext, 'login':True}
        else:
            #it is possible they are a google, tell them to login if they are
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            template_file = 'templates/register_modal.html'
            template_values = {'url': url,'url_linktext': url_linktext, 'login':True}

        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))

    def post(self):
        user = users.get_current_user()
        if user:
            fnam = self.request.get('fnam')
            lnam = self.request.get('lnam')
            mem = Member(key_name=user.email(),fnam=fnam,lnam=lnam,user=user)
            mem.put()
            self.redirect('/')

application = webapp.WSGIApplication([('/register', RegisterPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()