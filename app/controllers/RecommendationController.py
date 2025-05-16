import functools
import logging
from flask import Blueprint, request, jsonify, current_app
import requests

bp = Blueprint('recommendation', __name__, url_prefix='/')

from app.service.RecommendationService import getRecommendation

@bp.route('/recommend', methods=('GET', 'POST'))
def recommend():
    try:
        data = request.get_json()
        if 'games' not in data:
            return jsonify({"error": "Missing required field: games"}), 400

        liked_games = data.get("games", [])
        
        if not liked_games:
            return jsonify({"error": "No liked games provided"}), 400

        all_games = liked_games.copy()
        
        for key in ['genres', 'themes', 'platforms']:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict) and 'games' in item and isinstance(item['games'], list):
                        all_games.extend(item['games'])
        
        try:
            base_url = current_app.config.get("MAIN_SERVER_API_BASE_URL")
            response = requests.get(f"{base_url}/knnserver/allgames")
            if response.status_code == 200:
                api_games = response.json().get("games")
                existing_ids = {game['id'] for game in all_games}
                for game in api_games:
                    if game['id'] not in existing_ids:
                        all_games.append(game)
            else:
                logging.error("Failed to fetch additional games, status code: ", response.status_code)

        except Exception as e:
            logging.warning(f"Failed to fetch additional games: {str(e)}")

        if not all_games:
            return jsonify({"error": "No games available for recommendation"}), 400

        recommended_games = getRecommendation(liked_games, all_games)
        print(recommended_games)
        
        return recommended_games
        
    except Exception as e:
        logging.error(f"Error in recommendation controller: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
