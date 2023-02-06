# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies.all()), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "Movie created", 201

@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id: int):
        movie = Movie.query.get(id)

        if not movie:
            return "Movie not found", 404

        return movie_schema.dump(movie), 200

    def put(self, id: int):
        updated_movie = db.session.query(Movie).filter(Movie.id == id).update(request.json)

        if updated_movie != 1:
            return "Movie not updated", 400

        db.session.commit()

        return "Updated", 204

    def delete(self, id: int):
        movie = Movie.query.get(id)

        if not movie:
            return "Movie not found", 404

        db.session.delete(movie)
        db.session.commit()

        return "Movie deleted", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json

        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return "Director added", 201

@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id: int):
        try:
            director = db.session.query(Director).get(id)
            return director_schema.dump(director), 200

        except Exception:
            return str(Exception), 404

    def put(self, id: int):
        director = Director.query.get(id)
        req_json = request.json
        if "name" in req_json:
            director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()

    def delete(self, id: int):
        director = Director.query.get(id)

        if not director:
            return "Director not found", 404

        db.session.delete(director)
        db.session.commit()

        return "Director deleted", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json

        new_genre = Director(**req_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "Genre added", 201

@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id: int):
        try:
            genre = db.session.query(Genre).get(id)
            return genre_schema.dump(genre), 200

        except Exception:
            return str(Exception), 404

    def put(self, id: int):
        genre = Genre.query.get(id)
        req_json = request.json
        if "name" in req_json:
            genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()

    def delete(self, id: int):
        genre = Genre.query.get(id)

        if not genre:
            return "Genre not found", 404

        db.session.delete(genre)
        db.session.commit()

        return "Genre deleted", 204


if __name__ == '__main__':
    app.run(debug=True)
