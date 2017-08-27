import webapp2
import json
from datetime import datetime
from google.appengine.ext import ndb

class Library(ndb.Model):
	library_id = ndb.StringProperty(required=True)
	library_name = ndb.StringProperty(required=True)
	library_location = ndb.StringProperty(required=True)
	library_book_info = ndb.JsonProperty()

class Book(ndb.Model):
	book_id = ndb.StringProperty(required=True)
	book_name = ndb.StringProperty(required=True)
	book_author_fname = ndb.StringProperty(required=True)
	book_author_lname = ndb.StringProperty(required=True)
	book_genre = ndb.StringProperty(required=True)

#User types: regular, librarian (only librarian can add books to libs, author (only author can make book)
class User(ndb.Model):
	user_id = ndb.StringProperty()
	user_firstname = ndb.StringProperty()
	user_lastname = ndb.StringProperty()
	user_role = ndb.StringProperty()
	user_books = ndb.JsonProperty()

class LibrarySystem(webapp2.RequestHandler):
	def get(self):
		self.response.write('Main Route.')

class UserHandler(webapp2.RequestHandler):
	def get(self, user_id=None):
		if user_id:
			u = ndb.Key(urlsafe=user_id).get()
			u_dict = u.to_dict()
			self.response.write(json.dumps(u_dict))
		else:
			users = User.query().fetch()
			usersDict = []
			for key in users:
				usersDict.append(key.to_dict())
			# usersDict.to_dict()
			self.response.write(json.dumps(usersDict))

	def post(self):
		user_data = json.loads(self.request.body)
		new_user = User(user_id=user_data['user_id'], user_firstname=user_data['user_firstname'], user_lastname=user_data['user_lastname'], user_role=user_data['user_role'], user_books=user_data['user_books'])
		new_user.put()
		new_user.user_id = new_user.key.urlsafe()
		new_user.put()
		book_dict = new_user.to_dict()
		book_dict['self'] = '/user/' + new_user.key.urlsafe()
		self.response.write(json.dumps(book_dict))

	def delete(self, user_id):
		if user_id:
			u = ndb.Key(urlsafe=user_id).get()
			u.key.delete()
			self.response.write("deleted user.")
		else:
			self.response.write("User ID Does Not Exist.")

#Creates a new library, no id required. library_book_info initially set to {}.
class LibraryHandler(webapp2.RequestHandler):
	def get(self, lib_id=None):
		if lib_id:
			lib = ndb.Key(urlsafe=lib_id).get()
			lib_dict = lib.to_dict()
			self.response.write(json.dumps(lib_dict))
		else:
			libraries = Library.query().fetch()
			librariesDict = []
			for key in libraries:
				librariesDict.append(key.to_dict())
			self.response.write(json.dumps(librariesDict))

	def post(self):
		library_data = json.loads(self.request.body)
		new_lib = Library(library_id = 'asdf', library_name = library_data['library_name'], library_location=library_data['library_location'], library_book_info=library_data['library_book_info'])
		new_lib.put()
		new_lib.library_id = new_lib.key.urlsafe()
		new_lib.put()
		library_dict = new_lib.to_dict()
		library_dict['self'] = '/library/' + new_lib.key.urlsafe()
		self.response.write(json.dumps(library_dict))
	def delete(self, lib_id=None):
		lib = ndb.Key(urlsafe=lib_id).get()
		lib.key.delete()
		self.response.write("deleted library.")

#Add quantity of books to library, only allowed if user has 'owner' status.
class AddBookToLibraryHandler(webapp2.RequestHandler):
	def put(self, library_id, owner_id, book_id):
		if owner_id:
			u = ndb.Key(urlsafe=owner_id).get()
			u_dict = u.to_dict()
			if u_dict['user_role'] == 'owner':
				#do stuff
				put_data = json.loads(self.request.body)
				lib = ndb.Key(urlsafe=library_id).get()
				lib.library_book_info[book_id] = put_data['quantity']
				lib.put()
				lib_dict = lib.to_dict()
				self.response.write(json.dumps(lib_dict))
			else:
				self.response.status = '403'
				self.response.write("Forbidden: Only users with owner status can add books to store.")

#Create a new book, only allowed if user has 'author' status.				
class BookHandler(webapp2.RequestHandler):
	def get(self):
		books = Book.query().fetch()
		booksDict = []
		for key in books:
			booksDict.append(key.to_dict())
		self.response.write(json.dumps(booksDict))

	def post(self, user_id):
		if user_id:
			u = ndb.Key(urlsafe=user_id).get()
			u_dict = u.to_dict()
			if u_dict['user_role'] == 'author':
				book_data = json.loads(self.request.body)
				new_book = Book(book_id='asdf', book_name=book_data['book_name'], book_author_fname=u_dict['user_firstname'], book_author_lname=u_dict['user_lastname'], book_genre=book_data['book_genre'])
				new_book.put()
				new_book.book_id = new_book.key.urlsafe()
				new_book.put()
				book_dict = new_book.to_dict()
				book_dict['self'] = '/book/' + new_book.key.urlsafe()
				self.response.write(json.dumps(book_dict))
			else:
				self.response.status = '403'
				self.response.write("Forbidden: Only users with author status can create books.")

class RemoveBookHandler(webapp2.RequestHandler):
	def delete(self, book_id):
		book = ndb.Key(urlsafe=book_id).get()
		book.key.delete()
		self.response.write("Deleted book.")


class BuyBookHandler(webapp2.RequestHandler):
	def put(self, user_id, book_id, lib_id):
		if lib_id:
			l = ndb.Key(urlsafe=lib_id).get()
			u = ndb.Key(urlsafe=user_id).get()
			if l.library_book_info[book_id] > 0:
				l.library_book_info[book_id] -= 1;
				l.put()
				if book_id in u.user_books:
					u.user_books[book_id] += 1;
					u.put()
				else:
					u.user_books[book_id] = 1;
					u.put()
		#book in stock -- subtract from library total
		self.response.write(json.dumps(u.to_dict()))

#Returns the titles in a specified library along with the quantity remaining.
class LibraryCatelogHandler(webapp2.RequestHandler):
	def get(self, lib_id):
		l = ndb.Key(urlsafe=lib_id).get()
		# l_dict = l.to_dict()
		cat_dict = {}
		for key in l.library_book_info:
			b = ndb.Key(urlsafe=key).get()
			cat_dict[b.book_name] = l.library_book_info[key]
		self.response.write(json.dumps(cat_dict))


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
	('/', LibrarySystem),
	('/library', LibraryHandler),
	('/library/(.*)/catelog', LibraryCatelogHandler),
	('/library/(.*)/owner/(.*)/book/(.*)', AddBookToLibraryHandler), #must be type librarian.
	('/library/(.*)', LibraryHandler),
	('/book', BookHandler),
	('/book/user/(.*)', BookHandler), #user = user_id (must be author)
	('/book/id/(.*)', RemoveBookHandler), 
	('/user', UserHandler),
	('/user/(.*)/buy/book/(.*)/library/(.*)', BuyBookHandler),
	('/user/(.*)', UserHandler)
    
], debug=True)