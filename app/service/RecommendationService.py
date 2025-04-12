from flask import current_app
import requests


def getRecommendation(liked_games):
    base_url = current_app.config["MAIN_SERVER_API_BASE_URL"]
    response = requests.get(f"{base_url}/igdb/popular")
    print(response.json())

    return response.json()
