#!/usr/bin/env python

from models import Review
import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
import datetime as dt
import json
from collections import OrderedDict


def stringify(db_object):
    return str(db_object.key())


def format_datetime(value):
    #British!
    return value.strftime('%d/%m/%Y')


def describe(rating):
    return Review.descriptions[Review.ratings.index(rating)]

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates/"))

jinja_environment.filters['datetime'] = format_datetime
jinja_environment.filters['stringify'] = stringify
jinja_environment.filters['description'] = describe


class MainHandler(webapp2.RequestHandler):
    def get(self):
        index_text = memcache.get("index")
        if not index_text:
            count = Review.all(keys_only=True).count()
            last_twelve = Review.gql("ORDER BY creationDate DESC LIMIT 12")
            percentage = count/20.0
            if percentage > 100.0:
                percentage = 100
            template = jinja_environment.get_template("index.html")
            index_text = template.render({"categories":Review.categories, "percentage":percentage, "numReviews":count, "latestReviews":last_twelve})
            memcache.add("index", index_text)
        self.response.out.write(index_text)


class EditHandler(webapp2.RequestHandler):
    def get(self, serialised_key):
        if users.is_current_user_admin():
            template = jinja_environment.get_template("edit.html")
            if serialised_key:
                review = db.get(db.Key(encoded=serialised_key))
                if review:
                    self.response.out.write(template.render({"categories":Review.categories, "ratings":Review.ratings, "title":review.title, "content":review.content, "savedCategory":review.category, "savedRating":review.rating}))
                else:
                    self.error(404)
            else:
                self.response.out.write(template.render({"categories":Review.categories, "ratings":Review.ratings}))
        elif users.get_current_user():
            self.redirect("/nopermission")
        else:
            self.redirect(users.create_login_url(self.request.url))

    def post(self, serialised_key):
        if users.is_current_user_admin():
            #Either fetch review or create one
            review = None
            if serialised_key:
                review = db.get(db.Key(encoded=serialised_key))
            if not review:
                review = Review()
            #Add/update contents
            review.title = self.request.get('title')
            review.content = self.request.get('content')
            category = self.request.get('category')
            if category in Review.categories:
                review.category = category
            else:
                review.category = Review.categories[-1]  #i.e Other

            rating = self.request.get('rating')
            if rating in Review.ratings:
                review.rating = rating
            else:
                review.rating = Review.ratings[-1]   #i.e. N/A
            review.editDate = dt.datetime.now()
            review.put()
            self.redirect("/")
        else:
            self.redirect("/")


class ViewHandler(webapp2.RequestHandler):
    def get(self, category):
        template = jinja_environment.get_template("view.html")
        if users.is_current_user_admin():
            if category and category in Review.categories:
                reviews_collection = OrderedDict()
                for rating in Review.ratings:
                    reviews = Review.gql("WHERE rating = '%s' AND category = '%s'" % (rating, category))
                    if reviews.count() > 0:
                        reviews_collection[rating] = reviews
                self.response.out.write(template.render({"reviewsCollection": reviews_collection, "admin":True,"categories":Review.categories, "category":category}))
            else:
                reviews_collection = OrderedDict()
                for rating in Review.ratings:
                    reviews = Review.gql("WHERE rating = '%s'" % rating)
                    if reviews.count() > 0:
                        reviews_collection[rating] = reviews
                self.response.out.write(template.render({"reviewsCollection":reviews_collection, "admin":True,"categories":Review.categories}))
        #Not admin so cache etc
        else:
            if category and category in Review.categories:
                reviews_text = memcache.get("/view/%s" % category)
                if reviews_text is None:
                    reviews_collection = OrderedDict()
                    for rating in Review.ratings:
                        reviews = Review.gql("WHERE rating = '%s' AND category = '%s'" % (rating, category))
                        if reviews.count() > 0:
                            reviews_collection[rating] = reviews
                    reviews_text = template.render({"reviewsCollection":reviews_collection, "admin":False,"categories":Review.categories, "category":category})
                    memcache.add("/view/%s" % category, reviews_text)
            else:
                reviews_text = memcache.get("/view")
                if reviews_text is None:
                    reviews_collection = OrderedDict()
                    for rating in Review.ratings:
                        reviews = Review.gql("WHERE rating = '%s'" % rating)
                        if reviews.count() > 0:
                            reviews_collection[rating] = reviews
                    reviews_text = template.render({"reviewsCollection":reviews_collection, "admin":False,"categories":Review.categories})
                    memcache.add("/view", reviews_text)
            self.response.out.write(reviews_text)


class ExportHandler(webapp2.RequestHandler):
    """
    Export (if admin, else bounce)
    """
    def get(self):
        if not users.is_current_user_admin():
            self.redirect("/nopermission")
        else:
            reviews = Review.all()
            self.response.out.write(json.dumps([r.to_dict() for r in reviews]))



class NoPermissionHandler(webapp2.RequestHandler):
    def get(self):
        nop_text = memcache.get("/nopermission")
        if not nop_text:
            template = jinja_environment.get_template("error.html")
            nop_text = template.render({"categories":Review.categories, "title":"Admin only", "message":"You must be a site admin to access this page.", "type":"warning"})
            memcache.add("/nopermission", nop_text)
        self.response.status = 403
        self.response.out.write(nop_text)


####################################################
######          Wire up:                     #######
####################################################

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/write/?([-A-z0-9]+)?', EditHandler),
    ('/view/?([-A-z0-9]+)?', ViewHandler),
    ('/nopermission', NoPermissionHandler),
    ('/reviews.json', ExportHandler)
], debug=False)


def handle_404(request, response, exception):
    template = jinja_environment.get_template("error.html")
    response.write(template.render({"title":"Page not found"}))
    response.set_status(404)

app.error_handlers[404] = handle_404
