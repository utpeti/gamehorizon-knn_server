from flask import current_app, jsonify
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getRecommendation(liked_games, all_games):
    """
    get game recommendations based on liked games using feature vectors
    
    parameters:
    - liked_games: list of game objects that the user likes
    - all_games: list of all available games
    
    returns:
    - JSON response with recommended games
    """
    try:
        # extract all unique IDs for genres, themes, and platforms from all_games
        all_genre_ids = set()
        all_theme_ids = set()
        all_platform_ids = set()
        
        for game in all_games:
            genres = game.get('genres', [])
            themes = game.get('themes', [])
            platforms = game.get('platforms', [])
            
            if genres and isinstance(genres, list):
                all_genre_ids.update(genres)
            if themes and isinstance(themes, list):
                all_theme_ids.update(themes)
            if platforms and isinstance(platforms, list):
                all_platform_ids.update(platforms)
        
        # create and fit encoders with the complete set of IDs
        genre_encoder = MultiLabelBinarizer()
        genre_encoder.fit([list(all_genre_ids)])
        
        theme_encoder = MultiLabelBinarizer()
        theme_encoder.fit([list(all_theme_ids)])
        
        platform_encoder = MultiLabelBinarizer()
        platform_encoder.fit([list(all_platform_ids)])
        
        # extract liked game IDs for filtering
        liked_game_ids = [game['id'] for game in liked_games]
        
        # calculate vectors for liked games
        liked_game_vectors = []
        for game in liked_games:
            vector = game_to_vector(game, genre_encoder, theme_encoder, platform_encoder)
            liked_game_vectors.append((game, vector))
        
        recommendations = []
        
        for game in all_games:
            if game['id'] in liked_game_ids:
                continue
                
            # create feature vector for the candidate game
            game_vec = game_to_vector(game, genre_encoder, theme_encoder, platform_encoder)
            
            # calculate similarity with each liked game vector
            similarities = []
            for _, liked_vec in liked_game_vectors:
                sim = compute_similarity(game_vec, liked_vec)
                similarities.append(sim)
            
            # calculate average similarity
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                recommendations.append((game, avg_similarity))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        top_games = [game for game, _ in recommendations[:20]]
        return jsonify(top_games)
        
    except Exception as e:
        logger.error(f"Error in getRecommendation: {str(e)}")
        raise


def compute_similarity(vec1, vec2):
    if len(vec1) == 0 or len(vec2) == 0:
        return 0
    
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    
    return cosine_similarity(vec1, vec2)[0][0]


def game_to_vector(game, genre_encoder, theme_encoder, platform_encoder):
    """
    convert a game object to a feature vector
    
    parameters:
    - game: game object with genres, themes, and platforms fields (as lists of IDs)
    - genre_encoder, theme_encoder, platform_encoder: feature encoders
    
    returns:
    - feature vector representing the game
    """
    try:
        genre_ids = game.get('genres', []) or []
        theme_ids = game.get('themes', []) or []
        platform_ids = game.get('platforms', []) or []
        
        # filter out any IDs that aren't in the encoder's classes
        valid_genre_ids = [gid for gid in genre_ids if gid in genre_encoder.classes_]
        valid_theme_ids = [tid for tid in theme_ids if tid in theme_encoder.classes_]
        valid_platform_ids = [pid for pid in platform_ids if pid in platform_encoder.classes_]
        
        # transform to binary vectors
        genre_vec = genre_encoder.transform([valid_genre_ids])[0] if valid_genre_ids else np.zeros(len(genre_encoder.classes_))
        theme_vec = theme_encoder.transform([valid_theme_ids])[0] if valid_theme_ids else np.zeros(len(theme_encoder.classes_))
        platform_vec = platform_encoder.transform([valid_platform_ids])[0] if valid_platform_ids else np.zeros(len(platform_encoder.classes_))
        
        return np.concatenate([genre_vec, theme_vec, platform_vec])
    except Exception as e:
        logger.error(f"Error in game_to_vector for game {game.get('id')}: {str(e)}")

        return np.concatenate([
            np.zeros(len(genre_encoder.classes_)),
            np.zeros(len(theme_encoder.classes_)),
            np.zeros(len(platform_encoder.classes_))
        ])
