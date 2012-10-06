from google.appengine.ext import ndb
import md5
import util


class BaseX(object):
  @classmethod
  def retrieve_one_by(cls, name, value):
    cls_db_list = cls.query(getattr(cls, name) == value).fetch(1)
    if cls_db_list:
      return cls_db_list[0]
    return None

  @ndb.ComputedProperty
  def created_ago(self):
    if not self.created:
      return None
    return util.format_datetime_ago(self.created)

  @ndb.ComputedProperty
  def modified_ago(self):
    if not self.modified:
      return None
    return util.format_datetime_ago(self.modified)

  @ndb.ComputedProperty
  def created_utc(self):
    if not self.created:
      return None
    return util.format_datetime_utc(self.created)

  @ndb.ComputedProperty
  def modified_utc(self):
    if not self.modified:
      return None
    return util.format_datetime_utc(self.modified)


class ConfigX(object):
  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')


class UserX(object):
  @ndb.ComputedProperty
  def avatar_url(self):
    return 'http://www.gravatar.com/avatar/%s?d=identicon&r=x' % (
        md5.new(self.email or self.name).hexdigest().lower()
      )
