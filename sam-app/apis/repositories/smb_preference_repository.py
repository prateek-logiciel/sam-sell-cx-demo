import json

class SMBPreferences:
    def __init__(self, event, db_pool, loop, user_id):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = user_id

    async def update_calendar_settings(self, data, key="calendars", id=None):
        query = """
        UPDATE smb_preferences
        SET calendar_settings = jsonb_set(
            COALESCE(calendar_settings::jsonb, '{}'),
            $2::text[],
            $3::jsonb
        )
        WHERE smb_id = $1;
        """

        json_data = data.get(key)
        key_path = [key]
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(query, self.user_id, key_path, json.dumps(json_data))
                    return True

        except Exception as e:
            raise Exception(f"An error occurred while updating calendar listing: {str(e)}")