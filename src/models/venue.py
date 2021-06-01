from models.database import db

venus_generes_pivot = db.Table('venus_generes_pivot',
    db.Column('genere_id', db.Integer, db.ForeignKey('Genere.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

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