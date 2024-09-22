import uuid


def generate_ticket_number():
    return str(uuid.uuid4())


def format_phone_number(phone_number):
    # Remove any spaces or non-numeric characters like '+'
    phone_number = phone_number.strip().replace(" ", "").replace("+", "")

    # If the number starts with '07', replace it with '2547'
    if phone_number.startswith("07"):
        phone_number = "254" + phone_number[1:]

    # If the number starts with '01', replace it with '2541'
    elif phone_number.startswith("01"):
        phone_number = "254" + phone_number[1:]

    # If the number starts with '7', assume it's missing the '254' and add it
    elif phone_number.startswith("7"):
        phone_number = "254" + phone_number

    # If the number starts with '1', assume it's missing the '254' and add it
    elif phone_number.startswith("1"):
        phone_number = "254" + phone_number

    # If the number starts with '254', it's already in the correct format
    elif phone_number.startswith("254"):
        pass
    else:
        # Handle other cases (e.g., invalid numbers)
        raise ValueError("Invalid phone number format")

    return phone_number
