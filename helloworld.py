import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import datetime
import urllib
import webapp2
import simplejson

from google.appengine.ext import db
from google.appengine.api import users


class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
        


class Guestbook(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    guestbook_name = self.request.get('guestbook_name')
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

class RESTfulHandler(webapp2.RequestHandler):
    
    
    def get(self, id):
        #guestbook_name = self.request.get('guestbook_name')
        greetings_query = Greeting.all().order('-date')
        
        json_output = []

        for item in greetings_query:
            json_output.append({ "name"     : item.author.nickname(),
                                 "content" : item.content,
                                 "date" : item.date.strftime("%A %d. %B %Y"),})
         
           
	json_output = simplejson.dumps(json_output)
	self.response.out.write(json_output)
        
        
#            def get(self, id):
#	key = self.request.cookies['todos']
#	todolist = db.get(key)
#	todos = []
#	query = Todos.all()
#	query.filter("todolist =", todolist.key())
#	for todo in query:
#	    todos.append(todo.toDict())
#	todos = simplejson.dumps(todos)
#	self.response.out.write(todos)
#
#
#    def post(self, id):
#	key = self.request.cookies['todos']
#	todolist = db.get(key)
#	todo = simplejson.loads(self.request.body)
#	todo = Todos(todolist = todolist.key(),
#		     order   = todo['order'],
#		     content = todo['content'],
#		     done    = todo['done'])
#	todo.put()
#	todo = simplejson.dumps(todo.toDict())
#	self.response.out.write(todo)
#
#    def put(self, id):
#	key = self.request.cookies['todos']
#	todolist = db.get(key)
#	todo = Todos.get_by_id(int(id))
#	if todo.todolist.key() == todolist.key():
#	    tmp = simplejson.loads(self.request.body)
#	    todo.content = tmp['content']
#	    todo.done    = tmp['done']
#	    todo.put()
#	    todo = simplejson.dumps(todo.toDict())
#	    self.response.out.write(todo)
#	else:
#	    self.error(403)
#
#    def delete(self, id):
#	key = self.request.cookies['todos']
#        todolist = db.get(key)
#	todo = Todos.get_by_id(int(id))
#	if todo.todolist.key() == todolist.key():
#	    tmp = todo.toDict()
#	    todo.delete()
#	else:
#	    self.error(403)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/sign', Guestbook),
                                ('/json\/?([0-9]*)', RESTfulHandler)],
                                #('/json', RESTfulHandler)],
                              debug=True)