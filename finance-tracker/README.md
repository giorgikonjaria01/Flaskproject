- Currency caching verified via flask shell: confirmed a single ExchangeRate 
  row is created on first conversion (GEL→USD), the same row and timestamp 
  are reused on a repeat call within the 1-hour window, and the row is 
  updated (not duplicated) with a fresh timestamp once manually backdated 
  past the cache window.