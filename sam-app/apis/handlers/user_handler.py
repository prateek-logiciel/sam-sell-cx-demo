from utils.helper import format_response
from services.user_service import UserInfo

class UserHandler:
    def __init__(self, db_pool, loop):
        self.db_pool = db_pool
        self.loop = loop

    def authenticate_user(self, event, context):
        user_info = UserInfo(event, self.db_pool, self.loop)
        response = self.loop.run_until_complete(user_info.authenticate_user())
        return format_response(200, response)

    def save_user_info(self, event, context):
        user_info = UserInfo(event, self.db_pool, self.loop)
        response = self.loop.run_until_complete(user_info.save_user_info_handler())
        return response if isinstance(response, dict) else format_response(200, response)

    def create_calendar_event(self, event, context):
        user_info = UserInfo(event, self.db_pool, self.loop)
        response = self.loop.run_until_complete(user_info.create_calendar_event_handler())
        return response if isinstance(response, dict) else format_response(200, response)