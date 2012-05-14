from google.appengine.ext import db

class LoggedModel(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    createdBy = db.UserProperty(auto_current_user_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    modifiedBy = db.UserProperty(auto_current_user=True)

#email is keyname
class Member(LoggedModel):
    fnam = db.StringProperty(required=True)
    lnam = db.StringProperty(required=True)
    user = db.UserProperty()
    #levels null:member,0:beginner,1:intermediate,2:rider,3:advrider,4:instructor1,5:instructor2,6:instructor3,7:examiner,8:master
    level = db.IntegerProperty()

# abstract
class CertTempBase(LoggedModel):
    #code4 = db.StringProperty(required=True) # now the keyname
    short = db.StringProperty(required=True) # a heading (under 40)
    desc = db.StringProperty() # a proper description (under 200)
    note = db.StringProperty() # an information aside for instructors

# self reference prereq by assigning parent
class CertificationTemplate(CertTempBase):
    prereq = db.SelfReferenceProperty(collection_name='requiredby') # prerequisite Certification

class Element(CertificationTemplate):
    certtemp = db.ReferenceProperty(CertificationTemplate, collection_name='elements')
    ord = db.IntegerProperty(required=True)

class Task(Element):
    element = db.ReferenceProperty(Element, collection_name='tasks')
    # example: this.element.certtemp.short

class Certification(LoggedModel):
    template = db.ReferenceProperty(CertificationTemplate, collection_name='certifications')
    owner = db.ReferenceProperty(Member, collection_name='certifications')
    completed = db.BooleanProperty()

class ElemScore(LoggedModel):
    certification = db.ReferenceProperty(Certification, collection_name='scores')
    certtemp_elem = db.ReferenceProperty(Element)
    score = db.IntegerProperty()
    completed = db.BooleanProperty()

class TaskScore(LoggedModel):
    elemscore = db.ReferenceProperty(ElemScore, collection_name='taskscores')
    certtemp_task = db.ReferenceProperty(Task)
    score = db.IntegerProperty()
