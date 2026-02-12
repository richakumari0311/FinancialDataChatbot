import pandas as pd
import re
from typing import Optional


class FinancialDataChatbot:
    """
    A chatbot that answers questions based on holdings and trades CSV data.
    Only responds with information from the provided CSV files.
    Returns "Sorry can not find the answer" for queries outside the data scope.
    """
    
    def __init__(self, holdings_path: str, trades_path: str):
        """
        Initialize the chatbot with CSV files.
        
        Args:
            holdings_path: Path to holdings.csv file
            trades_path: Path to trades.csv file
        """
        self.holdings_df = None
        self.trades_df = None
        self.load_data(holdings_path, trades_path)
    
    def load_data(self, holdings_path: str, trades_path: str):
        """
        Load CSV files into pandas DataFrames.
        
        Args:
            holdings_path: Path to holdings.csv
            trades_path: Path to trades.csv
        """
        try:
            self.holdings_df = pd.read_csv(holdings_path)
            self.trades_df = pd.read_csv(trades_path)
            
            # Convert date columns to datetime with error handling
            date_columns_holdings = ['AsOfDate', 'OpenDate', 'CloseDate']
            date_columns_trades = ['TradeDate', 'SettleDate']
            
            for col in date_columns_holdings:
                if col in self.holdings_df.columns:
                    self.holdings_df[col] = pd.to_datetime(
                        self.holdings_df[col], 
                        errors='coerce'
                    )
            
            for col in date_columns_trades:
                if col in self.trades_df.columns:
                    self.trades_df[col] = pd.to_datetime(
                        self.trades_df[col], 
                        errors='coerce'
                    )
            
            print("Data loaded successfully")
            print(f"Holdings records: {len(self.holdings_df)}")
            print(f"Trades records: {len(self.trades_df)}")
            
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            raise
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def get_total_holdings(self, fund_name: Optional[str] = None) -> Optional[int]:
        """
        Get total number of holdings, optionally filtered by fund name.
        
        Args:
            fund_name: Optional fund name to filter by
            
        Returns:
            Count of holdings or None if fund not found
        """
        if fund_name:
            holdings = self.holdings_df[
                self.holdings_df['PortfolioName'].str.contains(
                    fund_name, 
                    case=False, 
                    na=False
                )
            ]
            if holdings.empty:
                return None
            return len(holdings)
        return len(self.holdings_df)
    
    def get_total_trades(self, fund_name: Optional[str] = None) -> Optional[int]:
        """
        Get total number of trades, optionally filtered by fund name.
        
        Args:
            fund_name: Optional fund name to filter by
            
        Returns:
            Count of trades or None if fund not found
        """
        if fund_name:
            trades = self.trades_df[
                self.trades_df['PortfolioName'].str.contains(
                    fund_name, 
                    case=False, 
                    na=False
                )
            ]
            if trades.empty:
                return None
            return len(trades)
        return len(self.trades_df)
    
    def get_best_performing_funds(self) -> Optional[pd.Series]:
        """
        Get funds ranked by yearly P&L performance.
        
        Returns:
            Series with fund names as index and PL_YTD as values, 
            sorted descending by performance, or None if data unavailable
        """
        required_columns = ['PL_YTD', 'PortfolioName']
        
        if not all(col in self.holdings_df.columns for col in required_columns):
            return None
        
        try:
            performance = self.holdings_df.groupby('PortfolioName')['PL_YTD'].sum()
            performance = performance.sort_values(ascending=False)
            return performance
        except Exception:
            return None
    
    def answer_question(self, question: str) -> str:
        """
        Main method to answer questions about the financial data.
        
        Args:
            question: Natural language question from user
            
        Returns:
            Answer string or "Sorry can not find the answer"
        """
        question_lower = question.lower()
        fund_name = self._extract_fund_name(question)
        
        # Check for holdings count questions
        if self._is_holdings_query(question_lower):
            # If question has 'for' but no valid fund found, it's invalid
            if 'for' in question_lower and fund_name is None:
                return "Sorry can not find the answer"
            
            count = self.get_total_holdings(fund_name)
            if count is None and fund_name:
                return "Sorry can not find the answer"
            if fund_name:
                return f"Total holdings for '{fund_name}': {count}"
            return f"Total holdings: {count}"
        
        # Check for trades count questions
        if self._is_trades_query(question_lower):
            # If question has 'for' but no valid fund found, it's invalid
            if 'for' in question_lower and fund_name is None:
                return "Sorry can not find the answer"
            
            count = self.get_total_trades(fund_name)
            if count is None and fund_name:
                return "Sorry can not find the answer"
            if fund_name:
                return f"Total trades for '{fund_name}': {count}"
            return f"Total trades: {count}"
        
        # Check for performance comparison questions
        if self._is_performance_query(question_lower):
            performance = self.get_best_performing_funds()
            if performance is None:
                return "Sorry can not find the answer"
            
            return self._format_performance_response(performance)
        
        return "Sorry can not find the answer"
    
    def _is_holdings_query(self, question_lower: str) -> bool:
        """Check if question is about holdings count."""
        count_keywords = ['total', 'number', 'how many', 'count']
        
        # Match if: "holdings" + count keyword, OR "holdings for" pattern
        return ('holdings' in question_lower and 
                (any(keyword in question_lower for keyword in count_keywords) or
                 'for' in question_lower))
    
    def _is_trades_query(self, question_lower: str) -> bool:
        """Check if question is about trades count."""
        count_keywords = ['total', 'number', 'how many', 'count']
        
        # Match if: "trade/trades" + count keyword, OR "trade/trades for" pattern
        return ('trade' in question_lower and 
                (any(keyword in question_lower for keyword in count_keywords) or
                 'for' in question_lower))
    
    def _is_performance_query(self, question_lower: str) -> bool:
        """Check if question is about fund performance."""
        performance_keywords = [
            'perform', 'better', 'best', 'worst', 
            'profit', 'loss', 'p&l', 'pl'
        ]
        return any(keyword in question_lower for keyword in performance_keywords)
    
    def _format_performance_response(self, performance: pd.Series) -> str:
        """
        Format performance data into readable response.
        
        Args:
            performance: Series with fund performance data
            
        Returns:
            Formatted string with performance rankings
        """
        result = "Fund Performance (Year-to-Date P&L):\n"
        result += "=" * 50 + "\n"
        
        for fund, pl in performance.items():
            result += f"{fund}: ${pl:,.2f}\n"
        
        result += "=" * 50 + "\n"
        result += f"Best performing: {performance.idxmax()} "
        result += f"(${performance.max():,.2f})\n"
        result += f"Worst performing: {performance.idxmin()} "
        result += f"(${performance.min():,.2f})"
        
        return result
    
    def _extract_fund_name(self, question: str) -> Optional[str]:
        """
        Extract fund name from question by matching against actual fund names.
        
        Args:
            question: User's question string
            
        Returns:
            Fund name if found, None otherwise
        """
        question_lower = question.lower()
        
        # Check holdings data for matching fund names
        if self.holdings_df is not None and 'PortfolioName' in self.holdings_df.columns:
            for fund in self.holdings_df['PortfolioName'].dropna().unique():
                if str(fund).lower() in question_lower:
                    return str(fund)
        
        # Check trades data for matching fund names
        if self.trades_df is not None and 'PortfolioName' in self.trades_df.columns:
            for fund in self.trades_df['PortfolioName'].dropna().unique():
                if str(fund).lower() in question_lower:
                    return str(fund)
        
        # Try pattern matching for "for [fund name]"
        match = re.search(
            r'for\s+["\']?([^"\'?.]+?)["\']?(?:\?|$|,)', 
            question, 
            re.IGNORECASE
        )
        
        if match:
            potential_fund = match.group(1).strip()
            potential_fund_lower = potential_fund.lower()
            
            # Check if extracted phrase matches any actual fund (case-insensitive)
            if self.holdings_df is not None and 'PortfolioName' in self.holdings_df.columns:
                for fund in self.holdings_df['PortfolioName'].dropna().unique():
                    if potential_fund_lower == str(fund).lower():
                        return str(fund)
            
            if self.trades_df is not None and 'PortfolioName' in self.trades_df.columns:
                for fund in self.trades_df['PortfolioName'].dropna().unique():
                    if potential_fund_lower == str(fund).lower():
                        return str(fund)
        
        return None


def main():
    """Main function to run the chatbot in interactive mode."""
    print("=" * 60)
    print("Financial Data Chatbot")
    print("=" * 60)
    print("\nInitializing chatbot...")
    
    try:
        # Use CSV files from current working directory
        chatbot = FinancialDataChatbot('holdings.csv', 'trades.csv')
    except Exception as e:
        print(f"\nError: Could not initialize chatbot - {e}")
        print("Please ensure holdings.csv and trades.csv are in the current directory.")
        return
    
    print("\nExample Questions:")
    print("- What is the total number of holdings?")
    print("- How many trades are there?")
    print("- Which funds performed better?")
    print("- Total holdings for [fund name]")
    print("- How many trades for [fund name]?")
    print("\nType 'quit' to exit")
    print("=" * 60)
    
    while True:
        try:
            user_question = input("\nYour question: ")
            
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_question.strip():
                print("Please enter a question.")
                continue
            
            answer = chatbot.answer_question(user_question)
            print(f"\nAnswer: {answer}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError processing question: {e}")


if __name__ == "__main__":
    main()