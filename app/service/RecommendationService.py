from flask import jsonify
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getRecommendation(liked_games, all_games):
    """
    Optimized version: get game recommendations based on liked games using feature vectors
    """

    try:
        # --- Step 1: Collect all unique IDs for encoding ---
        all_genre_ids = set()
        all_theme_ids = set()
        all_platform_ids = set()

        for game in all_games:
            all_genre_ids.update(game.get('genres', []) or [])
            all_theme_ids.update(game.get('themes', []) or [])
            all_platform_ids.update(game.get('platforms', []) or [])

        # --- Step 2: Fit encoders ---
        genre_encoder = MultiLabelBinarizer()
        genre_encoder.fit([list(all_genre_ids)])

        theme_encoder = MultiLabelBinarizer()
        theme_encoder.fit([list(all_theme_ids)])

        platform_encoder = MultiLabelBinarizer()
        platform_encoder.fit([list(all_platform_ids)])

        # --- Step 3: Precompute all game vectors ---
        game_vectors = {}
        for game in all_games:
            vector = game_to_vector(game, genre_encoder, theme_encoder, platform_encoder)
            game_vectors[game['id']] = vector

        # --- Step 4: Prepare matrices for similarity computation ---
        liked_game_ids = {game['id'] for game in liked_games}
        liked_vectors = np.stack([game_vectors[gid] for gid in liked_game_ids if gid in game_vectors])

        candidate_games = [game for game in all_games if game['id'] not in liked_game_ids]
        candidate_vectors = np.stack([game_vectors[game['id']] for game in candidate_games])

        # --- Step 5: Vectorized similarity calculation ---
        similarity_matrix = cosine_similarity(candidate_vectors, liked_vectors)
        avg_similarities = similarity_matrix.mean(axis=1)

        # --- Step 6: Sort and return top recommendations ---
        recommendations = sorted(
            zip(candidate_games, avg_similarities),
            key=lambda x: x[1],
            reverse=True
        )

        top_games = [game for game, _ in recommendations[:20]]
        return jsonify(top_games)

    except Exception as e:
        logger.error(f"Error in getRecommendation: {str(e)}")
        raise


def game_to_vector(game, genre_encoder, theme_encoder, platform_encoder):
    """
    Convert a game object to a binary feature vector based on genres, themes, and platforms
    """
    try:
        genre_ids = game.get('genres', []) or []
        theme_ids = game.get('themes', []) or []
        platform_ids = game.get('platforms', []) or []

        valid_genres = [gid for gid in genre_ids if gid in genre_encoder.classes_]
        valid_themes = [tid for tid in theme_ids if tid in theme_encoder.classes_]
        valid_platforms = [pid for pid in platform_ids if pid in platform_encoder.classes_]

        genre_vec = genre_encoder.transform([valid_genres])[0] if valid_genres else np.zeros(len(genre_encoder.classes_))
        theme_vec = theme_encoder.transform([valid_themes])[0] if valid_themes else np.zeros(len(theme_encoder.classes_))
        platform_vec = platform_encoder.transform([valid_platforms])[0] if valid_platforms else np.zeros(len(platform_encoder.classes_))

        return np.concatenate([genre_vec, theme_vec, platform_vec])
    except Exception as e:
        logger.error(f"Error in game_to_vector for game {game.get('id')}: {str(e)}")
        return np.concatenate([
            np.zeros(len(genre_encoder.classes_)),
            np.zeros(len(theme_encoder.classes_)),
            np.zeros(len(platform_encoder.classes_))
        ])
