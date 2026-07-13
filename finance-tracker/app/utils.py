def format_currency(value, currency='GEL'):
    symbols = {'GEL': '₾', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{float(value):,.2f}"