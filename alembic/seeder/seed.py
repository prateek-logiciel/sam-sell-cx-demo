import os
import asyncpg
import asyncio
from dotenv import load_dotenv

load_dotenv() 

# Seed 'smbs' table and return the inserted IDs
async def seed_smbs(conn):
    async with conn.transaction():
        smb_records = await conn.fetch("""
            INSERT INTO smbs (id, name,website,status,created_at,updated_at) VALUES
                (1, 'Example SMB','example.com','active','2024-08-14 10:30:54.696009',NULL),
                (2, 'Highland Contractor','highlandcontractors.net','active','2024-08-14 13:25:54.330334',NULL),
                (6, 'Allstate Roofing','400roof.com','active','2024-08-14 10:30:13.839595',NULL);
        """)
        smb_ids = [record['id'] for record in smb_records]
        print(f"Inserted SMB IDs: {smb_ids}")
        return smb_ids

# Seed 'smb_preferences' table with valid smb_id values
async def seed_smb_preferences(conn, smb_ids):
    async with conn.transaction():
        await conn.fetch("""
            INSERT INTO public.smb_preferences (smb_id,calendar_settings,storage_settings) VALUES
                (2,NULL,NULL),
                (6,NULL,'{"source": {"type": "neo4j", "config": "HLD"}}'),
                (1,NULL,'{}');
        """)

# Seed 'visitors' table and return the inserted IDs
async def seed_visitors(conn, smb_ids):
    async with conn.transaction():
        visitor_records = await conn.fetch("""
            INSERT INTO visitors (session_id,smb_id,name,email,ip_address,"location",status,browser_info,created_at,updated_at,is_email_verified,is_phone_verified,phone) VALUES
                ('4a1b8c31-240e-4aa2-b6ba-946e795ecefb',1,NULL,NULL,'192.168.1.1','New York, USA','active','{"language": "en-US", "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", "screenResolution": "1536x864"}','2024-08-14 10:30:13.839595',NULL,false,false,NULL),
                ('1fde51c7-1d78-4be5-8799-0f4ff5d3ffc8',2,NULL,NULL,'192.168.1.1','New York, USA','active','{"language": "en-US", "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", "screenResolution": "1536x864"}','2024-08-14 10:30:54.696009',NULL,false,false,NULL),
                ('5af3dc82-0813-4cf4-afad-72c99ce87501',6,NULL,NULL,'182.120.0.1','New York, USA','active','{"language": "en-US", "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", "screenResolution": "1536x864"}','2024-08-14 13:25:54.330334',NULL,false,false,NULL),
                ('550e8400-e29b-41d4-a716-446655440003',6,'Bob Brown','bob.brown@example.com','192.168.1.4','Houston','active','{"browser": "Edge", "version": "105"}','2024-08-28 06:44:48.550863','2024-08-28 06:44:48.550863',false,false,NULL),
                ('550e8400-e29b-41d4-a716-446655440002',6,'Harsha','harsha@sellcx.com','192.168.1.3','Chicago','inactive','{"browser": "Safari", "version": "14"}','2024-08-28 06:44:48.550863','2024-08-28 06:44:48.550863',false,false,NULL),
                ('550e8400-e29b-41d4-a716-446655440000',1,'Vikash Pathak','vikash@sellcx.com','192.168.1.1','Florida, 8987DC, USA','active','{"browser": "Chrome", "version": "105"}','2024-08-28 06:44:48.550863','2024-08-28 06:44:48.550863',true,true,'+917889026462'),
                ('550e8400-e29b-41d4-a716-446655440001',6,'David Buzzelli','','192.168.1.2','Los Angeles','active','{"browser": "Firefox", "version": "100"}','2024-08-28 06:44:48.550863','2024-08-28 06:44:48.550863',false,false,NULL)
            ON CONFLICT DO NOTHING
            RETURNING id; """)
        
        visitor_ids = [record['id'] for record in visitor_records]
        print(f"Inserted Visitor IDs: {visitor_ids}")
        return visitor_ids

# Main function to seed all tables
async def seed_all():
    conn = await asyncpg.connect(
        host=os.getenv("STATE_HOST"),
        user=os.getenv("STATE_USER"),
        password=os.getenv("STATE_PASSWORD"),
        port=os.getenv("STATE_PORT"),
        database=os.getenv("STATE_DATABASE"),
    )
    
    try:
        # Seed smbs and get valid smb IDs
        smb_ids = await seed_smbs(conn)

        # # Seed smb_preferences with valid smb_ids
        await seed_smb_preferences(conn, smb_ids)

        # # Seed visitors with valid smb_ids and get valid visitor IDs
        await seed_visitors(conn, smb_ids)

        # Seed issues using valid visitor_ids and smb_ids
        # await seed_issues(conn, smb_ids, visitor_ids)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        # If an error occurs, the transaction is automatically rolled back

    finally:
        await conn.close()

# Run the seeders
if __name__ == "__main__":
    asyncio.run(seed_all())
