# AutoShowroom Kenya 🚗

A professional car marketplace web application built with Python (Flask).

## Features
- 🏠 Beautiful homepage with hero, featured cars, stats
- 🔍 Browse & filter cars by brand, price, fuel, transmission, body type
- 🚗 Detailed car listing page with photo gallery
- 📱 WhatsApp contact button for sellers
- 👤 User accounts (register / login)
- 📋 Post car listings with up to 6 photos
- ❤️ Save favourite cars
- 📊 Seller dashboard with stats
- ✅ Mark cars as sold
- 📱 Mobile responsive

## Setup

### 1. Install Python 3.9+
Download from https://python.org

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
Go to: http://localhost:5000

## Demo Account
- Email: demo@autoshowroom.co.ke
- Password: demo1234

## Project Structure
```
autoShowroom/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── showroom.db            # SQLite database (auto-created)
├── static/
│   └── uploads/           # Car photos
└── templates/
    ├── base.html           # Base layout
    ├── index.html          # Homepage
    ├── shop.html           # Browse cars
    ├── car_detail.html     # Single car page
    ├── post_car.html       # List a car form
    ├── dashboard.html      # Seller dashboard
    ├── login.html          # Login page
    ├── register.html       # Register page
    └── _car_card.html      # Car card component
```

## Customization
- Change site name: search "AutoShowroom" in templates
- Change colors: edit CSS variables in `base.html` `:root`
- Add new car brands: edit the `<select>` in `post_car.html`
- Change currency: edit `format_price` filter in `app.py`
