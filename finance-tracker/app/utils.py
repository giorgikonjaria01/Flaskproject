def format_currency(value, currency='GEL'):
    symbols = {'GEL': '₾', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{value:,.2f}"