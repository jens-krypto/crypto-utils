# KMOON Ecosystem Analytics Calculator

A noble instrument for calculating Market Cap and Total Value Locked (TVL) across the KMOON ecosystem.

## 🌕 Overview

This calculator tracks metrics for the following KMOON ecosystem tokens:
- KMOON (Solana)
- IYKYK (Solana)
- AA (Ethereum)
- RB (Ethereum)
- IYKYK (TRON)

## 🏰 Installation

First, establish thy development sanctuary:

```bash
# Create a virtual environment
python -m venv venv

# Activate the sacred circle
source venv/bin/activate  # On Unix or MacOS
# OR
.\venv\Scripts\activate  # On Windows

# Install the required enchantments
pip install -r requirements.txt
```

## 🗝️ Usage

The calculator can be used in several ways:

### 1. As a Standalone Script

Simply run the script directly:

```bash
python kmoon_ecosystem_calculator.py
```

This will:
- Calculate Market Cap and TVL for all tokens
- Print results to console
- Save results to `kmoon_ecosystem_metrics.json`

### 2. As an Imported Module

Import and use in your Python code:

```python
# Basic usage
from kmoon_ecosystem_calculator import get_kmoon_ecosystem_metrics

# Get metrics data
metrics = get_kmoon_ecosystem_metrics()

# Use the data
print(f"Total Market Cap: ${metrics['totals']['total_market_cap']:,.2f}")
print(f"Total TVL: ${metrics['totals']['total_tvl']:,.2f}")
for address, data in metrics['tokens'].items():
    print(f"{data['ticker']}: MC=${data['market_cap']:,.2f}, TVL=${data['tvl']:,.2f}")
```

### 3. In a FastAPI Application

Create a simple API endpoint:

```python
from fastapi import FastAPI
from kmoon_ecosystem_calculator import get_kmoon_ecosystem_metrics

app = FastAPI()

@app.get("/api/metrics")
async def get_metrics():
    return get_kmoon_ecosystem_metrics()
```

### 4. With Custom Caching

Example with simple caching:

```python
from functools import lru_cache
from kmoon_ecosystem_calculator import get_kmoon_ecosystem_metrics

# Cache results for 5 minutes
@lru_cache(maxsize=1, ttl=300)
def get_cached_metrics():
    return get_kmoon_ecosystem_metrics()
```

### 5. In a Schedule/Cron Job

Example using schedule library:

```python
import schedule
import time
from kmoon_ecosystem_calculator import get_kmoon_ecosystem_metrics

def job():
    metrics = get_kmoon_ecosystem_metrics()
    # Do something with the data...

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 📜 Output Format

The calculator returns a dictionary with the following structure:

```json
{
  "tokens": {
    "5tzkqRo8XjHefzuJumij7suA6N7nTZA1FSLtzM8Bpump": {
      "ticker": "IYKYK",
      "market_cap": 582367.89,
      "tvl": 102594.44
    },
    "HQ2KXz4rJf1b18sHiGgvsCUe8hgEH21jqf2gys5jpump": {
      "ticker": "KMOON",
      "market_cap": 111284.93,
      "tvl": 42234.88
    }
  },
  "totals": {
    "total_market_cap": 789123.45,
    "total_tvl": 161371.41
  }
}
```

## ⚛️ Data Sources

- Solana: 
  * Price: Jupiter API
  * Supply: Solana RPC
  * Liquidity: DexScreener API
- Ethereum: 
  * All metrics from Uniswap V2 pools
  * ETH price from Chainlink oracle
- TRON: 
  * All metrics from TRONSCAN API

## 🛡️ Best Practices

1. **Rate Limiting**: The calculator makes multiple API calls. Consider implementing rate limiting if using frequently.

2. **Caching**: For high-traffic applications, implement caching to avoid excessive blockchain queries.

3. **Error Handling**: Always check for error responses in the returned data:
```python
metrics = get_kmoon_ecosystem_metrics()
if "error" in metrics:
    print(f"Error: {metrics['error']}")
```

4. **Network Timeouts**: Default timeouts are set for network requests. Adjust if needed in your environment.

## ⚔️ Error Handling

The calculator handles various error conditions:
- Network connectivity issues
- Invalid responses from blockchain nodes
- Contract interaction failures
- Price feed issues

All errors are logged with appropriate context.

## 📖 License

MIT - Free as KMOON in the crypto sky

## 🤝 Contributing

Feel free to contribute to this noble cause:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request