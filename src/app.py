# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
from pprint import pprint
from sqlalchemy.orm import load_only
from sqlalchemy import and_
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    jsonify)
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import sys

# -- Models --
from models import *

# ------------
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.app = app
db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    city_states = db.session.query(Venue.city, Venue.state).distinct()

    # import ipdb
    # ipdb.set_trace()

    response = []
    for c_s in city_states:
        pprint(c_s)
        # dictionary with mixed keys
        my_dict = {
            'city': c_s.city,
            'state': c_s.state,
            'venues': db.session
            .query(Venue)
            .filter(and_(Venue.city == c_s.city, Venue.state == c_s.state))
            .order_by(Venue.name)
            .all()
        }
        response.append(my_dict)

    pprint(response)

    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = "%{}%".format(request.form.get('search_term', ''))
    result = Venue.query.filter(Venue.name.ilike(search)).all()
    response = {
        "count": len(result),
        "data": result
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = Venue.query.get(venue_id)
    data.past_shows = list(map(lambda s: __showParse(s), data.past_shows))
    data.upcoming_shows = list(
        map(lambda s: __showParse(s), data.upcoming_shows))
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        input = request.form
        genres = input['genres']
        form = VenueForm(input)
        venue = Venue()
        form.populate_obj(venue)
        venue.seeking_talent = True if input['seeking_talent'] == 'y' else False
        genre: Genre = Genre.query.filter_by(name=genres).first()
        venue.genres = []
        venue.genres.append(genre)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully added!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be listed.', 'error')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

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
    response = {
        "count": len(result),
        "data": result
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    data.past_shows = list(map(lambda s: __showParse(s), data.past_shows))
    data.upcoming_shows = list(
        map(lambda s: __showParse(s), data.upcoming_shows))
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
    data.upcoming_shows = list(
        map(lambda s: __showParse(s), data.upcoming_shows))
    form.name.data = data.name
    form.city.data = data.city
    form.genres.data = [(c.id, c.name) for c in data.genres]
    form.image_link.data = data.image_link
    form.phone.data = data.phone
    form.website_link.data = data.website
    form.seeking_description.data = data.seeking_description
    form.seeking_venue.data = data.seeking_venue
    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website = request.form['website_link']
        genres = request.form['genres']
        seeking_venue = request.form['seeking_venue']
        seeking_description = request.form['seeking_description']

        genre: Genre = Genre.query.filter_by(name=genres).first()

        artist: Artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description)

        artist.genres.append(genre)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully added!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist could not be listed.', 'error')
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    data: Venue = Venue.query.get(venue_id)
    data.upcoming_shows = list(
        map(lambda s: __showParse(s), data.upcoming_shows))
    form.name.data = data.name
    form.genres.data = [(c.id, c.name) for c in data.genres]
    form.address.data = data.address
    form.city.data = data.city
    form.state.data = data.state
    form.phone.data = data.phone
    form.website_link.data = data.website
    form.facebook_link.data = data.facebook_link
    form.seeking_talent.data = data.seeking_talent
    form.seeking_description.data = data.seeking_description
    form.image_link.data = data.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website = request.form['website_link']
        genres = request.form['genres']
        seeking_talent = request.form['seeking_talent']
        seeking_description = request.form['seeking_description']

        genre: Genre = Genre.query.filter_by(name=genres).first()
        venue: Venue = Venue.query.filter_by(id=venue_id).first()

        venue.name = name,
        venue.city = city,
        venue.state = state,
        venue.address = address,
        venue.phone = phone,
        venue.image_link = image_link,
        venue.facebook_link = facebook_link,
        venue.website = website,
        venue.seeking_talent = seeking_talent,
        venue.seeking_description = seeking_description

        venue.genres.append(genre)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be listed.', 'error')
        print(sys.exc_info())
    finally:
        db.session.close()
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
    form = ArtistForm(request.form)

    try:
        genres = request.form['genres']
        genre: Genre = Genre.query.filter_by(name=genres).first()

        artist: Artist = Artist()
        form.populate_obj(artist)
        artist.seeking_venue = True if request.form['seeking_venue'] == 'y' else False
        genre: Genre = Genre.query.filter_by(name=genres).first()
        
        artist.genres = []
        artist.genres.append(genre)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist could not be listed.', 'error')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    #       num_shows should be aggregated based on number of upcoming shows per venue
    error = False
    data = []
    try:
        print('about to chekc the shows')
        result = Show.query.all()
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
    # called upon submitting the new artist listing form
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        venue_fields = ["id", "name"]
        venue: Venue = Venue.query.filter_by(
            id=venue_id).options(load_only(*venue_fields)).first()

        artitst_fields = ["id", "name", "image_link"]
        artist: Artist = Artist.query.filter_by(
            id=artist_id).options(load_only(*artitst_fields)).first()

        show: Show = Show(
            venue_id=venue_id,
            venue_name=venue.name,
            artist_id=artist_id,
            artist_name=artist.name,
            artist_image_link=artist.image_link,
            start_time=start_time
        )

        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.', 'error')
        print(sys.exc_info())
    finally:
        db.session.close()

    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(401)
def not_found_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def not_found_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


def __showParse(show: Show):
    show.start_time = show.start_time.strftime("%d-%b-%Y %H:%M:%S")
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
