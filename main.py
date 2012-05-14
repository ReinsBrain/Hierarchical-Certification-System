import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import Member


import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')




class MainPage(webapp.RequestHandler):
    def get(self):
        template_file = 'anonymous.html'
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            template_values = {'url': url,'url_linktext': url_linktext}
            if users.is_current_user_admin(): template_file = 'templates/admin/admin.html'
            else:
                #check member database and pull member.level
                member = Member.get_by_key_name(user.email())
                if member:
                    url = users.create_logout_url(self.request.uri)
                    url_linktext = 'Logout'
                    member.title = "Registered Member"
                    template_file = 'templates/anonymous.html'
                    if member.level is None:
                        template_file = 'templates/anonymous.html'
                    else:
                        # retrieve certifications for storage in template_values
                        if member.level == LevelsEnum.BEGINNER:
                            member.title = "Kiteboard Beginner"
                            template_file = 'templates/rider/beginner.html'
                        elif member.level == LevelsEnum.INTERMEDIATE:
                            member.title = "Kiteboard Intermediate"
                            template_file = 'templates/rider/intermediate.html'
                        elif member.level == LevelsEnum.RIDER:
                            member.title = "Kiteboard Rider"
                            template_file = 'templates/rider/rider1.html'
                        elif member.level == LevelsEnum.RIDER2:
                            member.title = "Kitebaord Advanced Rider"
                            template_file = 'templates/rider/rider2.html'
                        elif member.level == LevelsEnum.INSTRUCTOR1:
                            member.title = "Kiteboard Instructor Level I"
                            template_file = 'templates/instructor/instructor1.html'
                        elif member.level == LevelsEnum.INSTRUCTOR2:
                            member.title = "Kiteboard Instructor Level II"
                            template_file = 'templates/instructor/instructor2.html'
                        elif member.level == LevelsEnum.INSTRUCTOR3:
                            member.title = "Kiteboard Instructor Level III"
                            template_file = 'templates/instructor/instructor3.html'
                        elif member.level == LevelsEnum.EXAMINER:
                            member.title = "Examiner"
                            template_file = 'templates/examiner/examiner1.html'
                        elif member.level == LevelsEnum.EXAMINER2:
                            member.title = "Senior Examiner"
                            template_file = 'templates/examiner/examiner2.html'
                        elif member.level == LevelsEnum.MASTER:
                            member.title = "Master Examiner"
                            template_file = 'templates/master/master.html'
                        else:
                            #raise and handle error: member.level is beyond LevelsEnum constraints - invalid state.
                            pass
                    template_values = {'url': url,'url_linktext': url_linktext, 'member':member }
                else:
                    # a google user but not registered
                    url = users.create_logout_url(self.request.uri)
                    url_linktext = 'Logout'
                    template_file = 'templates/anonymous.html'
                    template_values = {'url': url,'url_linktext': url_linktext, 'register':True}
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login|Register'
            template_file = 'templates/anonymous.html'
            template_values = {'url': url,'url_linktext': url_linktext, 'loginregister':True}

        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/', MainPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()