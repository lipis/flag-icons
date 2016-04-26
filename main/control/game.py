# coding: utf-8

import flask
import random

import cache
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

  country_dbs = cache.get_country_dbs(continent)
  random.shuffle(country_dbs)
  question_db = None
  answer_dbs = None
  answers = 4
  streak = int(flask.request.cookies.get('%s-%s-streak' % (continent, game), 0))

  if streak > 8:
    answers = 5
  if streak > 16:
    answers = 6
  if streak > 32:
    answers = 7
  if streak > 48:
    answers = 8

  if len(country_dbs) >= answers:
    question_db = country_dbs[0]
    answer_dbs = country_dbs[0:answers]
    random.shuffle(answer_dbs)

  title = ''
  if game == 'capital':
    title = 'Capitals of '
  else:
    title = 'Countries of '

  title += 'the World' if not continent else continent

  util.track_event_to_ga('quiz', 'view', '%s - %s' % (game, continent or 'World'), 1)
  return flask.render_template(
    'game/game.html',
    html_class='game',
    title=title,
    game=game,
    continent=continent,
    country_dbs=country_dbs,
    question_db=question_db,
    answer_dbs=answer_dbs,
    streak=streak,
    top=int(flask.request.cookies.get('%s-%s-top' % (continent, game), 0)),
  )


@app.route('/answer/<game>/<continent>/<int:country_id>/<answer_key>/')
@app.route('/answer/<game>/<int:country_id>/<answer_key>/')
def game_answer(game, country_id, answer_key, continent=None):
  if game not in ['capital', 'country']:
    flask.abort(404)
  continent = continent.replace('+', ' ') if continent else None
  if continent and continent.replace('+', ' ') not in config.CONTINENTS:
    flask.abort(404)

  streak = int(flask.request.cookies.get('%s-%s-streak' % (continent, game), 0))
  top = int(flask.request.cookies.get('%s-%s-top' % (continent, game), 0))

  country_db = model.Country.get_by_id(country_id)
  if country_db and country_db.key.urlsafe() == answer_key:
    flask.flash('Correct! The capital of %s is %s.' % (country_db.name, country_db.capital), category='success')
    streak += 1
    if top < streak:
      top = streak
    util.track_event_to_ga('quiz', 'won', '%s - %s' % (game, continent or 'World'), 1)
  else:
    if game == 'capital':
      flask.flash('Wrong! The capital of %s is %s.' % (country_db.name, country_db.capital), category='danger')
    if game == 'country':
      flask.flash('Wrong! The capital %s belongs to %s.' % (country_db.capital, country_db.name), category='danger')
    streak = 0
    util.track_event_to_ga('quiz', 'lost', '%s - %s' % (game, continent or 'World'), 1)

  response = flask.make_response(flask.redirect('%s#question' % flask.url_for('game', game=game, continent=continent)))
  response.set_cookie('%s-%s-streak' % (continent, game), str(streak), max_age=60 * 60 * 24 * 365)
  response.set_cookie('%s-%s-top' % (continent, game), str(top), max_age=60 * 60 * 24 * 365)
  return response
