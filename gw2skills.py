import cgi
import os
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Skill(db.Model):
    """A skill entry to put in the database, it contains:
    name
    description
    combo_type
    profession
    race
    """
    name = db.StringProperty()
    description = db.StringProperty()
    combo_type = db.StringProperty(choices=set("field", "physical_projectile", "blast_finisher", "whirl_finisher", "leap_finisher"))
    field_type = db.StringProperty(choices=set("dark", "ethereal", "fire",
                                               "ice", "light", "lightning",
                                               "poison", "smoke", "water"))

class Greeting(db.Model):
    """Models in a Guestbook entry"""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    content_2 = db.StringProperty()

def guestbook_key(guestbook_name=None):
    "Construct a datastore key for a guestbook entity with a guestbookname"
    return db.Key.from_path("Guestbook", guestbook_name or "default_guestbook")


class MainPage(webapp.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name')

        # Doing a strongly consistent ancestor query
        greetings = db.GqlQuery("SELECT * "
                                "FROM Greeting "
                                "WHERE ANCESTOR IS :1 "
                                "ORDER BY date DESC LIMIT 10",
                                 guestbook_key(guestbook_name))
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        template_values = {
        'greetings' : greetings,
        'url': url,
        'url_linktext': url_linktext}

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
class Guestbook(webapp.RequestHandler):
    def post(self):
        guestbook_name = self.request.get("guestbook_name")
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/?' + urllib.urlencode({"guestbook_name":
                                               cgi.escape(guestbook_name)}))

application = webapp.WSGIApplication([('/', MainPage),
                                      ("/sign", Guestbook)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()