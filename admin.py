import os
import logging
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from LevelsEnum import LevelsEnum
from google.appengine.ext import db
from LoggedModels import CertificationTemplate
from LoggedModels import Element
from LoggedModels import Task
from LoggedModels import Certification
from LoggedModels import ElemScore
from LoggedModels import Member

class CertificationsPage(webapp.RequestHandler):
    def get(self):
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        # if there is a 'id' in query string then it is a view for a specific cert...
        if self.request.get('certid'):
            cid = int(self.request.get('certid'))
            template_file = 'templates/admin/cert.html'
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
            template_file = 'templates/admin/certs.html'
            cs_query = Certification.all()
            cs = cs_query.fetch(100)
            for c in cs:
                c.id = c.key().id()
                c.templatekeyname = c.template.key().name()
            #get all cert_temps
            ctemps_query = CertificationTemplate.all()
            ctemps = ctemps_query.fetch(100)
            for ctemp in ctemps:
                ctemp.code4 = ctemp.key().name()
            template_values = {'url': url,'url_linktext': url_linktext,'certs': cs, 'ctemps':ctemps}
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))

    def post(self):
        method = self.request.get('method')
        cert_id = None
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
                    else: level = 0
                    c.completed = True
                    c.owner.level = level
                    #updated Member's level using an algorithm to evaluate elements
            if c.put() and c.completed:
                #triggers an email to email
                pass
            self.redirect('/admin/certifications')
        elif method == "delete":
            # delete the record and related scores
            c = Certification.get_by_id(cert_id)
            for s in c.scores:
                s.delete()
            c.delete()
            self.redirect('/admin/certifications')
            # todo : adjust level
        else:
            # a new post
            c = Certification()
            template = CertificationTemplate.get_by_key_name(templatekey)

            c.template = template
            mem = Member.get_by_key_name(email)
            # goddamit, email should be the keyname for a member!!!
            if mem:
                #... what if the fnam and lnam are different? an update?
                pass
            else:
                # create a new member
                mem = Member(key_name=email,fnam=fnam,lnam=lnam)
                mem.put()
                # todo : don't forget to send them an email to confirm membership!!!
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
                else: level = 0
                mem.level = level
            mem.put()
            c.owner = mem
            c.put()
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
            self.redirect('/admin/members?memberkey=' + email)


class TemplatesPage(webapp.RequestHandler):
    def get(self):
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        # if there is a 'key' in query string then it is a view for a specific template...
        if self.request.get('keyname'):
            kn = self.request.get('keyname')
            template_file = 'templates/admin/cert_temp.html'
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            ctemp = CertificationTemplate.get_by_key_name(kn)
            if ctemp:
                ctemp.code4 = ctemp.key().name()
                ctemp.els = ctemp.elements
            template_values = {'url': url,'url_linktext': url_linktext,'ctemp': ctemp}
        else:
            template_file = 'templates/admin/cert_temps.html'
            ctemps_query = CertificationTemplate.all()
            ctemps = ctemps_query.fetch(100)
            for ctemp in ctemps:
                ctemp.code4 = ctemp.key().name()
                if ctemp.prereq:
                    ctemp.p = ctemp.prereq.key().name()
            template_values = {'url': url,'url_linktext': url_linktext,'ctemps': ctemps}
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))
    def post(self):
        p = self.request.get('prereq')
        short = self.request.get('short')
        desc = self.request.get('desc')
        key3 = self.request.get('key3')
        method = self.request.get('method')
        if key3:
            ctemp = CertificationTemplate.get_by_key_name(key3)
            if method == "update":
                # an edit
                if p:
                    pr = CertificationTemplate.get_by_key_name(p)
                    ctemp.prereq = pr
                if short: ctemp.short = short
                if desc: ctemp.desc = desc
                ctemp.put()
            elif method == "delete":
                # a deletion
                # first delete all dependencies
                # ctemp.elements
                for el in ctemp.elements:
                    el.elem.delete()
                    el.delete()
                ctemp.delete()
        else:
            # a new post
            if p:
                ctp = CertificationTemplate.get_by_key_name(p)
                ctemp = CertificationTemplate(key_name=key3)
                ctemp.short = short
                ctemp.desc = desc
                ctemp.prereq = ctp
                ctemp.put()
            else:
                ctemp = CertificationTemplate(key_name=key3, short=short)
                ctemp.short = short
                ctemp.desc = desc
                ctemp.put()

        self.redirect('/admin/templates')

