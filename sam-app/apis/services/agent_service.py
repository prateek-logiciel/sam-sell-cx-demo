from utils.jwt_utils import token_required
from utils.google_calendar import *
from utils.helper import dict_from_record
from repositories.agent import AgentRepository
from utils.helper import *
import math


class Agent:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    @token_required
    async def get_agents(self):
        try:
            query_params = self.event.get('queryStringParameters')
            filters, limit, offset = parse_filter(query_params)

            return await self.get_agents_by_user_id(self.user_id, filters, limit, offset)
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

    @token_required
    async def assign_agent_to_calendar(self):
        try:
            # Extract agentId, calendarId from the JSON body
            if self.event['body']:
                body = json.loads(self.event['body'])

            agent_repository = AgentRepository(self.event, self.db_pool, self.loop, self.user_id)
            data = body.get('data', [])
            await agent_repository.save_agent_preferences(data)
        except Exception as e:
            raise Exception(f"An error occurred while assigning calendar with agents: {str(e)}")

    async def get_agents_by_user_id(self, id, filters=None, limit=10, offset=0):
        query = """
        SELECT *
        FROM
            agents as a
        LEFT JOIN agent_preferences AS ap ON a.id = ap.agent_id
        WHERE
            a.smb_id = $1
        """

        params = [id]
        if filters:
            query, filter_params = query_filters(query, filters, alias='a')
            params.extend(filter_params)

        # Add pagination
        query += f" LIMIT {limit} OFFSET {offset}"

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetch(query, *params)

                    count_query = f"SELECT COUNT(*) FROM ({query.split('LIMIT')[0]}) AS count_query"
                    total_count = await connection.fetchval(count_query, *params)

                    result = dict_from_record(result)

                    current_page = math.floor(offset / limit) + 1
                    return {
                        "data": result,
                        "total": total_count,
                        "page": current_page
                    }
        except Exception as e:
            raise Exception(f"An error occurred while fetching agents: {str(e)}")
