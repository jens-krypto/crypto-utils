# KMOON Ecosystem TVL Calculator

A noble instrument for calculating Total Value Locked (TVL) across the KMOON ecosystem.

## 🌕 Overview

This calculator tracks TVL for the following KMOON ecosystem tokens:
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
python kmoon_ecosystem_tvl_calculator.py
```

This will:
- Calculate TVL for all tokens
- Print results to console
- Save results to `kmoon_ecosystem_tvl.json`

### 2. As an Imported Module

Import and use in your Python code:

```python
# Basic usage
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl

# Get TVL data
tvl_data = get_kmoon_ecosystem_tvl()

# Use the data
print(f"Total Ecosystem TVL: ${tvl_data['total_tvl']:,.2f}")
for address, tvl in tvl_data['tokens'].items():
    print(f"Token {address}: ${tvl:,.2f}")
```

### 3. In a FastAPI Application

Create a simple API endpoint:

```python
from fastapi import FastAPI
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl

app = FastAPI()

@app.get("/api/tvl")
async def get_tvl():
    return get_kmoon_ecosystem_tvl()
```

### 4. With Custom Caching

Example with simple caching:

```python
from functools import lru_cache
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl

# Cache results for 5 minutes
@lru_cache(maxsize=1, ttl=300)
def get_cached_tvl():
    return get_kmoon_ecosystem_tvl()
```

### 5. In a Schedule/Cron Job

Example using schedule library:

```python
import schedule
import time
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl

def job():
    tvl_data = get_kmoon_ecosystem_tvl()
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
    "5tzkqRo8XjHefzuJumij7suA6N7nTZA1FSLtzM8Bpump": 1234.56,    // IYKYK (SOL)
    "HQ2KXz4rJf1b18sHiGgvsCUe8hgEH21jqf2gys5jpump": 789.10,     // KMOON (SOL)
    "0x5c050f01db04c98206eb55a6ca4dc3287c69abff": 4567.89,      // AA (ETH)
    "0x9756f5cd1cb7c0dbb6893973c2f0cec59c671c05": 9876.54,      // RB (ETH)
    "TLxGAoiRk3oCr4yFPKHPrVAd7ZknhFcMWo": 62210.07             // IYKYK (TRON)
  },
  "total_tvl": 78678.16
}
```

## ⚛️ Supported Networks

- Solana (via Jupiter API)
- Ethereum (via Uniswap V2)
- TRON (via TRONSCAN API)

## 🛡️ Best Practices

1. **Rate Limiting**: The calculator makes multiple API calls. Consider implementing rate limiting if using frequently.

2. **Caching**: For high-traffic applications, implement caching to avoid excessive blockchain queries.

3. **Error Handling**: Always check for error responses in the returned data:
```python
tvl_data = get_kmoon_ecosystem_tvl()
if "error" in tvl_data:
    print(f"Error: {tvl_data['error']}")
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

# Practical Examples

## 🎯 Example 1: Discord Bot
```python
import discord
from discord.ext import commands, tasks
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl
from datetime import datetime

bot = commands.Bot(command_prefix='!')

@bot.command(name='tvl')
async def tvl(ctx):
    """Get current TVL for KMOON ecosystem"""
    tvl_data = get_kmoon_ecosystem_tvl()
    
    # Create embed message
    embed = discord.Embed(
        title="KMOON Ecosystem TVL",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Add TVL for each token
    for address, value in tvl_data['tokens'].items():
        embed.add_field(
            name=f"Token: {address[:6]}...{address[-4:]}", 
            value=f"${value:,.2f}",
            inline=False
        )
    
    # Add total TVL
    embed.add_field(
        name="Total TVL", 
        value=f"${tvl_data['total_tvl']:,.2f}", 
        inline=False
    )
    
    await ctx.send(embed=embed)

bot.run('YOUR_DISCORD_TOKEN')
```

