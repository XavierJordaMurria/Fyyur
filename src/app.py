#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from pprint import pprint
import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only, column_property
from sqlalchemy import and_
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venus_generes_pivot = db.Table('venus_generes_pivot',
    db.Column('genere_id', db.Integer, db.ForeignKey('Genere.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

artists_generes_pivot = db.Table('artists_generes_pivot',
    db.Column('genere_id', db.Integer, db.ForeignKey('Genere.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

class Genere(db.Model):
    __tablename__ = 'Genere'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    generes = db.relationship('Genere', 
                              secondary=venus_generes_pivot)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # past_shows = db.relationship("Show")
    upcoming_shows = db.relationship("Show")
    # upcoming_shows = db.relationship("Show",
    #                 primaryjoin="and_(Show.start_time >= 'func.now()')")

    # past_shows_count = column_property(func.count('past_shows'))
    # upcoming_shows_count = column_property(func.count('upcoming_shows'))
    def __repr__(self):
      return f'''<Venue {self.id}, {self.name}, {self.city}>'''

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    generes = db.relationship('Genere',
                              secondary=artists_generes_pivot, lazy='subquery')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # past_shows = db.relationship("Show")
    upcoming_shows = db.relationship("Show")
    # past_shows = db.relationship("Show",
    #                 primaryjoin="and_(Show.start_time < 'func.now()')")
    # upcoming_shows = db.relationship("Show",
    #                 primaryjoin="and_(Show.start_time >= 'func.now()')")

    # past_shows_count = column_property(func.count('past_shows'))
    # upcoming_shows_count = column_property(func.count('upcoming_shows'))

    def __repr__(self):
      return f'''<Artist {self.id}, {self.name}, {self.city}>'''
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  venue_name = db.Column(db.String(120))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  artist_name = db.Column(db.String(120))
  artist_image_link = db.Column(db.String(500))
  start_time = db.Column(db.DateTime)

  def __repr__(self):
    return f'''<Show {self.id}, {self.venue_id}, {self.venue_name}, {self.artist_id}, {self.artist_name}, {self.start_time}>'''

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  city_states = db.session.query(Venue.city, Venue.state).distinct()

  response = []
  for c_s in city_states:
    pprint(c_s)
    # dictionary with mixed keys
    my_dict = {
      'city': c_s.city,
      'state': c_s.state,
      'venues' : db.session
        .query(Venue)
        .filter(and_(Venue.city==c_s.city, Venue.state==c_s.state))
        .order_by(Venue.name)
        .all()
    }
    response.append(my_dict)
  
  pprint(response)

  return render_template('pages/venues.html', areas=response);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = "%{}%".format(request.form.get('search_term', ''))
  result = Venue.query.filter(Venue.name.ilike(search)).all()
  response={
    "count": len(result),
    "data": result
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = Venue.query.get(venue_id)
  data.upcoming_shows = list(map(lambda s: __showParse(s),data.upcoming_shows))
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  body = {}
  req = request.form
  print(req)
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    generes = request.form['generes']
    seeking_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    venue = Venue(
              name = name,
              city = city,
              state = state,
              address = address,
              phone = phone,
              image_link = image_link,
              facebook_link = facebook_link,
              website = website,
              generes = generes,
              seeking_talent = seeking_talent,
              seeking_description = seeking_description)


    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully added!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue could not be listed.', 'error')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  rows = ["id", "name"]
  data = db.session.query(Artist).options(load_only(*rows)).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search = "%{}%".format(request.form.get('search_term', ''))
  result = Artist.query.filter(Artist.name.ilike(search)).all()
  response={
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  data.upcoming_shows = list(map(lambda s: __showParse(s),data.upcoming_shows))
  return render_template('pages/show_artist.html', artist=data)

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = Artist.query.get(artist_id)
  data.upcoming_shows = list(map(lambda s: __showParse(s),data.upcoming_shows))
  form.name.data = data.name
  form.city.data = data.city
  form.genres.data = [(c.id, c.name) for c in data.generes ]
  form.image_link.data = data.image_link
  form.phone.data = data.phone
  form.website_link.data = data.website
  form.seeking_description.data = data.seeking_description
  form.seeking_venue.data = data.seeking_venue
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue
  error = False
  data=[]
  try:
    print('about to chekc the shows')
    result=Show.query.all()
    db.session.commit()

    data = list(map(lambda s: __showParse(s), result))
    [print(show) for show in data]

    print(f'Loaden {len(data)} shows')
  except Exception as e: 
    error = True
    print(e)
    print('something went wrng')
    db.session.rollback()
  finally:
    print('finally')
    db.session.close()

  if not error:
    return render_template('pages/shows.html', shows=data)
  else:
    abort(500)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

def __showParse(show):
  show.start_time =  show.start_time.strftime("%d-%b-%Y %H:%M:%S")
  return show
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True) 

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
