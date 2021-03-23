#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for,
  jsonify
)
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Venue, Artist, Show   

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# DONE: connect to a local postgresql database

migrate = Migrate(app, db)

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
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  locations = db.session.query(Venue.city, Venue.state).distinct().all()

  data = []
  
  for city, state in locations:
    new_data = {}
    new_data["city"] = city
    new_data["state"] = state
    new_data["venues"] = []
    venues = Venue.query.filter_by(city=city, state=state).all()
    for venue in venues:
      venue_info = {}
      venue_info['id'] = venue.id
      venue_info['name'] = venue.name
      venue_info['num_upcoming_shows'] = len(venue.shows)
      new_data["venues"].append(venue_info)
    data.append(new_data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  app.logger.info(search_term)

  res = Venue.query.filter(Venue.name.ilike("%"+ search_term +"%")).all()
  data = []
  for venue in res:
    entry = {}
    entry['id'] = venue.id
    entry['name'] = venue.name
    upcomingshows = []
    for show in venue.shows:
      if show.start_time >= datetime.now():
        upcomingshows.append(show)
    entry["num_upcoming_shows"] = len(upcomingshows)
    data.append(entry)
  
  response = {"count": len(data), "data": data}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  data = []
  venues = Venue.query.all()
  
  for venue in venues:
    entry = {}
    entry['id'] = venue.id
    entry['name'] = venue.name
    entry['genres'] = venue.genres 
    entry['address'] = venue.address
    entry['city'] = venue.city
    entry['state'] = venue.state
    entry['phone'] = venue.phone
    entry['website'] = venue.website_link
    entry['facebook_link'] = venue.facebook_link
    entry['seeking_talent'] = venue.seeking_talent
    entry['seeking_description'] = venue.seeking_description
    entry['image_link'] = venue.image_link

    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
      if show.start_time <= datetime.now():
        past_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.showartist.name,
          'artist_image_link': show.showartist.image_link,
          'start_time': str(show.start_time)
        })
      else:
        upcoming_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.showartist.name,
          'artist_image_link': show.showartist.image_link,
          'start_time': str(show.start_time)
        })
      
    entry['past_shows'] = past_shows
    entry['upcoming_shows'] = upcoming_shows
    entry['past_shows_count'] = len(past_shows)
    entry['upcoming_shows_count'] = len(upcoming_shows)

    data.append(entry)

  currvenuedata = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=currvenuedata)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
  try:
    form = VenueForm(request.form, meta={'csrf': False})
    if not form.validate():
      app.logger.info(form.errors)
      error = True

    else:  
      newVenue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(newVenue)
      db.session.commit()
      newVenueName = newVenue.name

  except Exception as err:
    app.logger.error('err = %s', err)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('forms/new_venue.html', form=form)
  else:
    # on successful db insert, flash success
    flash('Venue ' + newVenueName + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # DONE BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  todelete = Venue.query.get(venue_id)
  try:
    db.session.delete(todelete)
    db.session.commit()
  except:
    app.logger.error('Delete Venue Error')
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Venue ' + venue_id + ' could not be deleted')
  else:
    flash('Venue ' + venue_id + ' was successfully deleted')
  return jsonify({
    'redirected': True,
    'url': 'http://127.0.0.1:5000/'
  })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    entry = {}
    entry["id"] = artist.id
    entry["name"] = artist.name
    data.append(entry)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  res = Artist.query.filter(Artist.name.ilike("%"+ search_term +"%")).all()
  data = []
  for artist in res:
    entry = {}
    entry['id'] = artist.id
    entry['name'] = artist.name
    upcomingshows = []
    for show in artist.shows:
      if show.start_time >= datetime.now():
        upcomingshows.append(show)
    entry["num_upcoming_shows"] = len(upcomingshows)
    data.append(entry)
  
  response = {"count": len(data), "data": data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue(artist) page with the given venue_id
  # DONE: replace with real venue(artist) data from the venues(artists) table, using venue(artist)_id
  
  def showinfo(show):
    info = {}
    venue_id = show.venue_id 
    if venue_id is None: return None
    app.logger.info('venue id for {%s} is {%s}', artist_id, venue_id)
    venue = Venue.query.get(venue_id)
    info['venue_id'] = venue.id
    info['venue_name'] = venue.name
    info['venue_image_link'] = venue.image_link
    info['start_time'] = str(show.start_time)
    return info

  try:
    data = []
    artists = Artist.query.all()

    for artist in artists:
      entry = {}
      entry['id'] = artist.id
      entry['name'] = artist.name
      entry['genres'] = artist.genres
      entry['city'] = artist.city
      entry['state'] = artist.state
      entry['phone'] = artist.phone
      entry['website'] = artist.website_link
      entry['facebook_link'] = artist.facebook_link
      entry['seeking_venue'] = artist.seeking_venue
      entry['seeking_description'] = artist.seeking_description
      entry['image_link'] = artist.image_link

      past_shows = []
      upcoming_shows = []
      for show in artist.shows:
        if show.venue_id:
          if show.start_time <= datetime.now():
            past_shows.append({
              'venue_id': show.venue_id,
              'venue_name': show.showvenue.name,
              'venue_image_link': show.showvenue.image_link,
              'start_time': str(show.start_time)
            })
          else:
            upcoming_shows.append({
              'venue_id': show.venue_id,
              'venue_name': show.showvenue.name,
              'venue_image_link': show.showvenue.image_link,
              'start_time': str(show.start_time)
            })

      entry['past_shows'] = past_shows
      entry['upcoming_shows'] = upcoming_shows
      entry['past_shows_count'] = len(past_shows)
      entry['upcoming_shows_count'] = len(upcoming_shows)

      data.append(entry)
  
    currartistdata = list(filter(lambda d: d['id'] == artist_id, data))[0]
    return render_template('pages/show_artist.html', artist=currartistdata)
  
  except Exception as e:
    app.logger.error(e)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  artist = {"id": artist_id, "name": artist.name}
  
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:
    form = ArtistForm(request.form, meta={'csrf': False})
    if not form.validate():
      app.logger.info(form.errors)
      error = True

    else:
      # formgenres = form.genres.data
      # genre_string = ';'.join(formgenres)

      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.image_link = form.image_link.data
      artist.genres = form.genres.data
      #artist.genres = genre_string
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
      artist_name = artist.name

  except Exception as err:
    app.logger.error('err = %s', err)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    return redirect(url_for("edit_artist", artist_id=artist_id))
  else:
    # on successful db insert, flash success
    flash('Artist ' + artist_name + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  venue = {"id": venue_id, "name": venue.name}

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    form = VenueForm(request.form, meta={'csrf': False})
    if not form.validate():
      app.logger.info(form.errors)
      error = True

    else:
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.genres = form.genres.data #genre_string
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()
      venue_name = venue.name

  except Exception as err:
    app.logger.error('err = %s', err)
    error = True
    db.session.rollback()
  finally:
    
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    return redirect(url_for("edit_venue", venue_id=venue_id))
  else:
    # on successful db insert, flash success
    flash('Venue ' + venue_name + ' was successfully updated!')
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
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  error = False
  try:
    form = ArtistForm(request.form, meta={'csrf': False})

    if not form.validate():
      app.logger.info(form.errors)
      error = True

    else:
      newArtist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = form.genres.data, 
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(newArtist)
      db.session.commit()
      newArtistName = newArtist.name

  except Exception as err:
    app.logger.error('err = %s', err)
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    return render_template('forms/new_artist.html', form=form)
  else:
    # on successful db insert, flash success
    flash('Artist ' + newArtistName + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    entry = {}
    venue = show.venue
    artist = show.artist
    if not venue or not artist: continue
    entry["venue_id"] = venue.id
    entry["venue_name"] = venue.name
    entry["artist_id"] = artist.id
    entry["artist_name"] = artist.name
    entry["artist_image_link"] = artist.image_link
    entry["start_time"] = str(show.start_time)
    data.append(entry)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  try:
    form = ShowForm(request.form, meta={'csrf': False})

    if not form.validate():
      app.logger.info(form.errors)
      error = True
      raise Exception ("invalid input")

    else:
      artist_id = form.artist_id.data
      artist_exist = Artist.query.get(artist_id)
      if artist_exist is None:
        raise Exception ('artist id does not exist')

      venue_id = form.venue_id.data
      venue_exist = Venue.query.get(venue_id)
      if venue_exist is None:
        raise Exception ('venue id does not exist')

      newShow = Show(
        artist_id = artist_id,
        venue_id = venue_id,
        start_time = form.start_time.data
      )
      db.session.add(newShow)
      db.session.commit()

  except Exception as err:
    app.logger.error('err = %s', err)
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show at ' + str(form.start_time.data) +  ' could not be listed.')
    return render_template('forms/new_show.html', form=form)
  else:
    # on successful db insert, flash success
      flash('Show at ' + str(form.start_time.data) + ' was successfully listed!')
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
