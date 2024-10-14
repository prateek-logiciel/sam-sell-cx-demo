
# Alembic: Create Our First Migration
### 1️⃣ — Create a Migration Script
To create a new migration script, use the following command:
```sh
alembic revision -m "create schema sellcx"
```

This will generate a new file in the versions directory within your Alembic project. The file will be named with the current timestamp and a unique identifier, like so:
```sh
{current_timestamp}_{unique_identifier}_create_schema_sellcx.py
```
**Current Timestamp:** The timestamp when the migration was created.

**Unique Identifier:** A unique identifier for the migration (e.g., 9ec3d7e4bde9).

**Message:** The message provided in the command, with spaces replaced by underscores.

### 2️⃣ — Modify the Migration File
To create the schema for the project, you will need to modify the migration file. Since Alembic does not have a specific method for creating a schema, you can use the op.execute method to run the SQL query.

Modify the upgrade() and downgrade() methods as follows:

```sh
def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS sellcx;')

def downgrade() -> None:
    op.execute('DROP SCHEMA IF EXISTS sellcx CASCADE;')
```

### 3️⃣ — Execute the Migration
To apply the migration and create the schema in the database, run the following command:

```sh
alembic upgrade head
```
If the migration is successful, you will see a "Done" message. You can also verify that the new schema has been created in the database and that the Alembic version table has been updated.

### To Downgrade previous version

```sh
alembic downgrade -1
```

### To Downgrade particular version

```sh
alembic downgrade <revision_id>
```

### To Check version history

```sh
alembic history
```

The alembic history command is used to display a list of the migration scripts that have been applied or are available in our Alembic project. It shows the revision history of the database migrations in reverse chronological order (latest first).

### To run the seeder files

```sh
python3 -m alembic.seeder.seed
python3 -m alembic.seeder.agent_seed 
```