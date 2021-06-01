
from models.database import db

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