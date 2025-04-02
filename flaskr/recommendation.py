import functools
import numpy as np

from flask import ( Blueprint, flash, g, redirect, render_template, request, session,
                    url_for )

bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')
