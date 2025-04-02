# has to return a json for now.

import functools
import json
import os

from flask import ( Blueprint, flash, g, redirect, render_template, request, session,
                    url_for, jsonify, current_app)

bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')

@bp.route('/recommend', methods=('GET', 'POST'))
def recommend():
    recommendations = {
        "some": "recommendations",
        "for": "you",
        "based": "on",
        "your": "preferences"
    }
    
    return jsonify(recommendations)
    