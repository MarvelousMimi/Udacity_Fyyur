#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_migrate import Migrate
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
from models import *
app.config.from_object(local)
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = [
    #   {
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    ]
    locations = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    for location in locations:
      venue_list = []
      entries = {}
      venues = db.session.query(Venue).filter((Venue.state == location.state) & (Venue.city == location.city)).all()
    
      for venue in venues:
        venue_data = {}
        venue_data['id'] = venue.id
        venue_data['name'] = venue.name
        venue_data['num_upcoming_shows'] = len(venue.shows)
        venue_list.append(venue_data),
        entries['city'] = location.city
        entries['venue'] = venue_list
        entries['state'] = location.state
        data.append(entries) 

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '' )
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    count = len(results)
    data = []
    for result in results:
      response_data = {}
      response_data['id'] = result.id
      response_data['name'] = result.name
      response_data['num_upcoming_shows'] = len(result.shows)
      data.append(response_data)
    response = {
        'count': count,
        'data': data,
      }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue=Venue.query.filter_by(id=venue_id).one()
    upcoming_shows=[]
    past_shows=[]
    
    for show in venue.shows:
      past_shows_data={}
      upcoming_shows_data={}
      today=datetime.today()

    if show.start_time<today:
      past_shows_data["artist_id"]=(show.artist).id
      past_shows_data["artist_name"]=(show.artist).name
      past_shows_data["start_time"]=show.start_time
      past_shows_data["artist_image_link"]=(show.artist).image_link
      past_shows.append(past_shows_data)

    else:
      upcoming_shows_data["artist_id"]=(show.artist).id
      upcoming_shows_data["artist_image_link"]=(show.artist).image_link
      upcoming_shows_data["artist_name"]=(show.artist).name
      upcoming_shows_data["start_time"]=show.start_time
      upcoming_shows.append(upcoming_shows_data)
  
    data={
      "id": venue.id,
      "name": venue.name,
      "state": venue.state,
      "address": venue.address,
      "city": venue.city,
      "phone": venue.phone,
      "genres": venue.genres,
      "website": venue.website_link,
      "seeking_talent":venue.seeking_talent ,
      "facebook_link": venue.facebook_link,
      "image_link": venue.image_link,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    
    form = VenueForm(request.form)
    venue_name = request.form['name']
    seeking_talent = request.form.get('seeking_talent', False)
    if seeking_talent == "y":
      seeking_talent = True
    else:
      seeking_talent = False
    if form.validate():
      error = False
      try:
        venue = Venue(name = venue_name,city = request.form["city"], state = request.form["state"], phone = request.form["phone"],
        address= request.form["address"], facebook_link = request.form["facebook_link"],
        genres = (request.form.getlist("genres")),
        seeking_description = request.form["seeking_description"])
        website_link = request.form["website_link"], image_link = request.form["image_link"], 
        seeking_talent = (request.form.get("seeking_talent"))
        db.session.add(venue)
        db.session.commit()
      
    # on successful db insert, flash success

      # flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
      # TODO: on unsuccessful db insert, flash an error instead.
    
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      finally:
        db.session.close()
      if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!') 
        return render_template('pages/home.html')
      else:
        flash('An error occured. Venue' +
        venue_name + 'could not be listed.', 'error')
    else:
      flash('Venue' + venue_name + ' could not be created due to validation error(s)!', 'error')
      flash(form.errors)
      return render_template('forms/new_venue.html', form=form)
      


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
      venue=Venue.query.filter_by(id=venue_id).one()
      db.session.delete(venue)
      db.session.commit()
      flash("venue successfully deleted!"),
    except:
      db.session.rollback()
      flash("an error occured during deletion, Try again")
    finally:
      db.session.close()
    
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    artists = Artist.query.all()

    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    
    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    count = len(results)
    data = []
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    for result in results:
      response_data = {}
      response_data['id']=result.id
      response_data['name']=result.name
      response_data['num_upcoming_shows']=len(result.shows)
      data.append(response_data)

    response = {
        "count": count,
        "data":  data
        #   {
        #     "id": 4,
        #     "name": "Guns N Petals",
        #     "num_upcoming_shows": 0,
        # }
        
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist=Artist.query.filter_by(id=artist_id).one()
    past_shows=[]
    upcoming_shows=[]
    # TODO: replace with real artist data from the artist table, using artist_id
    
    for show in artist.shows:
      past_shows_data={}
      upcoming_shows_data={}
      today=datetime.today()
    if show.start_time<today:
      past_shows_data["venue_id"]=(show.venue).id
      past_shows_data["venue_name"]=(show.venue).name
      past_shows_data["venue_image_link"]=(show.venue).image_link
      past_shows_data["start_time"]=show.start_time
      past_shows.append(past_shows_data)
    else:
      upcoming_shows_data["venue_id"]=(show.venue).id
      upcoming_shows_data["venue_name"]=(show.venue).name
      upcoming_shows_data["venue_image_link"]=(show.venue).image_link
      upcoming_shows_data["start_time"]=show.start_time
      upcoming_shows.append(upcoming_shows_data)
    data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue":artist.seeking_venue ,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id = artist_id).one()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    
    # artist record with ID <artist_id> using the new attributes
    
    seeking_talent = request.form.get('seeking_talent', False)
    if seeking_talent == "y":
      seeking_talent = True
    else:
      seeking_talent = False

    try:
      artist=Artist.query.filter_by(id=artist_id).one()
      artist.name=request.form["name"]
      artist.city = request.form["city"]
      artist.state = request.form["state"]
      artist.phone = request.form["phone"]
      artist.facebook_link = request.form["facebook_link"]
      artist.genres = request.form.getlist("genres")
      artist.website_link = request.form["website_link"]
      artist.image_link = request.form["image_link"]
      artist.seeking_venue = (request.form.get("seeking_venue")) 
      artist.seeking_description = request.form["seeking_description"]
      db.session.add(artist)
      db.session.commit()
      flash("Artist updated successfully")
    except:
      db.session.rollback()
      flash("artist update failed, try again")
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).one()
    # {
    #   "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    seeking_talent = request.form.get('seeking_talent', False)
    if seeking_talent == "y":
      seeking_talent = True
    else:
      seeking_talent = False
    try:
      venue = Venue.query.filter_by(id=venue_id).one()
      venue.name = request.form["name"]
      venue.city = request.form["city"]
      venue.state = request.form["state"]
      venue.phone = request.form["phone"]
      venue.address = request.form["address"]
      venue.facebook_link = request.form["facebook_link"]
      venue.genres = request.form.getlist("genres")
      venue.website_link = request.form["website_link"]
      venue.image_link = request.form["image_link"]
      venue.seeking_talent = request.form.get("seeking_venue") 
      venue.seeking_description = request.form["seeking_description"]
      db.session.add(venue)
      db.session.commit()
      flash("venue updated successfully!")
    except:
      db.session.rollback()
      flash("venue update failed, try again")
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

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
    seeking_talent = request.form.get('seeking_talent', False)
    if seeking_talent == "y":
                seeking_talent = True
    else:
                seeking_talent = False
    try:
      artist=Artist(name = request.form["name"],city = request.form["city"], state = request.form["state"], phone = request.form["phone"],
      facebook_link = request.form["facebook_link"], genres=request.form.getlist("genres"), website_link=request.form["website_link"],
      image_link = request.form["image_link"], seeking_venue = request.form.get("seeking_venue"), seeking_description=request.form["seeking_description"] ) 
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ,' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      
    finally:
      db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [
    #   {
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }
    ]

    shows=Show.query.all()
    for show in shows:
      show_details = {}
      show_details["venue_id"] = show.venue_id
      show_details["venue_name"] = (show.venue).name
      show_details["artist_id"] = show.artist_id
      show_details["artist_name"] = (show.artist).name
      show_details["artist_image_link"] = (show.artist).image_link
      show_details["start_time"] = show.start_time
      data.append(show_details)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods = ['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    try:
      show = Show(artist_id = int(request.form["artist_id"]) ,venue_id=int(request.form["venue_id"]),start_time=request.form["start_time"] )
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
