import os
import random
import threading
import time

import requests

from producer import log_error, log_request, log_response

# env vars used:
print(
    f"DEBUG - Environment KAFKA_BROKER: '{os.environ.get('KAFKA_BROKER', 'not set')}'"
)
print(f"DEBUG - Environment API_URL: '{os.environ.get('API_URL', 'not set')}'")

API_URL = os.environ.get("API_URL", "http://json-server:3000/orders")
ORDER_COUNT = 0
LOCK = threading.Lock()


def generate_random_order():
    # generate random order to json server.
    global ORDER_COUNT
    order = {
        "userId": random.randint(1, 15),
        "productId": random.randint(1, 3),
        "quantity": random.randint(1, 5),
        "date": time.strftime("%Y-%m-%d"),
        "processed": False,
    }

    log_request(endpoint=API_URL, method="POST", data=order)

    start_time = time.time()
    try:
        response = requests.post(API_URL, json=order)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 201:
            with LOCK:
                ORDER_COUNT += 1
            log_response(
                endpoint=API_URL,
                status_code=201,
                response_data={"response_time": response_time, **response.json()},
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=API_URL, status_code=500, error_message=str(e))


def get_all_orders():
    # Fetch all orders from JSON Server.
    log_request(endpoint=API_URL, method="GET")
    start_time = time.time()

    try:
        response = requests.get(API_URL)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=API_URL,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "orders": response.json(),
                },
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=API_URL, status_code=500, error_message=str(e))


def get_unprocessed_orders():
    # Fetch only unprocessed orders.
    unprocessed_url = API_URL + "?processed=false"
    log_request(endpoint=unprocessed_url, method="GET")
    start_time = time.time()

    try:
        response = requests.get(unprocessed_url)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=API_URL,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "unprocessed_orders": response.json(),
                },
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=API_URL, status_code=500, error_message=str(e))


def mark_all_as_processed():
    # Mark all unprocessed orders as processed.
    log_request(endpoint=API_URL, method="PATCH", data={"processed": True})
    start_time = time.time()

    try:
        response = requests.patch(API_URL, json={"processed": True})
        response_time = round(time.time() - start_time, 4)

        if response.status_code in [200, 204]:
            log_response(
                endpoint=API_URL,
                status_code=response.status_code,
                response_data={
                    "response_time": response_time,
                    "message": "All orders processed.",
                },
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=API_URL, status_code=500, error_message=str(e))


def get_processed_orders():
    # Fetch only processed orders.
    processed_url = API_URL + "?processed=true"
    log_request(endpoint=processed_url, method="GET")
    start_time = time.time()

    try:
        response = requests.get(processed_url)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=API_URL,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "processed_orders": response.json(),
                },
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=API_URL, status_code=500, error_message=str(e))


def delete_order(order_id):
    # Delete an order by its ID.
    url = f"{API_URL}/{order_id}"
    log_request(endpoint=url, method="DELETE")

    start_time = time.time()
    try:
        response = requests.delete(url)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=url,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "message": f"Order {order_id} deleted successfully.",
                },
            )
        elif response.status_code == 404:
            log_error(
                endpoint=url,
                status_code=response.status_code,
                error_message=f"Order {order_id} not found.",
            )
        else:
            log_error(
                endpoint=API_URL,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=url, status_code=500, error_message=str(e))


def trigger_other_endpoints():
    # Call other API endpoints after every 10 orders.
    get_all_orders()
    delete_order(2)
    get_unprocessed_orders()
    mark_all_as_processed()
    get_processed_orders()


def simulate_load():
    # Continuously generate random orders and trigger logs every 10 orders.
    global ORDER_COUNT

    print(f"Simulation started. API URL: {API_URL}")

    while True:
        thread = threading.Thread(target=generate_random_order)
        thread.start()
        time.sleep(random.uniform(2, 7))

        with LOCK:
            if ORDER_COUNT % 10 == 0 and ORDER_COUNT > 0:
                print("\nTriggering other endpoints after 10 orders...\n")
                thread_trigger = threading.Thread(target=trigger_other_endpoints)
                thread_trigger.start()


if __name__ == "__main__":
    # Wait a bit to ensure all services are up
    print("Waiting for services to be ready...")
    time.sleep(10)
    simulate_load()
