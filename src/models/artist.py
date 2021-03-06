
from models.database import db

artists_genres_pivot = db.Table('artists_genres_pivot',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',
                              secondary=artists_genres_pivot, lazy='subquery')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    upcoming_shows = db.relationship("Show",
                    primaryjoin="and_(Artist.id==Show.artist_id, "
                    "Show.start_time >= str(func.now()))")
    past_shows = db.relationship("Show",
                    primaryjoin="and_(Artist.id==Show.artist_id, "
                    "Show.start_time < str(func.now()))")

    # past_shows_count = column_property(func.count('past_shows'))
    # upcoming_shows_count = column_property(func.count('upcoming_shows'))

    def __repr__(self):
      return f'''<Artist {self.id}, {self.name}, {self.city}>'''