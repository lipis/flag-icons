from flask import request

from wtforms import FileField as _FileField
from wtforms import ValidationError


class FileField(_FileField):
    """
    Subclass of **wtforms.FileField** providing a `file` property
    returning the relevant **FileStorage** instance in **request.files**.
    """
    @property
    def file(self):
        """
        Returns FileStorage class if available from request.files
        or None
        """
        return request.files.get(self.name, None)


class FileRequired(object):
    """
    Validates that field has a **FileStorage** instance
    attached.

    `message` : error message

    You can also use the synonym **file_required**.
    """

    def __init__(self, message=None):
        self.message=message

    def __call__(self, form, field):
        file = getattr(field, "file", None)

        if not file:
            raise ValidationError, self.message

file_required = FileRequired


class FileAllowed(object):
    """
    Validates that the uploaded file is allowed by the given
    Flask-Uploads UploadSet.

    `upload_set` : instance of **flaskext.uploads.UploadSet**

    `message`    : error message

    You can also use the synonym **file_allowed**.
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        file = getattr(field, "file", None)

        if file is not None and \
            not self.upload_set.file_allowed(file, file.filename):
            raise ValidationError, self.message

file_allowed = FileAllowed
    
