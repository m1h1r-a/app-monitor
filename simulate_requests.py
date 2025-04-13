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

def simulate_network_delay():
    # Occasionally add delays (10% chance of slowdown)
    if random.random() < 0.1:
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)

def get_current_traffic_factor():
    # Simulate daily pattern - more traffic during business hours
    hour = int(time.strftime("%H"))
    if 9 <= hour <= 17:  # Business hours
        return random.uniform(0.8, 1.2)
    elif 18 <= hour <= 22:  # Evening
        return random.uniform(0.4, 0.7)
    else:  # Night
        return random.uniform(0.1, 0.3)

def simulate_error(endpoint):
    # Simulate different types of errors
    error_types = [
        {"status": 400, "message": "Bad Request - Invalid parameters"},
        {"status": 401, "message": "Unauthorized - Authentication required"},
        {"status": 403, "message": "Forbidden - Insufficient permissions"},
        {"status": 404, "message": "Not Found - Resource doesn't exist"},
        {"status": 500, "message": "Internal Server Error - Something went wrong"}
    ]
    
    error = random.choice(error_types)
    log_error(endpoint=endpoint, status_code=error["status"], error_message=error["message"])
    return error

def generate_random_order():
    # generate random order to json server.
    global ORDER_COUNT
    
    # Simulate network delay
    simulate_network_delay()
    
    order = {
        "userId": random.randint(1, 2),  # Based on db.json
        "productId": random.randint(1, 3),  # Based on db.json
        "quantity": random.randint(1, 5),
        "date": time.strftime("%Y-%m-%d"),
        "processed": "false",  # String "false" to match db.json format
    }

    log_request(endpoint=API_URL, method="POST", data=order)

    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(API_URL)
        return
    
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
    simulate_network_delay()
    
    log_request(endpoint=API_URL, method="GET")
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(API_URL)
        return

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
    simulate_network_delay()
    
    unprocessed_url = API_URL + "?processed=false"
    log_request(endpoint=unprocessed_url, method="GET")
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(unprocessed_url)
        return

    try:
        response = requests.get(unprocessed_url)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=unprocessed_url,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "unprocessed_orders": response.json(),
                },
            )
        else:
            log_error(
                endpoint=unprocessed_url,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=unprocessed_url, status_code=500, error_message=str(e))


def mark_all_as_processed():
    # Mark all unprocessed orders as processed.
    simulate_network_delay()
    
    log_request(endpoint=API_URL, method="PATCH", data={"processed": "true"})
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(API_URL)
        return

    try:
        response = requests.patch(API_URL, json={"processed": "true"})
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
    simulate_network_delay()
    
    processed_url = API_URL + "?processed=true"
    log_request(endpoint=processed_url, method="GET")
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(processed_url)
        return

    try:
        response = requests.get(processed_url)
        response_time = round(time.time() - start_time, 4)

        if response.status_code == 200:
            log_response(
                endpoint=processed_url,
                status_code=200,
                response_data={
                    "response_time": response_time,
                    "processed_orders": response.json(),
                },
            )
        else:
            log_error(
                endpoint=processed_url,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=processed_url, status_code=500, error_message=str(e))


def delete_order(order_id):
    # Delete an order by its ID.
    simulate_network_delay()
    
    url = f"{API_URL}/{order_id}"
    log_request(endpoint=url, method="DELETE")
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        simulate_error(url)
        return

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
                endpoint=url,
                status_code=response.status_code,
                error_message=response.text,
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=url, status_code=500, error_message=str(e))


def simulate_traffic_burst():
    # Simulate a sudden burst of traffic
    print("⚡ Traffic burst starting...")
    burst_requests = random.randint(10, 20)
    
    for _ in range(burst_requests):
        thread = threading.Thread(target=generate_random_order)
        thread.start()
        time.sleep(random.uniform(0.1, 0.3))  # Small delay between burst requests
    
    print(f"⚡ Traffic burst completed: {burst_requests} requests")


def trigger_other_endpoints():
    # Call other API endpoints after every 10 orders.
    get_all_orders()
    delete_order(random.randint(1, 2))  # Randomly delete order 1 or 2
    get_unprocessed_orders()
    mark_all_as_processed()
    get_processed_orders()


def simulate_load():
    # Continuously generate random orders and trigger logs every 10 orders.
    global ORDER_COUNT
    
    print(f"Simulation started. API URL: {API_URL}")
    
    # Initial delay to ensure all services are up
    time.sleep(10)
    
    burst_timer = 0

    while True:
        # Determine current traffic level based on time of day
        traffic_factor = get_current_traffic_factor()
        delay = random.uniform(2, 7) / traffic_factor
        
        thread = threading.Thread(target=generate_random_order)
        thread.start()
        
        # Occasionally trigger other operations
        with LOCK:
            if ORDER_COUNT % 10 == 0 and ORDER_COUNT > 0:
                print("\nTriggering other endpoints after 10 orders...\n")
                thread_trigger = threading.Thread(target=trigger_other_endpoints)
                thread_trigger.start()
        
        # Occasionally create traffic bursts
        burst_timer += 1
        if burst_timer >= 20:  # Every ~20 regular requests
            if random.random() < 0.3:  # 30% chance
                thread_burst = threading.Thread(target=simulate_traffic_burst)
                thread_burst.start()
            burst_timer = 0
            
        time.sleep(delay)


if __name__ == "__main__":
    # Wait a bit to ensure all services are up
    print("Waiting for services to be ready...")
    time.sleep(10)
    simulate_load()