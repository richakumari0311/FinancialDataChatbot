# Financial Data Chatbot

A natural language chatbot for querying financial portfolio data - ask questions about holdings, trades, and fund performance in plain English, with no database or internet connection required.

## What It Does

- Answers natural language questions about holdings and trades data from CSV files
- Compares fund performance by yearly P&L
- Supports fund-specific queries with case-insensitive matching
- Returns a clear error message for out-of-scope queries
- Runs entirely locally — no API keys, no cloud, no cost

## Tech Stack

| Component | Tool |
|---|---|
| Language | Python 3.7+ |
| Data Processing | Pandas |
| Interface | Command-line |

## Setup

**1. Clone the repo**
```
git clone https://github.com/richakumari0311/FinancialDataChatbot.git
cd FinancialDataChatbot
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Add your data**

Place your CSV files in the project folder:
- `holdings.csv` - portfolio holdings data
- `trades.csv` - trade history data

**4. Run**
```
python chatbot.py
```

## Example Queries

```
What is the total number of holdings?
How many trades are there?
Total holdings for FundName
Which funds performed better?
Show me fund performance
```

## Project Structure

```
FinancialDataChatbot/
├── chatbot.py          # Main application (~325 lines)
├── test.py             # Unit tests (18 tests)
├── requirements.txt    # Dependencies
├── holdings.csv        # Sample holdings data
└── trades.csv          # Sample trades data
```

## Key Details

- Tested with 1000+ holdings and 600+ trades records
- 18 unit tests covering core query types and edge cases
- All data processing is local, no external API calls
