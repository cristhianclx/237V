from flask import Flask
from flask_restful import Resource, Api
import requests


app = Flask(__name__)
api = Api(app)


class WorkingResource(Resource):
    def get(self):
        return {'working': True}


class PokemonResource(Resource):
    def get(self, name):
        r = requests.get('https://pokeapi.co/api/v2/pokemon/{}'.format(name))
        if r.ok:
            data = r.json()
             # game_indices
            abilities = []
            for a in data["abilities"]:
                abilities.append(a["ability"]["name"])
            return {
                "name": name,
                "abilities": abilities,
                "height": data["height"],
                "game_indices": [{"version": 1, "game_index": 3}]
            }
        else:
            return {
                "error": "a big error happened"
            }, 400


api.add_resource(WorkingResource, '/')
api.add_resource(PokemonResource, '/pokemon-by-name/<string:name>')


if __name__ == '__main__':
    app.run(debug=True)