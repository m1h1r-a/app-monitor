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

# Define more distinct endpoints for better visualization
BASE_URL = os.environ.get("API_URL", "http://json-server:3000").split("/orders")[0]
ENDPOINTS = {
    "orders": f"{BASE_URL}/orders",
    "users": f"{BASE_URL}/users",
    "products": f"{BASE_URL}/products",
    "analytics": f"{BASE_URL}/analytics"
}

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

def generate_data_for_endpoint(endpoint_key):
    if endpoint_key == "orders":
        return {
            "userId": random.randint(1, 15),
            "productId": random.randint(1, 3),
            "quantity": random.randint(1, 5),
            "date": time.strftime("%Y-%m-%d"),
            "processed": False,
        }
    elif endpoint_key == "users":
        return {
            "name": f"User{random.randint(100, 999)}",
            "email": f"user{random.randint(100, 999)}@example.com",
            "active": random.choice([True, False])
        }
    elif endpoint_key == "products":
        return {
            "name": f"Product{random.randint(100, 999)}",
            "price": round(random.uniform(10.0, 100.0), 2),
            "inStock": random.choice([True, False])
        }
    elif endpoint_key == "analytics":
        return {
            "period": random.choice(["daily", "weekly", "monthly"]),
            "metric": random.choice(["sales", "views", "conversions"])
        }
    return {}

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

def make_request(endpoint, method, data=None):
    global ORDER_COUNT
    simulate_network_delay()
    
    log_request(endpoint=endpoint, method=method, data=data)
    start_time = time.time()
    
    # Simulate random errors (5% chance)
    if random.random() < 0.05:
        error = simulate_error(endpoint)
        return
    
    try:
        if method == "GET":
            response = requests.get(endpoint)
        elif method == "POST":
            response = requests.post(endpoint, json=data)
        elif method == "PUT":
            # Get a random ID to update
            item_id = random.randint(1, 10)
            response = requests.put(f"{endpoint}/{item_id}", json=data)
        elif method == "DELETE":
            # Get a random ID to delete
            item_id = random.randint(1, 10)
            response = requests.delete(f"{endpoint}/{item_id}")
        elif method == "PATCH":
            # Get a random ID to patch
            item_id = random.randint(1, 10)
            response = requests.patch(f"{endpoint}/{item_id}", json=data)
        
        response_time = round(time.time() - start_time, 4)
        
        if 200 <= response.status_code < 300:
            if method == "POST" and endpoint == ENDPOINTS["orders"]:
                with LOCK:
                    ORDER_COUNT += 1
            
            response_data = {
                "response_time": response_time
            }
            
            # Try to include JSON response if available
            try:
                if response.text:
                    response_data.update(response.json())
            except:
                response_data["message"] = f"{method} operation completed"
                
            log_response(
                endpoint=endpoint,
                status_code=response.status_code,
                response_data=response_data
            )
        else:
            log_error(
                endpoint=endpoint,
                status_code=response.status_code,
                error_message=response.text
            )
    except requests.exceptions.RequestException as e:
        log_error(endpoint=endpoint, status_code=500, error_message=str(e))

def simulate_traffic_burst():
    # Simulate a sudden burst of traffic
    print("⚡ Traffic burst starting...")
    burst_requests = random.randint(15, 30)
    
    for _ in range(burst_requests):
        endpoint_key = random.choice(list(ENDPOINTS.keys()))
        endpoint = ENDPOINTS[endpoint_key]
        method = random.choices(
            ["GET", "POST", "PUT", "DELETE", "PATCH"], 
            weights=[0.6, 0.2, 0.1, 0.05, 0.05]
        )[0]
        data = None
        if method in ["POST", "PUT", "PATCH"]:
            data = generate_data_for_endpoint(endpoint_key)
        
        thread = threading.Thread(target=make_request, args=(endpoint, method, data))
        thread.start()
        time.sleep(random.uniform(0.1, 0.3))  # Small delay between burst requests
    
    print(f"⚡ Traffic burst completed: {burst_requests} requests")

def simulate_load():
    # Continuously generate random requests with realistic patterns
    global ORDER_COUNT

    print(f"Simulation started. Base URL: {BASE_URL}")
    print(f"Available endpoints: {', '.join(ENDPOINTS.keys())}")

    # Initial delay to ensure all services are up
    time.sleep(10)
    
    burst_timer = 0
    
    while True:
        # Determine current traffic level
        traffic_factor = get_current_traffic_factor()
        delay = random.uniform(2, 7) / traffic_factor
        
        # Select random endpoint and method
        endpoint_key = random.choice(list(ENDPOINTS.keys()))
        endpoint = ENDPOINTS[endpoint_key]
        
        method = random.choices(
            ["GET", "POST", "PUT", "DELETE", "PATCH"], 
            weights=[0.6, 0.2, 0.1, 0.05, 0.05]
        )[0]
        
        # Generate appropriate data based on method and endpoint
        data = None
        if method in ["POST", "PUT", "PATCH"]:
            data = generate_data_for_endpoint(endpoint_key)
        
        thread = threading.Thread(target=make_request, args=(endpoint, method, data))
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

def trigger_other_endpoints():
    # Call various endpoints to generate diverse metrics
    endpoints = list(ENDPOINTS.values())
    
    for endpoint in endpoints:
        # Make a GET request to each endpoint
        thread = threading.Thread(target=make_request, args=(endpoint, "GET", None))
        thread.start()
        time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    # Wait a bit to ensure all services are up
    print("Waiting for services to be ready...")
    time.sleep(10)
    simulate_load()