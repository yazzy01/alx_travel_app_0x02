# ALX Travel App

A Django-based travel application for managing travel listings, bookings, and user profiles with integrated payment processing using Chapa API.

## Features
- User authentication
- Travel listings
- Booking management
- User profiles
- Search functionality
- Secure payment processing with Chapa API

## Payment Integration with Chapa API

The application integrates with the Chapa payment gateway to provide a secure and reliable payment solution for bookings. Here's how it works:

1. **Booking Creation**: When a user creates a booking, the system calculates the total price based on the listing price and duration.

2. **Payment Initiation**: The application initiates a payment request to Chapa API with booking details and generates a unique transaction reference.

3. **Payment Processing**: Users are redirected to Chapa's secure payment page where they can complete the payment using various methods.

4. **Payment Verification**: After payment, the application verifies the payment status with Chapa API and updates the booking status accordingly.

5. **Confirmation**: On successful payment, a confirmation email is sent to the user with booking details.

### Technical Implementation

- **Payment Model**: Stores payment information including transaction ID, amount, and status.
- **API Integration**: Uses Chapa's REST API for payment initiation and verification.
- **Security**: API keys are stored as environment variables for security.
- **Error Handling**: Gracefully handles payment failures and exceptions.

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   ```
   CHAPA_SECRET_KEY=your_chapa_secret_key
   ```
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`

## Environment Variables
- `CHAPA_SECRET_KEY`: Your Chapa API secret key
- `DEFAULT_FROM_EMAIL`: Email address for sending notifications

## License
This project is licensed under the MIT License. 