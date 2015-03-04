# coding: utf-8

from flask.ext import restful

from api import helpers
import auth
import config
import model

from main import api


@api.resource('/api/v1/config/', endpoint='api.config')
class ConfigAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    return helpers.make_response(config.CONFIG_DB, model.Config.FIELDS)
