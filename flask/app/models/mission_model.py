from app.utils.enums import MissionStatus
from app.models.device_model import Device
from app.models.user_model import User
from app.utils.extensions import db


class Mission(db.Document):
    name = db.StringField(default="Mission")
    start_date = db.DateTimeField(default=None)
    end_date = db.DateTimeField(default=None)
    status = db.EnumField(MissionStatus, default=MissionStatus.CREATED)
    device_ids = db.ListField(db.ReferenceField(Device), default=[])
    user_ids = db.ListField(db.ReferenceField(User), default=[])
    meta = {"collection": "Missions"}

    def __repr__(self):
        return (
            f"<Mission:\n"
            f"id: {str(self.id)}\n"
            f"name: {self.name}\n"
            f"start_date: {self.start_date}\n"
            f"end_date: {self.end_date}\n"
            f"status: {self.status}\n"
            f"device_ids: {[str(dev.id) for dev in self.device_ids]}\n"
            f"user_ids: {[str(user.id) for user in self.user_ids]}>"
        )
