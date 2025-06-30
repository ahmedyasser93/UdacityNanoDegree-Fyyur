#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
#from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from models import db, Venue, Artist, Show


app = Flask(__name__)
app.config.from_object(config)  
db.init_app(app)
migrate = Migrate(app, db)
# Set the csrf token for Flask-WTF if needed
app.config['WTF_CSRF_ENABLED'] = False
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

  venues = Venue.query.order_by(Venue.city, Venue.state).all()
    
  grouped_data = []
  location_map = {}

  for venue in venues:
        key = (venue.city, venue.state)
        if key not in location_map:
            location_map[key] = {
                'city': venue.city,
                'state': venue.state,
                'venues': []
            }
            grouped_data.append(location_map[key])

        location_map[key]['venues'].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([
                show for show in venue.shows if show.start_time > datetime.now()
            ])
        })

  return render_template('pages/venues.html', areas=grouped_data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  count = len(venues)
  response = {
    "count": count,
    "data": []
  }
  for venue in venues:
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter((Show.venue_id==venue.id) & (Show.start_time > datetime.now())).count()
    })
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  
  shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
  data = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []

  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
      })
    else:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
      })
  
  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
  data.past_shows_count = len(past_shows)
  data.upcoming_shows_count = len(upcoming_shows)
 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  if form.validate():
    # called to create new shows in the db, upon submitting new show listing form
    venue = Venue(name=form.name.data, 
                  city=form.city.data, 
                  state=form.state.data, 
                  address=form.address.data, 
                  phone=form.phone.data, 
                  genres=form.genres.data, 
                  image_link=form.image_link.data, 
                  facebook_link=form.facebook_link.data, 
                  seeking_talent=form.seeking_talent.data, 
                  seeking_description=form.seeking_description.data
                  )
      #Modify data to be the data object returned from db insertion
    try:
      db.session.add(venue)
      db.session.commit()
        # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
      db.session.rollback()
      
      #on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue could not be listed.')
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    flash('An error occurred. Venue could not be listed.')

    return render_template('forms/new_venue.html', form=form)

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

  data =  Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = len(artists)
  response = {
    "count": count,
    "data": []
  }
  for artist in artists:
    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter((Show.artist_id==artist.id) & (Show.start_time > datetime.now())).count()
    })


  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = Artist.query.get(artist_id)
  shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()

  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat()
      })
    else:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat()
      })
  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
  data.past_shows_count = len(past_shows)
  data.upcoming_shows_count = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)  # Prefill form with artist data

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  #if form.validate():
  artist = Artist.query.get(artist_id)

  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.image_link = form.image_link.data
  artist.facebook_link = form.facebook_link.data
  artist.website = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  try:
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))
 # else:
 #   flash('An error occurred. Artist could not be updated.')
 #   return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)  # Prefill form with venue data

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    try:
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully updated!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('An error occurred. Venue could not be updated.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)

  if form.validate():
    # insert form data as a new artist record in the db, instead
    artist = Artist(name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    image_link=form.image_link.data,
                    facebook_link=form.facebook_link.data,
                    website=form.website_link.data,
                    seeking_venue=form.seeking_venue.data,
                    seeking_description=form.seeking_description.data
                  )
    try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    flash('An error occurred. Artist could not be listed.')
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm(request.form)
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate():
    show = Show(artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
              )
    try:
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
    flash('An error occurred. Show could not be listed.')
    return render_template('forms/new_show.html', form=form)       

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
