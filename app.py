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

  fake_data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
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

  fake_response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  def showinfo(show):
    info = {}
    info['artist_id'] = show.artist_id
    info['artist_name'] = Artist.query.get(show.artist_id).name
    info['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    info['start_time'] = str(show.start_time)
    return info
  
  data = []
  venues = Venue.query.all()

  for venue in venues:
    entry = {}
    entry['id'] = venue.id
    entry['name'] = venue.name
    entry['genres'] =  venue.genres.split(';') if venue.genres else ""
    entry['address'] = venue.address
    entry['city'] = venue.city
    entry['state'] = venue.state
    entry['phone'] = venue.phone
    entry['website'] = venue.website_link
    entry['facebook_link'] = venue.facebook_link
    entry['seeking_talent'] = venue.seeking_talent
    entry['seeking_description'] = venue.seeking_description
    entry['image_link'] = venue.image_link

    pastshows = []
    upcomingshows = []
    for show in venue.shows:
      if show.start_time < datetime.now():
        pastshows.append(show)
      else:
        upcomingshows.append(show)
      
    entry['past_shows'] = [showinfo(show) for show in pastshows]
    entry['upcoming_shows'] = [showinfo(show) for show in upcomingshows]
    entry['past_shows_count'] = len(entry['past_shows'])
    entry['upcoming_shows_count'] = len(entry['upcoming_shows'])

    data.append(entry)

  data1={
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
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #fake_data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

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
      formgenres = form.genres.data
      genre_string = ';'.join(formgenres)
    
      newVenue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = genre_string,
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

  fake_data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
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
  
  fake_response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
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
      entry['genres'] =  artist.genres.split(';') if artist.genres else ""
      entry['city'] = artist.city
      entry['state'] = artist.state
      entry['phone'] = artist.phone
      entry['website'] = artist.website_link
      entry['facebook_link'] = artist.facebook_link
      entry['seeking_venue'] = artist.seeking_venue
      entry['seeking_description'] = artist.seeking_description
      entry['image_link'] = artist.image_link

      pastshows = []
      upcomingshows = []
      for show in artist.shows:
        if show.start_time < datetime.now():
          pastshows.append(show)
        else:
          upcomingshows.append(show)
      
      entry['past_shows'] = []
      for show in pastshows:
        if showinfo(show) is not None:
          entry['past_shows'].append(showinfo(show))
      #[showinfo(show) for show in pastshows]
      entry['upcoming_shows'] = []
      for show in upcomingshows:
        if showinfo(show) is not None:
          entry['upcoming_shows'].append(showinfo(show))
      #[showinfo(show) for show in upcomingshows]
      entry['past_shows_count'] = len(entry['past_shows'])
      entry['upcoming_shows_count'] = len(entry['upcoming_shows'])

      data.append(entry)
  
    data1={
      "id": 4,
      "name": "Guns N Petals",
      "genres": ["Rock n Roll"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "326-123-5000",
      "website": "https://www.gunsnpetalsband.com",
      "facebook_link": "https://www.facebook.com/GunsNPetals",
      "seeking_venue": True,
      "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
      "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "past_shows": [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "start_time": "2019-05-21T21:30:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data2={
      "id": 5,
      "name": "Matt Quevedo",
      "genres": ["Jazz"],
      "city": "New York",
      "state": "NY",
      "phone": "300-400-5000",
      "facebook_link": "https://www.facebook.com/mattquevedo923251523",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "past_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
      }],
      "upcoming_shows": [],
      "past_shows_count": 1,
      "upcoming_shows_count": 0,
    }
    data3={
      "id": 6,
      "name": "The Wild Sax Band",
      "genres": ["Jazz", "Classical"],
      "city": "San Francisco",
      "state": "CA",
      "phone": "432-325-5432",
      "seeking_venue": False,
      "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "past_shows": [],
      "upcoming_shows": [{
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
      }],
      "past_shows_count": 0,
      "upcoming_shows_count": 3,
    }

    currartistdata = list(filter(lambda d: d['id'] == artist_id, data))[0]
    app.logger.info(currartistdata)
    app.logger.info(data)
  #fake_data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
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
  
  genres = artist.genres.split(';')
  form.genres.data = genres

  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  artist = {"id": artist_id, "name": artist.name}

  fake_artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  
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
      formgenres = form.genres.data
      genre_string = ';'.join(formgenres)

      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.image_link = form.image_link.data
      artist.genres = genre_string
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
  
  genres = venue.genres.split(';')
  form.genres.data = genres

  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  venue = {"id": venue_id, "name": venue.name}

  fake_venue={
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
      formgenres = form.genres.data
      genre_string = ';'.join(formgenres)

      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.genres = genre_string
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
      formgenres = form.genres.data
      genre_string = ';'.join(formgenres)
    
      newArtist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        genres = genre_string,
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
  
  fake_data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
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
