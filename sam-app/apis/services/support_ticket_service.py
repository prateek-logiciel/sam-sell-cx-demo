from utils.jwt_utils import token_required
from utils.google_calendar import *
from utils.helper import *
import math


class SupportTicket:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    @token_required
    async def get_support_tickets(self):
        try:
            query_params = self.event.get('queryStringParameters')
            filters, limit, offset = parse_filter(query_params)

            return await self.get_issues_by_id(self.user_id, filters, limit, offset)
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

    @token_required
    async def assign_agent_to_ticket(self):
        try:
            issue_id = self.event['pathParameters']['ticket_id']
            agent_id = self.event['pathParameters']['agent_id']

            # Extract status from the JSON body
            status = None
            if self.event['body']:
                body = json.loads(self.event['body'])
                status = body.get('status', None)

            query = """
                INSERT INTO issues_agents (issue_id, agent_id, status)
                VALUES ($1, $2, $3)
                ON CONFLICT (issue_id, agent_id)
                DO UPDATE SET status = COALESCE(EXCLUDED.status, issues_agents.status)
                RETURNING issue_id, agent_id, status;
            """

            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query, int(issue_id), int(agent_id), status)
                    result = dict_from_record(result)
                    return result
        except Exception as e:
            raise Exception(f"An error occurred while fetching Support tickets: {str(e)}")
    
    async def get_issues_by_id(self, id, filters=None, limit=10, offset=0):
        query = """
        SELECT
            i.id AS id,
            i.type AS type,
            i.description AS description,
            i.status AS status,
            i.created_at AS created_at,
            i.updated_at AS updated_at,
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
            s.id AS smb_id,
            s.name AS smb_name,
            s.email AS smb_email,
            s.website AS smb_website,
            s.status AS smb_status,
            s.phone AS smb_phone,
            s.created_at AS smb_created_at,
            s.updated_at AS smb_updated_at,
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
            issues i
        JOIN
            visitors v ON i.fk_visitor_id = v.id
        JOIN
            smbs s ON i.fk_smb_id = s.id
        JOIN
            agents a ON i.fk_smb_id = a.smb_id
        JOIN
            issues_agents ia ON ia.issue_id = i.id AND ia.agent_id = a.id
        WHERE
            i.fk_smb_id = $1
        """

        params = [id]
        filter_query = ''
        if filters:
            filter_query, filter_params = query_filters('', filters, alias='k')
            params.extend(filter_params)

        # Add pagination
        query = f"WITH issue_data AS ( {query} ) SELECT * FROM issue_data as k WHERE 1=1 {filter_query}"
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
                            "type": r["type"],
                            "description": r["description"],
                            "status": r["status"],
                            "created_at": r["created_at"],
                            "updated_at": r["updated_at"],
                            "visitor": {key[8:]: r[key] for key in r if key.startswith('visitor_')},
                            "smb": {key[4:]: r[key] for key in r if key.startswith('smb_')},
                            "assigned_to": {key[6:]: r[key] for key in r if key.startswith('agent_')}
                        })

                    return {
                        "data": response,
                        "total": total_count,
                        "page": current_page
                    }
        except Exception as e:
            raise Exception(f"An error occurred while fetching Support tickets: {str(e)}")