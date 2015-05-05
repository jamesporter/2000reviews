# 2000reviews

A simple Google App Engine Python App to create quick reviews (and allowing bulk json data export).

* Quickly and easily write and update reviews.
* Categories
* JSON export
* Mostly memcached
* Secure accounts (thanks to Google)

You should be able to set up your own scalable review site using this project without even knowing Python. Just follow the guide below.

# Getting Started

Sign up for a [Google App Engine](http://appengine.google.com) account. Create a new App (make a note of the app name you will need it shortly).

Download/install Google App Engine for your Operating System.

Clone this repo (or just download it via link on the left).

# Things you need to/should change

Having downloaded this repo:

Open app.yaml and change the application: APP_NAME to your name.

Open models.py and customise the review ratings and categories for your own use.

If you aren't British you may want to open up main.py and change the date formatting to something New World-y.

Customise (or remove) Google Analytics. For example by deleting

`{% include "google-tracking.html" %}`

from base.html

Then deploy. On Windows of Mac you can use the little Google App Engine Launcher App to do this for you.

Note that due to caching changes may not be immediately available. You might want to manually clear out the cache to see changes immediately.

# Optional

The default look is boring Bootstrap default. You might want to drop in something nicer. [Bootswatch](http://bootswatch.com/) is one good/easy/free option.

If you want anyone to be able to easily export your reviews you might want to edit the ExportHandler (just remove the admin check). You might want to cache this data as it is a relatively expensive operation (at least once there are more than a few reviews).
