from werkzeug import FileStorage
from wtforms import FileField as _FileField
from wtforms import ValidationError

class FileField(_FileField):
    """
    Werkzeug-aware subclass of **wtforms.FileField**

    Provides a `has_file()` method to check if its data is a FileStorage
    instance with an actual file.
    """
    @property
    def file(self):
        """
        :deprecated: synonym for **data**
        """
        return self.data

    def has_file(self):
        '''Return True iff self.data is a FileStorage with file data'''
        if not isinstance(self.data, FileStorage):
            return False
        # filename == None => the field was present but no file was entered
        # filename == '<fdopen>' is for a werkzeug hack:
        #   large file uploads will get stored in a temporary file on disk and
        #   show up as an extra FileStorage with name '<fdopen>'
        return self.data.filename not in [None, '', '<fdopen>']


class FileRequired(object):
    """
    Validates that field has a file.

    `message` : error message

    You can also use the synonym **file_required**.
    """

    def __init__(self, message=None):
        self.message=message

    def __call__(self, form, field):
        if not field.has_file():
            raise ValidationError, self.message

file_required = FileRequired


class FileAllowed(object):
    """
    Validates that the uploaded file is allowed by the given
    Flask-Uploads UploadSet.

    `upload_set` : instance of **flask.ext.uploads.UploadSet**

    `message`    : error message

    You can also use the synonym **file_allowed**.
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not field.has_file():
            return
        if not self.upload_set.file_allowed(field.data, field.data.filename):
            raise ValidationError, self.message

file_allowed = FileAllowed
    
