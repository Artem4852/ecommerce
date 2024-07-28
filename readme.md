# Ecommerce website

## Overview

This is a web application built using the Flask framework. It allows users to browse, purchase, and interact with products (shoes) for kids. The website features user authentication, product listings, email notifications, and integration with external APIs.

## Important Acknowledgement

Please take into consideration this project is a WIP so many things might not work correctly.

## Features

- **User Authentication**: Secure login and session management (hashing of passwords on client side).
- **Product Listings**: Displaying and managing a variety of products.
- **Favorites**: Adding products to favorites.
- **Email Notifications**: Sending emails using predefined templates.
- **Integration**: Integration with external services such as MongoDB, Nova Post API, Telegram, and Instagram.
- **Statistics Logging**: Logging site statistics for analysis.

## Setup

### Prerequisites

- Python 3.8 or higher
- Flask and required packages (see `requirements.txt`)

### Installation

1. **Clone the repository**:

   ```
   git clone https://github.com/Artem4852/ecommerce
   cd ecommerce
   ```

2. **Install dependencies**:

   ```
   pip3 install -r requirements.txt
   ```

3. **Setup environment variables**:
   Create a `.env` file in the root directory and add the following environment variables:

   ```
    MONGO_URI="mongo db uri"
    SECRET_KEY="flask secret key"
    NOVA_API_KEY="api key for nova post"
    TELEGRAM_TOKEN="telegram bot api token"
    ROCKET_TOKENS="tokens for rocket api - token1,token2,token3"
   ```

4. **Run the application**:
   ```
   python3 app.py
   ```

### Usage

- **Home Page**: Access the home page at `http://localhost:8080/`.
- **User Authentication**: Use the login functionality to access user-specific features.
- **Email Sending**: Emails are automatically sent for specific triggers (e.g., forgot password).
- **APIs**: The application integrates with external APIs for additional features.

### Important Endpoints

- **Home**: `/` - Displays the homepage with essential sections like hero, featured, and newsletter.
- **Shop**: `/shop` - Shop (catalogue) page.
- **Product Details**: `/product/<id>` - Detailed view of a specific product.
- **FAQ**: `/faq` - FAQ page with information about how to measure foot size correctly, shiping information, as well as replacements and returns information.
- **Contact**: `/contact` - Contact page with ability tto write to owners of the website.
- **Cart** and **Checkout**: `/cart` and `/checkout` - Cart and checkout pages.
- **Orders**: `/orders` - Displays orders page with list of user's orders.
- **User Login**: `/login` - User login page.

## License

This project is open source and available under the MIT License.
