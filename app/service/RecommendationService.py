from flask import current_app
import requests


def getRecommendation(liked_games, token):
    base_url = current_app.config["MAIN_SERVER_API_BASE_URL"]
    response = requests.get(f"{base_url}/igdb/liked-games")
    print(response.json())

    return response.json()
