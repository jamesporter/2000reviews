from google.appengine.ext import db

class Review(db.Model):
    #Content
    title = db.StringProperty()
    content = db.TextProperty()

    #Rating Stuff
    ratings = ["Classic", "Great","Good" ,"Okay","Poor","None"]
    descriptions = ["You must experience these.", "Highly recommended.","Worth experiencing but not essential." ,
                    "Acceptable; I didn't regret it but I wouldn't really recommend it.","Avoid.","For some reason a rating was not applicable."]
    rating = db.StringProperty()

    #Category stuff
    categories = ["Book", "Film", "TV", "Audio", "Game", "Performance", "Other"]
    category = db.StringProperty()

    #Date
    creationDate = db.DateTimeProperty(auto_now_add=True)
    editDate = db.DateTimeProperty(auto_now_add=True)

    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])