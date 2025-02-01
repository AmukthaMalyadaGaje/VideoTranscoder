import json
from lambda_function import lambda_handler

with open("test_event.json", "r") as file:
    event = json.load(file)

lambda_handler(event, None)
