from utils.helper import dict_from_record

class AgentRepository:
    def __init__(self, event, db_pool, loop, user_id):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = user_id
    
    async def update_columns(self, id: int, **columns):
        set_clause = ', '.join(f"{key} = ${index + 2}" for index, key in enumerate(columns.keys()))
    
        # query
        query = f"""
            UPDATE agents
            SET {set_clause}, updated_at = now()
            WHERE id = $1;
        """

        values = [id] + list(columns.values())
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(query, *values)
                    return True

        except Exception as e:
            raise Exception(f"An error occurred while updating agent columns: {str(e)}")

    async def save_agent_preferences(self, data: list):
        # Build the values part for the query using a list of tuples
        values = ", ".join(
            f"({entry['agent_id']}, '{entry['calendar_id']}')" for entry in data
        )

        query = f"""
        INSERT INTO agent_preferences (agent_id, calendar_id)
            VALUES {values}
        ON CONFLICT (agent_id) DO UPDATE
            SET calendar_id = EXCLUDED.calendar_id
        RETURNING agent_id, calendar_id;
        """

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    results = await connection.fetch(query)
                    return dict_from_record(results)

        except Exception as e:
            raise Exception(f"Error on adding data of calendar with agents: {str(e)}")
