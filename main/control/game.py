# coding: utf-8

import flask
import random

import config
import model
import util

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/game/<game>/<continent>/')
@app.route('/game/<game>/')
@app.route('/game/')
def game(game='capital', continent=None):
  if game and game not in ['capital', 'country']:
    return flask.redirect(flask.url_for('game', game='capital'))

  continent = continent.replace('+', ' ') if continent else None
  if continent and continent.replace('+', ' ') not in config.CONTINENTS:
    flask.abort(404)

  country_dbs, country_cursor = model.Country.get_dbs(continent=continent)
  random.shuffle(country_dbs)
  question_db = None
  answer_dbs = None
  if len(country_dbs) > 3:
    question_db = country_dbs[0]
    answer_dbs = country_dbs[0:4]
    random.shuffle(answer_dbs)

  return flask.render_template(
    'game/game.html',
    html_class='game',
    game=game,
    continent=continent,
    country_dbs=country_dbs,
    question_db=question_db,
    answer_dbs=answer_dbs,
  )


@app.route('/answer/<game>/<continent>/<int:country_id>/<answer_key>/')
@app.route('/answer/<game>/<int:country_id>/<answer_key>/')
def game_answer(game, country_id, answer_key, continent=None):
  if game not in ['capital', 'country']:
    flask.abort(404)
  continent = continent.replace('+', ' ') if continent else None
  if continent and continent.replace('+', ' ') not in config.CONTINENTS:
    flask.abort(404)

  country_db = model.Country.get_by_id(country_id)
  if country_db and country_db.key.urlsafe() == answer_key:
    flask.flash('Bravo! The capital of %s is %s.' % (country_db.name, country_db.capital), category='success')
  else:
    if game == 'capital':
      flask.flash('Wrong! The capital of %s is %s.' % (country_db.name, country_db.capital), category='danger')
    if game == 'country':
      flask.flash('Wrong! The capital %s belongs to %s.' % (country_db.capital, country_db.name), category='danger')

  return flask.redirect('%s#question' % flask.url_for('game', game=game, continent=continent))
