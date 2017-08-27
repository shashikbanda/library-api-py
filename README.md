# library-api

### About
This is a RESTful API written in Python using the webapp2 framework, hosted on Google Cloud. 

This API models a library. Each library has books. There are multiple classes of user accounts. There are owners, authors, and regular. Only owners can add books to a library. Only authors can create new books. Regular users don’t have any special functions. All three classes of users can “check out” or add books to their user account.

A book can be created and can be added to a library’s collection. When adding to the library, the user species in the post request the quantity he/she wishes to add. Only if a user ID with a role of owner is specified in the URL can a book be added to the library.


Live Link @ : https://library-app-176821.appspot.com

### API Documentation

Coming Soon...
