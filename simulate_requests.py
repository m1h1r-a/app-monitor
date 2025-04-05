import threading
import requests
import random
import time
from producer import log_request, log_response, log_error  

API_URL = "http://localhost:3000/orders"
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
        "processed": False
    }

    log_request(endpoint=API_URL, method="POST", data=order)  

    start_time = time.time()  
    response = requests.post(API_URL, json=order)
    response_time = round(time.time() - start_time, 4)  

    if response.status_code == 201:
        with LOCK:
            ORDER_COUNT += 1
        log_response(endpoint=API_URL, status_code=201, response_data={"response_time": response_time, **response.json()})
    else:
        # log_error(endpoint=API_URL, error_message=response.text)
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def get_all_orders():
    #Fetch all orders from JSON Server.
    log_request(endpoint=API_URL, method="GET")
    start_time = time.time()
    
    response = requests.get(API_URL)
    response_time = round(time.time() - start_time, 4)
    
    if response.status_code == 200:
        log_response(endpoint=API_URL, status_code=200, response_data={"response_time": response_time, "orders": response.json()})
    else:
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def get_unprocessed_orders():
    #Fetch only unprocessed orders.
    log_request(endpoint=API_URL + "?processed=false", method="GET")
    start_time = time.time()
    
    response = requests.get(API_URL + "?processed=false")
    response_time = round(time.time() - start_time, 4)
    
    if response.status_code == 200:
        log_response(endpoint=API_URL, status_code=200, response_data={"response_time": response_time, "unprocessed_orders": response.json()})
    else:
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def mark_all_as_processed():
    #Mark all unprocessed orders as processed.
    log_request(endpoint=API_URL, method="PATCH", data={"processed": True})
    start_time = time.time()

    response = requests.patch(API_URL, json={"processed": True})
    response_time = round(time.time() - start_time, 4)

    if response.status_code in [200, 204]:
        log_response(endpoint=API_URL, status_code=response.status_code, response_data={"response_time": response_time, "message": "All orders processed."})
    else:
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def get_processed_orders():
    #Fetch only processed orders.
    log_request(endpoint=API_URL + "?processed=true", method="GET")
    start_time = time.time()
    
    response = requests.get(API_URL + "?processed=true")
    response_time = round(time.time() - start_time, 4)
    
    if response.status_code == 200:
        log_response(endpoint=API_URL, status_code=200, response_data={"response_time": response_time, "processed_orders": response.json()})
    else:
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def delete_order(order_id):
    #Delete an order by its ID.
    url = f"{API_URL}/{order_id}"
    log_request(endpoint=url, method="DELETE")  

    start_time = time.time()
    response = requests.delete(url)
    response_time = round(time.time() - start_time, 4)

    if response.status_code == 200:
        log_response(endpoint=url, status_code=200, response_data={"response_time": response_time, "message": f"Order {order_id} deleted successfully."})
    elif response.status_code == 404:
        log_error(endpoint=url, status_code=response.status_code, error_message=f"Order {order_id} not found.")
    else:
        log_error(endpoint=API_URL, status_code=response.status_code, error_message=response.text)

def trigger_other_endpoints():
    #Call other API endpoints after every 10 orders.
    get_all_orders()
    delete_order(2)
    get_unprocessed_orders()
    mark_all_as_processed()
    get_processed_orders()

def simulate_load():
    #Continuously generate random orders and trigger logs every 10 orders.
    global ORDER_COUNT

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
    simulate_load()
