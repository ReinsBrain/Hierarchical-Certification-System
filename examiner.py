import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import Member
from LoggedModels import Certification
from LoggedModels import CertificationTemplate
from LoggedModels import ElemScore

class CertificationsPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        member = Member.get_by_key_name(user.email())
        # if there is a 'id' in query string then it is a view for a specific cert...
        if self.request.get('certid'):
            cid = int(self.request.get('certid'))
            template_file = 'templates/examiner/cert.html'
            user = users.get_current_user()
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            c = Certification.get_by_id(cid)
            if c:
                # i dunno
                pass


            #get all cert_temps
            ctemps_query = CertificationTemplate.all()
            ctemps = ctemps_query.fetch(100)
            for ctemp in ctemps:
                ctemp.code4 = ctemp.key().name()
            template_values = {'url': url,'url_linktext': url_linktext,'cert': c, 'ctemps':ctemps}
        else:
            if member.level == 7: member.canteach = [{'level':'KB1'},{'level':'KB2'},{'level':'KB3'},{'level':'IK1','mustscore':True},{'level':'IK2','mustscore':True}]
            elif member.level == 8: member.canteach = [{'level':'KB1'},{'level':'KB2'},{'level':'KB3'},{'level':'IK1',},{'level':'IK2'},{'level':'IK3','mustscore':True}]
            template_file = 'templates/examiner/certs.html'
            cs_query = Certification.gql("WHERE createdBy= :1", users.get_current_user())
            cs = cs_query.fetch(100)
            template_values = {'url': url,'url_linktext': url_linktext, 'member':member,'certs':cs}
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))
    def post(self):
        method = self.request.get('method')
        if self.request.get('id'): cert_id = int(self.request.get('id'))
        email = self.request.get('recipient')
        fnam = self.request.get('fnam')
        lnam = self.request.get('lnam')
        if self.request.get('completed') == '1': completed = True
        else: completed = False
        templatekey = self.request.get('ctemp')
        if method == "update":
            # an edit
            c = Certification.get_by_id(cert_id)
            if completed:
                if c.completed:
                    #already completed
                    pass
                else:
                    #update their level (member record)
                    if templatekey == 'KB1': level = 1
                    elif templatekey == 'KB2': level = 2
                    elif templatekey == 'KB3': level = 3
                    elif templatekey == 'IK1': level = 4
                    elif templatekey == 'IK2': level = 5
                    elif templatekey == 'IK3': level = 6
                    elif templatekey == 'EX1': level = 7
                    elif templatekey == 'EX2': level = 8
                    elif templatekey == 'M': level = 9
                    else: pass
                    c.completed = True
                    c.owner.level = level
                    #updated Member's level using an algorithm to evaluate elements
            if c.put() and c.completed:
                #triggers an email to email
                pass
            self.redirect('/examiner/certifications')
        elif method == "delete":
            # delete the record and related scores
            c = Certification.get_by_id(cert_id)
            for s in c.scores:
                s.delete()
            #also delete the member if there are no other certs related and the member has no user
            mem = c.owner
            c.delete()
            if mem.user: pass
            else:
                memcs = Certification.all()
                memcs = Certification.gql("WHERE owner= :1", c.owner)
                if memcs.count(limit=2) > 0: pass
                else:
                    # also check to see if this user is the creater of the record...
                    if mem.createdBy == users.get_current_user(): mem.delete()

            self.redirect('/examiner/certifications')
            # TODO adjust level
        else:
            # a new post
            c = Certification()
            template = CertificationTemplate.get_by_key_name(templatekey)

            c.template = template
            mem = Member.get_by_key_name(email)
            if (mem):
                #... what if the fnam and lnam are different? an update?
                pass
            else:
                # create a new member
                mem = Member(key_name=email,fnam=fnam,lnam=lnam)
                mem.put()
            if completed:
                c.completed = True
                if templatekey == 'KB1': level = 1
                elif templatekey == 'KB2': level = 2
                elif templatekey == 'KB3': level = 3
                elif templatekey == 'IK1': level = 4
                elif templatekey == 'IK2': level = 5
                elif templatekey == 'IK3': level = 6
                elif templatekey == 'EX1': level = 7
                elif templatekey == 'EX2': level = 8
                elif templatekey == 'M': level = 9
                mem.level = level
            mem.put()
            c.owner = mem
            c.put()
            # Trigger email to certification recipient
            from google.appengine.api import mail
            message = mail.EmailMessage(sender="WorldKiteOrg-DoNotReply <no-reply@worldkite.org>",subject="Congratulations - your WorldKite Certification is completed")
            message.to = mem.key().name()
            message.body = "Congratulations" + mem.fnam + " " + mem.lnam
            message.body += """

"""
            message.body += c.template.key().name() + " " + c.template.short
            message.body += """

Visit http://worldkite.org and login with the email address
you provided for your World Kite certification. We use Google's
system for authentication so if you email account is not already
registered with Google then you will be prompted to do so.

Please let us know if you have any questions by dropping an email to:
support@worldkite.com

Welcome to our team!

World Kite Organization
"""
            message.send()
            # now check the template and create new scores for each Element related to the CertTemp
            # first, get all CertificationTemplate.elements
            for el in template.elements:
                # now for each el, create a new ElemScore
                elsc = ElemScore()
                elsc.certtemp_elem = el
                elsc.certification = c
                if completed: elsc.score = 1
                else: elsc.score = 0
                elsc.put()
            self.redirect('/examiner/certifications?certid=' + str(c.key().id()))

class ScoresPage(webapp.RequestHandler):
    def get(self):
        #
        pass
    def post(self):
        # we need to be able to update scores for an uncompleted certification
        # passing (score) id, score, method (update)
        method = self.request.get('method')
        certid = int(self.request.get('certid'))
        scid = int(self.request.get('id'))
        score =int(self.request.get('score'))
        sc = ElemScore.get_by_id(scid)
        sc.score = score
        sc.put()
        # TODO check to see if all the scores are passing and update cert.completed if so...
        c = Certification.get_by_id(certid)
        completed = True
        for s in c.scores:
            if s.score == 0:
                complete = False
                break
        if completed:
            if c.completed:
                #already completed
                pass
            else:
                c.completed = True
                c.put()
                ctkn = c.template.key().name()
                if ctkn == 'KB1': level = 1
                elif ctkn == 'KB2': level = 2
                elif ctkn == 'KB3': level = 3
                elif ctkn == 'IK1': level = 4
                elif ctkn == 'IK2': level = 5
                elif ctkn == 'IK3': level = 6
                else: level = 0
                c.owner.level = level

            if c.put() and c.completed:
                #triggers an email to email
                c.owner.put()

        self.redirect('/examiner/certifications?certid='+self.request.get('certid'))



application = webapp.WSGIApplication([
    ('/examiner/certifications', CertificationsPage),
    ('/examiner/scores', ScoresPage),
],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()