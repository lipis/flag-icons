# coding: utf-8

import util


class Base(object):
  @classmethod
  def retrieve_one_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()

  @classmethod
  def get_dbs(cls, query=None, order=None, limit=None, cursor=None, **kwgs):
    return util.retrieve_dbs(
        query or cls.query(),
        limit=limit or util.param('limit', int),
        cursor=cursor or util.param('cursor'),
        order=order or util.param('order') or '-created',
        **kwgs
      )


class User(Base):
  @classmethod
  def get_dbs(cls, **kwgs):
    return super(User, cls).get_dbs(
        admin=util.param('admin', bool),
        active=util.param('active', bool),
        permissions=util.param('permissions', list),
        **kwgs
      )