class ElementsPage(webapp.RequestHandler):
    def post(self):
        method =  self.request.get('method')
        ctkey = self.request.get('ctkey') # required for redirect
        elkey = self.request.get('elkey')
        if method == 'delete':
            k = db.Key.from_path("Element", elkey)
            db.delete(k)
        elif method == 'update' or method == 'post':
            short = self.request.get('short')
            desc = self.request.get('desc')
            note = self.request.get('note')
            prereq = self.request.get('prereq')
            # save or update the element or task
            if method == 'post':
                ordstr = self.request.get('ord')
                ord = int(ordstr)
                ct = CertificationTemplate.get_by_key_name(ctkey)
                if ct:
                    kn = ctkey + '-' + ordstr
                    el = Element(key_name=kn,certtemp=ct,short=short,ord=ord)
                    # continue setting Element fields
                    if desc: el.desc = desc
                    if note: el.note = note
                    if prereq:
                        el_pre = Element.get_by_key_name(prereq)
                        if el_pre: el.prereq = el_pre
                        else:
                            # todo : raise error - Element prereq does not exist
                            pass
                    elkey = el.put()
                else:
                    # todo - raise error - can't create Element without CertificationTemplate
                    pass
            else:  # method == 'update'
                el = Element.get_by_key_name(elkey)
                if el:
                    # update element
                    if desc : el.desc = desc
                    if note : el.note = note
                    if prereq:
                        el_pre = Element.get_by_key_name(prereq)
                        if el_pre: el.prereq = el_pre
                        else:
                            # todo : raise error - Element prereq does not exist
                            pass
                    elkey = el.put()
                else:
                    # todo raise error - can't located Element to update
                    pass

        else:
            # todo : raise error - method not supplied or supported
            pass
        self.redirect('/admin/templates?keyname='+ctkey)

class TasksPage(webapp.RequestHandler):
    def post(self):
        method =  self.request.get('method')
        ctkey = self.request.get('ctkey') # required for redirect
        tskkey = self.request.get('tskkey')
        short = None
        desc = None
        note = None
        prereq = None
        if method == 'delete':
            k = db.Key.from_path("Task", tskkey)
            db.delete(k)
        elif method == 'update' or method == 'post':
            if self.request.get('short'): short = self.request.get('short')
            if self.request.get('desc'): desc = self.request.get('desc')
            if self.request.get('note'): note = self.request.get('note')
            if self.request.get('prereq'): prereq = self.request.get('prereq')
            # save or update the element or task
            if method == 'post':
                ordstr = self.request.get('ord')
                ord = int(ordstr)
                elkey = self.request.get('elkey')
                el = Element.get_by_key_name(elkey)
                if el:
                    kn = elkey + '-' + ordstr
                    tsk = Task(key_name=kn,element=el,short=short,ord=ord)
                    # continue setting Element fields
                    if desc: el.desc = desc
                    if note: el.note = note
                    if prereq:
                        tsk_pre = Task.get_by_key_name(prereq)
                        if tsk_pre: tsk.prereq = tsk_pre
                        else:
                            # todo : raise error - Task prereq does not exist
                            pass
                    tskkey = tsk.put()
                else:
                    # todo - raise error - can't create Task without Element
                    pass
            else:  # method == 'update'
                tskkey = self.request.get('tskkey')
                tsk = Task.get_by_key_name(tskkey)
                if tsk:
                    # update Task
                    if desc : tsk.desc = desc
                    if note : tsk.note = note
                    if prereq:
                        tsk_pre = Task.get_by_key_name(prereq)
                        if tsk_pre: tsk.prereq = tsk_pre
                        else:
                            # todo : raise error - Task prereq does not exist
                            pass
                    tskkey = tsk.put()
                else:
                    # todo raise error - can't located Task to update
                    pass

        else:
            # todo : raise error - method not supplied or supported
            pass
        self.redirect('/admin/templates?keyname='+ctkey)

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
        cert = Certification.get_by_id(certid)
        complete = True
        for s in cert.scores:
            if s.score == 0:
                complete = False
                break
        if complete:
            cert.completed = True
            cert.put()
        self.redirect('/admin/certifications?certid='+self.request.get('certid'))

class MembersPage(webapp.RequestHandler):
    def get(self):
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        # provide an email: get one, no email, get all
        mkey = self.request.get('memberkey')
        if mkey:
            # get specific member
            member = Member.get_by_key_name(mkey)
            ctemps_query = CertificationTemplate.all()
            ctemps = ctemps_query.fetch(100)
            template_file = 'templates/admin/member.html'
            template_values = {'url': url,'url_linktext': url_linktext,'member': member, 'ctemps': ctemps}
        else:
            # get all members
            members = Member.all()
            template_file = 'templates/admin/members.html'
            template_values = {'url': url,'url_linktext': url_linktext,'members': members}
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_values))
    def post(self):
        # provide an email: get one, no email, get all
        mkey = self.request.get('memberkey')
        if mkey:
            # get specific member
            member = Member.get_by_key_name(mkey)
            method = self.request.get('method')
            if method == 'delete':
                # delete member and his certs and scores
                for cert in member.certifications:
                    for sc in cert.scores:
                        sc.delete()
                    cert.delete()
                member.delete()
                self.redirect('/admin/members')
            elif method == 'update':
                # get admin changeable properties
                if self.request.get('level'): member.level = int(self.request.get('level'))
                if self.request.get('fnam'): member.fnam = self.request.get('fnam')
                if self.request.get('lnam'): member.lnam = self.request.get('lnam')
                member.put()
                self.redirect('/admin/members?memberkey=' + mkey)
        else:
            # no action to be done
            self.redirect('/admin/members')

application = webapp.WSGIApplication([
('/admin/templates', TemplatesPage),
('/admin/elements', ElementsPage),
('/admin/tasks', TasksPage),
('/admin/certifications', CertificationsPage),
('/admin/scores', ScoresPage),
('/admin/members', MembersPage),
],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()