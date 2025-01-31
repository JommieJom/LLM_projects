import requests

url = "http://localhost:8000/send_message"

data = {
    "message": "How many person in db who are male",
    # "db_path": "databases/sleep.db"
}

response = requests.post(url, json=data)
print(response.json())

# url = "http://localhost:8000/execute_query"
# data = {
#     "db_path": "databases/example.db",
#     "query": "SELECT * FROM customers WHERE city = 'New York'",
#     "limit": 5,
#     "offset": 0
# }

# response = requests.post(url, json=data)
# print(response.json())
