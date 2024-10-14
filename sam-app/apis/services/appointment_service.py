from utils.jwt_utils import token_required
from pydantic import BaseModel
from utils.google_calendar import *
from utils.helper import *
import math
from repositories.appointment import AppointmentRepository
from datetime import datetime

class AppointmentData(BaseModel):
    start_time: datetime
    end_time: datetime
    agent_id: int
    visitor_id: int
    calendar: dict
    summary: str
    attendees: list


class Appointment:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    @token_required
    async def get_appointments(self):
        try:
            query_params = self.event.get('queryStringParameters')
            filters, limit, offset = parse_filter(query_params)

            # Call the service method with filters
            return await self.get_appointments_by_user_id(self.user_id, filters, limit, offset)
            
            # return await self.get_appointments_by_user_id(self.user_id)
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

    @token_required
    async def create_appointment(self):
        try:
            body = json.loads(self.event['body'])

            body['start_time'] = datetime.strptime(body['start_time'], '%Y-%m-%d %H:%M:%S.%f')
            body['end_time'] = datetime.strptime(body['end_time'], '%Y-%m-%d %H:%M:%S.%f')

            data = AppointmentData(**body)

            data_dict = data.model_dump()
            data_dict['smb_id'] = self.user_id

            # Call the service method with filters
            appointment = AppointmentRepository(self)
            return await appointment.save_info(data_dict)
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")
        
    async def get_appointments_by_user_id(self, id, filters=None, limit=10, offset=0):
        query = """
        SELECT 
            ap.*,
            v.id AS visitor_id,
            v.name AS visitor_name,
            v.email AS visitor_email,
            v.phone AS visitor_phone,
            v.location AS visitor_location,
            v.ip_address AS visitor_ip_address,
            v.source AS visitor_source,
            v.is_customer AS visitor_is_customer,
            v.created_at AS visitor_created_at,
            v.updated_at AS visitor_updated_at,
            a.id AS agent_id,
            a.name AS agent_name,
            a.email AS agent_email,
            a.description AS agent_description,
            a.speciality AS agent_speciality,
            a.service AS agent_service,
            a.rating AS agent_rating,
            a.picture AS agent_picture,
            a.created_at AS agent_created_at,
            a.updated_at AS agent_updated_at
        FROM 
            appointments AS ap
        JOIN 
            visitors v ON ap.visitor_id = v.id AND ap.smb_id = v.smb_id
        LEFT JOIN 
            agents a ON ap.agent_id = a.id AND ap.smb_id = a.smb_id
        WHERE 
            ap.smb_id = $1
        """

        params = [id]
        if filters:
            query, filter_params = query_filters(query, filters, alias='ap')
            params.extend(filter_params)

        # Add ORDER BY clause (adjust the column name as needed)
        query += " ORDER BY ap.start_time DESC"

        # Add pagination
        query += f" LIMIT {limit} OFFSET {offset}"

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetch(query, *params)
                    result = dict_from_record(result)

                    count_query = f"SELECT COUNT(*) FROM ({query.split('LIMIT')[0]}) AS count_query"
                    total_count = await connection.fetchval(count_query, *params)

                    if len(result) == 0:
                        return result

                    current_page = math.floor(offset / limit) + 1
                    response = []
                    for r in result:
                        response.append({
                            "id": r["id"],
                            "calendar": r["calendar"],
                            "start_time": r["start_time"],
                            "end_time": r["end_time"],
                            "summary": r["summary"],
                            "attendees": r["attendees"],
                            "visitor": {key[8:]: r[key] for key in r if key.startswith('visitor_')},
                            "assigned_to": {key[6:]: r[key] for key in r if key.startswith('agent_')}
                        })
                    
                    return {
                        "data": response,
                        "total": total_count,
                        "page": current_page
                    }

        except Exception as e:
            raise Exception(f"An error occurred while fetching appointments: {str(e)}")