import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models.agent import Agent

load_dotenv()


# Fetch environment variables
db_host = os.getenv("STATE_HOST")
db_user = os.getenv("STATE_USER")
db_password = os.getenv("STATE_PASSWORD")
db_port = os.getenv("STATE_PORT")
db_name = os.getenv("STATE_DATABASE")

# Use environment variables in database URL
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Set up the database engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Define the data to seed
agents_data = [
    {
        "smb_id": 119,
        "name": "John Doe (Gutter Expert)",
        "email": "gutter_expert@sell.cx",
        "description": "Experienced gutter agent specializing in home improvements.",
        "speciality": "Expert Recognization, Gutter Installation, Gutter Maintenance, Gutter Repair, Water Damage Prevention",
        "service": "gutter",
        "rating": 5.0,
        "picture": "https://cdn-icons-png.flaticon.com/512/3135/3135915.png"
    },
    {
        "smb_id": 116,
        "name": "Jane Smith (Roofing Specialist)",
        "email": "roof_specialist@sell.cx",
        "description": "Skilled roofing agent with over 10 years of experience.",
        "speciality": "Roof Inspection, Roof Installation, Roof Repair",
        "service": "roofing",
        "rating": 4.8,
        "picture": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    },
    {
        "smb_id": 116,
        "name": "John Doe (Gutter Expert)",
        "email": "gutter_expert@sell.cx",
        "description": "Experienced gutter agent specializing in home improvements.",
        "speciality": "Expert Recognization, Gutter Installation, Gutter Maintenance, Gutter Repair, Water Damage Prevention",
        "service": "gutter",
        "rating": 5.0,
        "picture": "https://cdn-icons-png.flaticon.com/512/3135/3135915.png"
    },
    {
        "smb_id": 119,
        "name": "Jane Smith (Roofing Specialist)",
        "email": "roof_specialist@sell.cx",
        "description": "Skilled roofing agent with over 10 years of experience.",
        "speciality": "Roof Inspection, Roof Installation, Roof Repair",
        "service": "roofing",
        "rating": 4.8,
        "picture": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    }
]

# Seed the data
def seed_agents():
    for agent_data in agents_data:
        agent = Agent(
            smb_id=agent_data['smb_id'],
            name=agent_data['name'],
            email=agent_data['email'],
            description=agent_data['description'],
            speciality=agent_data['speciality'],
            service=agent_data['service'],
            rating=agent_data['rating'],
            picture=agent_data['picture']
        )
        session.add(agent)

    session.commit()
    print("Seed data added successfully.")

if __name__ == "__main__":    
    # Call the seeder function
    seed_agents()
