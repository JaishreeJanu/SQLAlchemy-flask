import sys
import os
sys.path.append(os.path.abspath("/home/jaishree/sqlalchemy-demo/flask movie example"))
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, db_insert_records, Actor, Movie

QUESTIONS_PER_PAGE = 10


def paginate(request, results):
    """return results in group of 10
    10 set of questions shown on each page
    Arguments:
        request {json} -- json body woth page parameter
        results {list} -- results

    Returns:
        list -- questions on current page
    """
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    all_results = [result.format() for result in results]
    paginated_results = all_results[start:end]
    return paginated_results


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    @app.route("/actors", methods=["GET"])
    def get_actors(token):
        """gets all actors
        if token has 'read:actors' permission
        Returns:
            json -- success value and list of actors
        """
        all_actors = Actor.query.all()
        actors = paginate(request, all_actors)

        if len(actors) == 0:
            abort(404, {"message": "OOPS! No actors willing to work"})

        return jsonify({"success": True, "actors": actors}), 200

    @app.route("/movies", methods=["GET"])
    def get_movies(token):
        """get all movies
        if token has 'read:movies' permission
        Returns:
            json -- success value and list of movies
        """
        all_movies = Movie.query.all()
        movies = paginate(request, all_movies)

        if len(movies) == 0:
            abort(404, {"message": "OOPS! No one is making movies"})

        return jsonify({"success": True, "movies": movies}), 200

    @app.route("/actors", methods=["POST"])
    def add_actor(token):
        """Adds a new record in actor db table
        if token has 'add:actor' permission
        Returns:
            json -- success value and id of new record
        """
        data = request.get_json()
        if not data.get("name"):
            abort(400, {"message": 'Please add "name" in the json'})

        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")
        new_actor = Actor(name=name, age=age, gender=gender)
        new_actor.insert()

        return jsonify({"success": True, "actor": new_actor.id}), 200

    @app.route("/movies", methods=["POST"])
    def add_movie(token):
        """Adds a new record in movie db table
        if token contains 'add:movie' permission
        Returns:
            json -- success value and id of new record
        """
        data = request.get_json()
        if not data:
            abort(400, {"message": "there is no json body"})

        title = data.get("title")
        release_date = data.get("release_date")

        new_movie = Movie(title=title, release_date=release_date)
        new_movie.insert()

        return jsonify({"success": True, "movie": new_movie.id}), 200

    @app.route("/actors/<int:actor_id>", methods=["PATCH"])
    def modify_actor(token, actor_id):
        """modifies the actor details with the actor_id,
        token must contain 'modify:actor' permission
        Arguments:
            actor_id {int}: actor id
        Returns:
            json -- success value and id of updated record
        """
        data = request.get_json()
        if not data:
            abort(400, {"message": "there is no json body"})
        this_actor = Actor.query.get(actor_id)

        if not this_actor:
            abort(404, {"message": "No actor with this id"})
        new_name = data.get("name")
        new_age = data.get("age")
        new_gender = data.get("gender")

        if new_name:
            this_actor.name = new_name
        if new_age:
            this_actor.age = new_age
        if new_gender:
            this_actor.gender = new_gender

        this_actor.update()
        return jsonify({"success": True, "actor": this_actor.id}), 200

    @app.route("/movies/<int:movie_id>", methods=["PATCH"])
    def modify_movie(token, movie_id):
        """modifies the movie details with the movie_id,
        token must contain 'modify:movie' permission
        Arguments:
            movie_id {int}: movie id
        Returns:
            json -- success value and id of updated record
        """
        data = request.get_json()
        if not data:
            abort(400, {"message": "there is no json body"})
        this_movie = Movie.query.get(movie_id)

        if not this_movie:
            abort(404, {"message": "No movie with this id"})

        if data.get("title"):
            new_title = data.get("title")
            this_movie.title = new_title
        if data.get("release_date"):
            new_release_date = data.get("release_date")
            this_movie.new_release_date = new_release_date

        this_movie.update()
        return jsonify({"success": True, "movie": this_movie.id}), 200

    @app.route("/actors/<int:actor_id>", methods=["DELETE"])
    def delete_actor(token, actor_id):
        """deletes actor with actor_id,
        should contain 'delete:actor' permission
        Arguments:
            actor_id {int}: actor id
        Returns:
            json -- success value and id of deleted record
        """
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404, {"message": "No actor with this id"})
        actor.delete()

        return jsonify({"success": True, "actor": actor.id}), 200

    @app.route("/movies/<int:movie_id>", methods=["DELETE"])
    def delete_movie(token, movie_id):
        """deletes movie with movie_id,
        should contain 'delete:movie' permission
        Arguments:
            movie_id {int}: movie id
        Returns:
            json -- success value and id of deleted record
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404, {"message": "No movie with this id"})
        movie.delete()

        return jsonify({"success": True, "movie": movie.id}), 200

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": error.description["message"],
                }
            ),
            400,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)