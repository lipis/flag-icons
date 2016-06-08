# coding: utf-8

from __future__ import absolute_import

import flask_restful

from api import helpers
import auth
import config
import model

from main import api_v1


@api_v1.resource('/admin/config/', endpoint='api.admin.config')
class ConfigAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    return helpers.make_response(config.CONFIG_DB, model.Config.FIELDS)
