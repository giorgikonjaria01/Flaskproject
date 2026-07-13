- Currency caching verified via flask shell: confirmed a single ExchangeRate 
  row is created on first conversion (GEL→USD), the same row and timestamp 
  are reused on a repeat call within the 1-hour window, and the row is 
  updated (not duplicated) with a fresh timestamp once manually backdated 
  past the cache window.


# Finance Tracker

a web-based finance management app built with Flask. Users can manage budgets, organize transactions by categories and convert currencies.

# Features 

## Authentication
- User registration and login;
- Secure password storage using Werkzeug password hashing;
- Session-based authentication;
- @login-required decorator for protected routes;

# Transaction

- Create income and expense transactions;
- Assign transactions to categories;
- Add descriptions and dates;
- View transaction history;
- Search transactions by description;
- Filter transactions by:
    Category,
    Income/Expense type
- Paginated transaction list (10 items per list);
- Export transactions to CSV;

Transactions use soft deletion:
- Deleted transactions are not physically removed;
- A deleted_at timestamp is stored instead;

# Categories

- Custom category names;
- Income or expense types;
- Custom colors for UI display;
- Categories are linked only to their owner;

# Budget 

- Monthly limit;
- Update to existing budgets;
- Delete budgets;
- Budget Tracking;

When spending reaches 80% or more:
    - A warning will be displayed;

# Statistics

- Monthly income total;
- Monthly expense total;
- Current balance;
- Spending totals by category;

# Currency Conversion

The application uses ExchangeRate-API for currency conversion

# Other

- API key stored in .env
- Exchange rate caching using database storage
- Cached rates are reused for one hour to reduce API requests

# Architecture

The project uses a service-oriented architecture.

Routes handle HTTP requests while services contain application logic.