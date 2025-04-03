import threading
import requests
import random
import time

API_URL = "http://localhost:3000/orders"

def generate_random_order():
    # generate random order to json server
    order = {
        "userId": random.randint(1, 15),
        "productId": random.randint(1, 3),
        "quantity": random.randint(1, 5),
        "date": time.strftime("%Y-%m-%d"),
        "processed": False
    }
    
    response = requests.post(API_URL, json=order)
    if response.status_code == 201:
        print(f"Order created: {order}")
    else:
        print(f"Failed to create order: {response.status_code}, {response.text}")

def simulate_load():
    # multiple threads
    while True:
        thread = threading.Thread(target=generate_random_order)
        thread.start()
        # random delay between 2 to 7 seconds
        time.sleep(random.uniform(2, 7))  

if __name__ == "__main__":
    simulate_load()
