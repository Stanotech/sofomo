Geolocation API

Geolocation API is a Django REST Framework (DRF) application that allows you to retrieve, add, and delete geolocation data based on an IP address or URL. The application uses an external API (IPStack) to fetch geolocation data.
Features

    GET /geolocation/: Retrieve geolocation data based on an IP address or URL.
    POST /geolocation/: Add new geolocation data based on an IP address or URL.
    DELETE /geolocation/: Delete geolocation data based on an IP address or URL.

Requirements

    Docker
    Docker Compose
    Python 3.10
    IPStack API key (you can get it from ipstack.com)

Installation


    git clone https://github.com/Stanotech/sofomo.git
    

Create a .env file in the root directory and fill it with the following data:

    POSTGRES_DB=geolocation_db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    DATABASE_URL=postgres://user:password@db:5432/geolocation_db
    IPSTACK_API_KEY=your_ipstack_api_key

bash:

    docker-compose up --build

The application will be available at http://localhost:8000.


API Usage
Retrieving Geolocation Data (GET)

Endpoint: /geolocation/
Parameters:

    ip (optional): IP address.
    url (optional): URL.

Example Request:


    curl -X GET "http://localhost:8000/geolocation/?ip=192.168.1.1"

Example Response:

json:

    [
        {
            "ip_address": "192.168.1.1",
            "url": null,
            "country": "Poland",
            "region": "Mazovia",
            "city": "Warsaw",
            "latitude": 52.2297,
            "longitude": 21.0122
        }
    ]

Adding Geolocation Data (POST)

Endpoint: /geolocation/
Parameters:

    ip (optional): IP address.
    url (optional): URL.

Example Request:

    curl -X POST "http://localhost:8000/geolocation/" -H "Content-Type: application/json" -d '{"ip": "192.168.1.1"}'

Example Response:

json:

    {
        "ip_address": "192.168.1.1",
        "url": null,
        "country": "Poland",
        "region": "Mazovia",
        "city": "Warsaw",
        "latitude": 52.2297,
        "longitude": 21.0122
    }

Deleting Geolocation Data (DELETE)

Endpoint: /geolocation/
Parameters:

    ip (optional): IP address.
    url (optional): URL.

Example Request:

    curl -X DELETE "http://localhost:8000/geolocation/?ip=192.168.1.1"

Example Response:

json:

    {
        "message": "Data deleted."
    }

Testing

To run unit and integration tests, follow these steps:

Ensure Docker is running:

    docker-compose up -d

Run the tests:

    docker-compose exec web pytest
