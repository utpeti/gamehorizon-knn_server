from flask import current_app
import requests
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


def getRecommendation(liked_games, token):
    base_url = current_app.config["MAIN_SERVER_API_BASE_URL"]
    response = requests.get(f"{base_url}/igdb/liked-games")
    print(response.json())

    return response.json()

def buildFeatures(genres, themes, platforms):
    genres_processed = [genre['name'] for genre in genres]
    themes_processed = [theme['name'] for theme in themes]
    platforms_processed = [platform['name'] for platform in platforms]

    genre_encoder = MultiLabelBinarizer()
    genre_encoder.fit([genres_processed])

    theme_encoder = MultiLabelBinarizer()
    theme_encoder.fit([themes_processed])

    platform_encoder = MultiLabelBinarizer()
    platform_encoder.fit([platforms_processed])