## 🎯 Example 2: Telegram Alert System
```python
import telebot
from datetime import datetime
import schedule
import time
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl

bot = telebot.TeleBot('YOUR_TELEGRAM_TOKEN')
CHAT_ID = 'YOUR_CHAT_ID'

last_tvl = 0

def check_tvl_changes():
    global last_tvl
    tvl_data = get_kmoon_ecosystem_tvl()
    current_tvl = tvl_data['total_tvl']
    
    # Calculate change percentage
    if last_tvl > 0:
        change_pct = ((current_tvl - last_tvl) / last_tvl) * 100
        
        # Alert if change is more than 5%
        if abs(change_pct) > 5:
            message = f"""
🚨 *TVL Change Alert*
Change: {change_pct:.2f}%
Previous TVL: ${last_tvl:,.2f}
Current TVL: ${current_tvl:,.2f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            bot.send_message(CHAT_ID, message, parse_mode='Markdown')
    
    last_tvl = current_tvl

# Check every 30 minutes
schedule.every(30).minutes.do(check_tvl_changes)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 🎯 Example 3: Simple Web Dashboard
```python
from flask import Flask, render_template_string
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>KMOON Ecosystem TVL Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: auto; }
        .card { 
            border: 1px solid #ddd; 
            padding: 20px; 
            margin: 10px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>KMOON Ecosystem TVL</h1>
        <div class="card">
            <h2>Total TVL: ${{ "{:,.2f}".format(data.total_tvl) }}</h2>
            <canvas id="tvlChart"></canvas>
        </div>
        <div class="card">
            <h2>Individual Token TVL</h2>
            {% for address, tvl in data.tokens.items() %}
            <p>{{ address }}: ${{ "{:,.2f}".format(tvl) }}</p>
            {% endfor %}
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('tvlChart');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: {{ labels|tojson }},
                datasets: [{
                    data: {{ values|tojson }},
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    tvl_data = get_kmoon_ecosystem_tvl()
    
    labels = list(tvl_data['tokens'].keys())
    values = list(tvl_data['tokens'].values())
    
    return render_template_string(
        HTML_TEMPLATE, 
        data=tvl_data,
        labels=labels,
        values=values
    )

if __name__ == '__main__':
    app.run(debug=True)
```

## 🎯 Example 4: API with Caching and Rate Limiting
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl
from datetime import datetime, timedelta
import asyncio
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple cache implementation
cache = {
    'data': None,
    'last_updated': None
}

# Rate limiting
requests_log = []
RATE_LIMIT = 10  # requests
RATE_WINDOW = 60  # seconds

async def update_cache():
    """Update cache every 5 minutes"""
    while True:
        try:
            cache['data'] = get_kmoon_ecosystem_tvl()
            cache['last_updated'] = datetime.now()
        except Exception as e:
            print(f"Cache update failed: {e}")
        await asyncio.sleep(300)  # 5 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_cache())

def check_rate_limit(request):
    """Check if request is within rate limits"""
    now = time.time()
    # Clean old requests
    global requests_log
    requests_log = [t for t in requests_log if t > now - RATE_WINDOW]
    
    if len(requests_log) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    requests_log.append(now)

@app.get("/api/tvl")
async def get_tvl():
    # Check rate limit
    check_rate_limit(None)
    
    # Return cached data if available and fresh
    if cache['data'] and cache['last_updated']:
        age = (datetime.now() - cache['last_updated']).total_seconds()
        return {
            "data": cache['data'],
            "cache_age_seconds": age,
            "cached": True
        }
    
    # If no cache, get fresh data
    try:
        data = get_kmoon_ecosystem_tvl()
        return {
            "data": data,
            "cached": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "cache": bool(cache['data']),
        "last_update": cache['last_updated'].isoformat() if cache['last_updated'] else None
    }
```

## 🎯 Example 5: Data Analysis Script
```python
import pandas as pd
import matplotlib.pyplot as plt
from kmoon_ecosystem_tvl_calculator import get_kmoon_ecosystem_tvl
from datetime import datetime
import json
from pathlib import Path

def analyze_tvl():
    # Get current TVL data
    current_data = get_kmoon_ecosystem_tvl()
    
    # Load historical data if exists
    history_file = Path('tvl_history.json')
    if history_file.exists():
        with history_file.open('r') as f:
            history = json.load(f)
    else:
        history = []
    
    # Add current data to history
    current_data['timestamp'] = datetime.now().isoformat()
    history.append(current_data)
    
    # Save updated history
    with history_file.open('w') as f:
        json.dump(history, f, indent=2)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Create visualization
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['total_tvl'], marker='o')
    plt.title('KMOON Ecosystem TVL Over Time')
    plt.xlabel('Date')
    plt.ylabel('TVL (USD)')
    plt.grid(True)
    plt.xticks(rotation=45)
    
    # Save plot
    plt.savefig('tvl_trend.png', bbox_inches='tight')
    
    # Calculate statistics
    stats = {
        'current_tvl': current_data['total_tvl'],
        'max_tvl': df['total_tvl'].max(),
        'min_tvl': df['total_tvl'].min(),
        'avg_tvl': df['total_tvl'].mean(),
        'std_tvl': df['total_tvl'].std()
    }
    
    return stats

if __name__ == '__main__':
    stats = analyze_tvl()
    print("\nKMOON Ecosystem TVL Statistics:")
    for key, value in stats.items():
        print(f"{key}: ${value:,.2f}")
```