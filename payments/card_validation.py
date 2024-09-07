def validate_card_number(card_no):
    odd_sum = 0
    even_sum = 0
    double_list = []

    # Strip any spaces or non-numeric characters from the card number
    card_no = card_no.replace(" ", "").replace("-", "")

    number = list(card_no)
    for (idx, val) in enumerate(number):
        if idx % 2 != 0:  # this is an odd number
            odd_sum += int(val)
        else:  # this is an even number
            double_list.append(int(val) * 2)

    # converting the list into a string
    double_string = ""
    for x in double_list:
        double_string += str(x)

    # converting the string back to a list
    double_list = list(double_string)

    for x in double_list:
        even_sum += int(x)

    net_sum = odd_sum + even_sum
    if net_sum % 10 == 0:
        print("Valid Card")
        return True
    else:
        print("Invalid Card")
        return False
