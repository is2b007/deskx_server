from protobuf3.message import Message
from protobuf3.fields import StringField, BoolField


class Request(Message):
    pass


class Response(Message):
    pass

Request.add_field('username', StringField(field_number=1, optional=True))
Request.add_field('password', StringField(field_number=2, optional=True))
Response.add_field('success', BoolField(field_number=1, optional=True))
Response.add_field('errorMessage', StringField(field_number=2, optional=True))
