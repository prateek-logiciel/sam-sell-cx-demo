from utils.jwt_utils import token_required
from utils.google_calendar import *
from utils.helper import *
import math

class Leads:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    @token_required
    async def get_visitors(self):
        try:
            query_params = self.event.get('queryStringParameters')
            filters, limit, offset = parse_filter(query_params)

            return await self.get_visitors_by_id(self.user_id, filters, limit, offset)
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while calendar processing: {str(e)}")

    async def get_visitors_by_id(self, id, filters=None, limit=10, offset=0):
        query = """
        SELECT *
        FROM
            visitors as v
        WHERE
            v.smb_id = $1
            AND v.name IS NOT NULL
            AND v.name != ''
        """

        params = [id]
        if filters:
            query, filter_params = query_filters(query, filters, alias='v')
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
            raise Exception(f"An error occurred while fetching Leads: {str(e)}")