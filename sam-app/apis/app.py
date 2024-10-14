import os
from dotenv import load_dotenv
from asyncpg import create_pool
import asyncio
import functools
from utils.helper import *
import traceback
import sys
from utils.jwt_utils import AuthenticationError

from services.user_service import UserInfo
from services.support_ticket_service import SupportTicket
from services.agent_service import Agent as AgentService
from services.create_session import CreateSession
from services.lead_service import Leads as LeadsService
from services.appointment_service import Appointment as AppointmentService

load_dotenv()

db_pool = None
loop = None
headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": "true"
}


@functools.lru_cache(maxsize=1)
def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = loop.run_until_complete(create_pool(
            host=os.getenv("STATE_HOST"),
            user=os.getenv("STATE_USER"),
            password=os.getenv("STATE_PASSWORD"),
            port=os.getenv("STATE_PORT"),
            database=os.getenv("STATE_DATABASE"),
        ))
    return db_pool

class Router:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop

    async def call_handler(self, handler, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler()

            return handler()
        except AuthenticationError as e:
            raise AuthenticationError(e.message, e.status_code)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise Exception(e)

    def route(self, method, path):
        routes = {
            ('POST', '/create_session'): CreateSession(self.event, self.db_pool, self.loop).create_session_handler,
            ('POST', '/create-contact-session'): CreateSession(self.event, self.db_pool, self.loop).create_contact_session_handler,
            # ('POST', '/save-user-info'): UserInfo(self.event, self.db_pool, self.loop).save_user_info_handler,
            # ('POST', '/create-calendar-event'): UserInfo(self.event, self.db_pool, self.loop).create_calendar_event_handler,
            ('POST', '/login'): UserInfo(self.event, self.db_pool, self.loop).authenticate_user,
            ('POST', '/forget-password'): UserInfo(self.event, self.db_pool, self.loop).forget_password,
            ('POST', '/reset-password'): UserInfo(self.event, self.db_pool, self.loop).reset_password,
            ('GET', '/calendars'): UserInfo(self.event, self.db_pool, self.loop).get_calendar_list,
            ('GET', '/agents'): AgentService(self.event, self.db_pool, self.loop).get_agents,
            ('GET', '/support-ticket'): SupportTicket(self.event, self.db_pool, self.loop).get_support_tickets,
            ('POST', '/support-ticket/{ticket_id}/assign-agent/{agent_id}'): SupportTicket(self.event, self.db_pool, self.loop).assign_agent_to_ticket,
            ('GET', '/leads'): LeadsService(self.event, self.db_pool, self.loop).get_visitors,
            ('GET', '/appointments'): AppointmentService(self.event, self.db_pool, self.loop).get_appointments,
            ('POST', '/create-appointment'): AppointmentService(self.event, self.db_pool, self.loop).create_appointment,
            ('POST', '/calendar/assign-agents'): AgentService(self.event, self.db_pool, self.loop).assign_agent_to_calendar,
        }

        handler = routes.get((method, path))
        if handler:
            return self.call_handler(handler)

        return "Route not found"

# Lambda handler function
def lambda_handler(event, context):
    global loop, db_pool
    
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if db_pool is None:
        db_pool = get_db_pool()

    try:
        # Handle OPTIONS requests for CORS
        if event['httpMethod'] == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": headers
            }

        router = Router(event, db_pool, loop)
        method = event['httpMethod']
        path = event['resource']

        # Call the appropriate handler based on the method and path
        response = loop.run_until_complete(router.route(method, path))

        return format_response(200, response)
    except AuthenticationError as e:
        return format_response(e.status_code, {'message': e.message})
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error_message = "".join(error_details)
        print(f"Unexpected error: {error_message}")
        return format_response(500, {"message": "An unexpected error occurred", "details": str(e)})
