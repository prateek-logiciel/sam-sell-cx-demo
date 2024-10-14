# Application

## Installation
### 1. Install Dependencies

Ensure you have Python 3.10+ and pip installed. Then, install the required dependencies:

```sh
pip install -r requirements.txt
```
### 2. Set Up Environment Variables

Create a .env file in the root directory and add the following environment variables:

``` sh
STATE_HOST=your_db_host
STATE_USER=your_db_user
STATE_PASSWORD=your_db_password
STATE_PORT=your_db_port
STATE_DATABASE=your_db_name
```

## Usage
### 1. Run the Application

To start the FastAPI server, use the following command:

```sh
uvicorn main:app --reload
```
