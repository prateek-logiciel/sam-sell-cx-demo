from utils.helper import dict_from_record
import json
from datetime import date, datetime


class AppointmentRepository:
    def __init__(self, parent):
        self.event = parent.event
        self.db_pool = parent.db_pool
        self.loop = parent.loop
        self.user_id = parent.user_id
    
    async def update_columns(self, **columns):
        set_clause = ', '.join(f"{key} = ${index + 2}" for index, key in enumerate(columns.keys()))
    
        # query
        query = f"""
            UPDATE appointments
            SET {set_clause}, updated_at = now()
            WHERE id = $1;
        """

        values = [self.user_id] + list(columns.values())
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(query, *values)
                    return True

        except Exception as e:
            raise Exception(f"An error occurred while updating appointment columns: {str(e)}")

    async def save_info(self, data: dict):
        # Prepare keys and values
        keys = []
        values = []
        params = []

        for key, value in data.items():
            keys.append(key)

            if isinstance(value, (dict, list)):
                values.append(f"${len(params) + 1}::jsonb")
                params.append(json.dumps(value))
            elif isinstance(value, (date, datetime)):
                values.append(f"${len(params) + 1}::timestamp")
                params.append(value)  # Pass datetime object directly
            elif value is None:
                values.append('NULL')
            else:
                values.append(f"${len(params) + 1}")
                params.append(value)

        # Create the parameterized INSERT query
        keys_str = ', '.join(keys)
        values_str = ', '.join(values)

        query = f"""
            INSERT INTO appointments ({keys_str})
            VALUES ({values_str})
            RETURNING *;
        """

        print(query)

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    results = await connection.fetch(query, *params)
                    return dict_from_record(results)

        except Exception as e:
            raise Exception(f"Error on adding data of appointment: {str(e)}")
