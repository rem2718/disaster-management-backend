from datetime import timedelta
import re

from flask_jwt_extended import create_access_token
from mongoengine import EmbeddedDocumentField

from app.utils.enums import UserType, UserStatus, MissionStatus
from app.utils.extensions import db, bcrypt


class cur_mission(db.EmbeddedDocument):
    _id = db.ObjectIdField(default=None)
    name = db.StringField()
    status = db.EnumField(MissionStatus, default=MissionStatus.CREATED)
    meta = {"collection": "cur_missions"}


class User(db.Document):
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    username = db.StringField(required=True)
    type = db.EnumField(UserType, default=UserType.REGULAR)
    status = db.EnumField(UserStatus, default=UserStatus.PENDING)
    has_mqtt_creds = db.BooleanField(default=False)
    cur_missions = db.ListField(
        EmbeddedDocumentField(cur_mission), required=False, default=[]
    )

    meta = {"collection": "Users"}

    def __repr__(self):
        return (
            f"<User:\n"
            f"id: {str(self.id)}\n"
            f"username: {self.username}\n"
            f"email: {self.email}\n"
            f"password: {self.password}\n"
            f"status: {UserStatus(self.status).name}\n"
            f"type: {UserType(self.type).name}\n",
            f"has_mqtt_creds: {self.has_mqtt_creds}"
            f"cur_missions: {[f'id: {str(mission._id)}, name: {mission.name}, status: {MissionStatus(mission.status).name}' for mission in self.cur_missions]}>",
        )

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_token(self):
        ident = {"id": str(self.id), "type": self.type.value}
        return create_access_token(identity=ident, expires_delta=timedelta(hours=24))

    @staticmethod
    def is_email(string):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, string) is not None
