import functools
import json
import os

from flask import ( Blueprint, flash, g, redirect, render_template, request, session,
                    url_for, jsonify, current_app, Response)

from app.service.RecommendationService import getRecommendation

bp = Blueprint('recommendation', __name__, url_prefix='/')

@bp.route('/recommend', methods=('GET', 'POST'))
def recommend():
    data = request.get_json()
    print(data)
    #user = data.get('user')
    #if (user is None):
    #    return Response('{\n"message":"No user provided"}', status=400, mimetype='application/json')
    
    #user_id = user.get('id')
    #liked_games = user.get('liked')
    #if (user_id is None or liked_games is None):
    #    return Response('{\n"message":"Invalid user provided"}', status=400, mimetype='application/json')

    recommended_games = getRecommendation(1,1)
    return recommended_games