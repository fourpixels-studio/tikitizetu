import stripe
import os

# Set your secret key from Stripe
stripe.api_key = os.environ.get('STRIPE_API_KEY')


def process_payment(card_number, cvc_number, expiry_date, amount):
    try:
        # Convert the expiry date from MM/YY to separate month and year
        exp_month, exp_year = expiry_date.split('/')

        # Create a PaymentMethod with the card details
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_number,
                "exp_month": int(exp_month),
                "exp_year": int(exp_year),
                "cvc": cvc_number,
            },
        )

        # Create a PaymentIntent to charge the card
        intent = stripe.PaymentIntent.create(
            amount=int(amount),  # amount in cents, so convert if necessary
            currency="kes",
            payment_method=payment_method.id,
            confirm=True,  # Confirm the payment immediately
        )

        # Check if the payment was successful
        if intent['status'] == 'succeeded':
            return True
        else:
            return False

    except stripe.error.CardError as e:
        # Handle card error (e.g., insufficient funds, invalid card, etc.)
        print(f"Card Error: {e.user_message}")
        return False

    except stripe.error.StripeError as e:
        # Handle general Stripe errors
        print(f"Stripe Error: {e.user_message}")
        return False

    except Exception as e:
        # Handle any other exceptions
        print(f"Error: {str(e)}")
        return False
