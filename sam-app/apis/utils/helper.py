from urllib.parse import urlparse
from datetime import datetime, timezone
import uuid
import json
import asyncpg

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": "true"
}


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")

def extract_domain(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the netloc (domain) from the parsed URL
    domain = parsed_url.netloc

    # If the domain includes 'www.', remove it
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain

def dict_from_record(record):
    if record is None:
        return None
    
    # Handle single record or list of records
    if isinstance(record, (asyncpg.Record, dict)):
        return convert_record_to_dict(record)
    
    return [convert_record_to_dict(row) for row in record]

def convert_record_to_dict(row):
    return {
        key: (str(value) if isinstance(value, (datetime, uuid.UUID)) else value)
        for key, value in row.items()
    }


def format_response(status_code, data):
    body = {
        "success": 200 <= status_code < 300,
        "data": data
    }

    if isinstance(data, dict) and 'total' in data:
        body = {
        "success": 200 <= status_code < 300,
        "data": data['data'],
        "total": data.get('total', None),
        "page": data.get('page', None)
    }

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body)
    }

def parse_filter(query_params):
    # Extract filter parameters
    filters = {}

    if query_params is None:
        return None, 10, 0

    for key, value in query_params.items():
        if key.endswith('_eq'):
            filters[key[:-3]] = {'eq': value}
        elif key.endswith('_from'):
            base_key = key[:-5]
            if base_key not in filters:
                filters[base_key] = {}
            filters[base_key]['from'] = value
        elif key.endswith('_to'):
            base_key = key[:-3]
            if base_key not in filters:
                filters[base_key] = {}
            filters[base_key]['to'] = value

    # Handle start_time filter specifically
    if 'start_time' in filters:
        if 'to' not in filters['start_time']:
            # If start_time_to is not provided, use current UTC time
            filters['start_time']['to'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Extract pagination parameters
    limit = int(query_params.get('limit', 10))
    offset = int(query_params.get('offset', 0))
    return filters, limit, offset

def query_filters(query, filters, alias):
    params = []
    i = 1
    for key, condition in filters.items():
        if 'eq' in condition:
            i += 1
            query += f" AND {alias}.{key} = ${i}"
            params.append(condition['eq'])
        if 'from' in condition:
            i += 1
            query += f" AND {alias}.{key} >= ${i}"
            params.append(datetime.strptime(f"{condition['from']} 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"))
        if 'to' in condition:
            i += 1
            query += f" AND {alias}.{key} <= ${i}"
            params.append(datetime.strptime(f"{condition['to']} 23:59:59.999", "%Y-%m-%d %H:%M:%S.%f"))
            
    return query, params
