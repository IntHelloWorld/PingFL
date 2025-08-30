import anthropic

MODEL_NAME = "claude-3-5-sonnet-20241022"
client = anthropic.Anthropic(
    api_key="sk-HgK8u1JLa9TIX8iS5vfiTRERJHCy92jAvBmOtBPFZ5Y3GTly",
    base_url="https://www.dmxapi.cn",
)

tools = [
    {
        "name": "get_customer_info",
        "description": "Retrieves customer information based on their customer ID. Returns the customer's name, email, and phone number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique identifier for the customer.",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "get_order_details",
        "description": "Retrieves the details of a specific order based on the order ID. Returns the order ID, product name, quantity, price, and order status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique identifier for the order.",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "cancel_order",
        "description": "Cancels an order based on the provided order ID. Returns a confirmation message if the cancellation is successful.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique identifier for the order to be cancelled.",
                }
            },
            "required": ["order_id"],
        },
    },
]


def get_customer_info(customer_id):
    # Simulated customer data
    customers = {
        "C1": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
        },
        "C2": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "987-654-3210",
        },
    }
    return customers.get(customer_id, "Customer not found")


def get_order_details(order_id):
    # Simulated order data
    orders = {
        "O1": {
            "id": "O1",
            "product": "Widget A",
            "quantity": 2,
            "price": 19.99,
            "status": "Shipped",
        },
        "O2": {
            "id": "O2",
            "product": "Gadget B",
            "quantity": 1,
            "price": 49.99,
            "status": "Processing",
        },
    }
    return orders.get(order_id, "Order not found")


def cancel_order(order_id):
    # Simulated order cancellation
    if order_id in ["O1", "O2"]:
        return True
    else:
        return False


def process_tool_call(tool_name, tool_input):
    if tool_name == "get_customer_info":
        return get_customer_info(tool_input["customer_id"])
    elif tool_name == "get_order_details":
        return get_order_details(tool_input["order_id"])
    elif tool_name == "cancel_order":
        return cancel_order(tool_input["order_id"])


import json


def chatbot_interaction(user_message):
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")

    messages = [{"role": "user", "content": user_message}]

    response = client.messages.create(
        model=MODEL_NAME, max_tokens=4096, tools=tools, messages=messages
    )

    print(f"\nInitial Response:")
    print(f"Stop Reason: {response.stop_reason}")
    print(f"Content: {response.content}")

    while response.stop_reason == "tool_use":
        tool_use = next(
            block for block in response.content if block.type == "tool_use"
        )
        tool_name = tool_use.name
        tool_input = tool_use.input

        print(f"\nTool Used: {tool_name}")
        print(f"Tool Input:")
        print(json.dumps(tool_input, indent=2))

        tool_result = process_tool_call(tool_name, tool_input)

        print(f"\nTool Result:")
        print(json.dumps(tool_result, indent=2))

        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response.content[0]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(tool_result),
                    }
                ],
            },
        ]

        response2 = client.messages.create(
            model=MODEL_NAME, max_tokens=4096, tools=tools, messages=messages
        )

        print(f"\nResponse:")
        print(f"Stop Reason: {response2.stop_reason}")
        print(f"Content: {response2.content}")

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )

    print(f"\nFinal Response: {final_response}")

    return final_response


chatbot_interaction("Can you tell me the email address for customer C1?")
# chatbot_interaction("What is the status of order O2?")
# chatbot_interaction("Output all of the available tool you have seen.")
# chatbot_interaction("Please cancel order O1 for me.")
