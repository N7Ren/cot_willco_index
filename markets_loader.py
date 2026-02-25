"""
Market data loader and validator module.

This module handles loading and validating market data from CSV files,
providing clean separation of concerns from the main application logic.
"""

import os
import pandas as pd


# Constants for market data validation
REQUIRED_MARKET_COLUMNS = {'contract_code', 'contract_name'}


class MarketsLoadError(Exception):
    """Custom exception for market loading errors."""
    pass


def validate_markets_dataframe(df, source="markets.csv"):
    """
    Validate markets DataFrame for required columns and data integrity.
    
    Args:
        df (pd.DataFrame): DataFrame to validate.
        source (str): Source description for error messages.
        
    Raises:
        ValueError: If validation fails.
    """
    # Check for required columns
    missing_cols = REQUIRED_MARKET_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"{source} is missing required columns: {', '.join(sorted(missing_cols))}"
        )
    
    # Check for empty/null values in required columns
    for col in REQUIRED_MARKET_COLUMNS:
        if df[col].isna().any():
            null_count = df[col].isna().sum()
            raise ValueError(
                f"{source} contains {null_count} empty value(s) in '{col}' column"
            )
        
        # Check for empty strings after stripping whitespace
        if (df[col].astype(str).str.strip() == '').any():
            empty_count = (df[col].astype(str).str.strip() == '').sum()
            raise ValueError(
                f"{source} contains {empty_count} blank value(s) in '{col}' column"
            )
    
    # Check for duplicate contract codes
    duplicates = df['contract_code'].duplicated()
    if duplicates.any():
        dup_codes = df.loc[duplicates, 'contract_code'].unique()
        raise ValueError(
            f"{source} contains duplicate contract codes: {', '.join(map(str, dup_codes))}"
        )


def load_markets(csv_path=None):
    """
    Load markets from CSV file.
    
    Attempts to load market data from markets.csv. If the file is not found
    or contains invalid data, raises a MarketsLoadError with a descriptive message.
    
    Args:
        csv_path (str, optional): Path to markets CSV file. If None, uses default
                                  location (markets.csv in the same directory as this module).
    
    Returns:
        pd.DataFrame: DataFrame with columns 'contract_code' and 'contract_name'.
        
    Raises:
        MarketsLoadError: If markets.csv cannot be loaded or contains invalid data.
    """
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "markets.csv")
    
    try:
        # Load from CSV file with dtype specification for consistency
        markets_df = pd.read_csv(
            csv_path,
            dtype=str,  # Read all columns as strings to preserve leading zeros
            skipinitialspace=True  # Strip leading whitespace from values
        )
        
        # Strip whitespace from column names and values
        markets_df.columns = markets_df.columns.str.strip()
        for col in markets_df.columns:
            if markets_df[col].dtype == 'object':
                markets_df[col] = markets_df[col].str.strip()
        
        # Validate the loaded data
        validate_markets_dataframe(markets_df, source=csv_path)
        
        return markets_df
        
    except FileNotFoundError as e:
        error_msg = (
            f"markets.csv not found at {csv_path}. "
            f"Please create the file with 'contract_code' and 'contract_name' columns."
        )
        raise MarketsLoadError(error_msg) from e
    
    except (ValueError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        error_msg = f"Error loading markets.csv: {str(e)}"
        raise MarketsLoadError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Unexpected error loading markets.csv: {type(e).__name__}: {str(e)}"
        raise MarketsLoadError(error_msg) from e


def load_markets_safe(csv_path=None):
    """
    Load markets from CSV file with safe error handling.
    
    This function wraps load_markets() and returns both the DataFrame and any error message.
    If loading fails, returns an empty DataFrame and the error message.
    
    Args:
        csv_path (str, optional): Path to markets CSV file.
    
    Returns:
        tuple: (pd.DataFrame, str or None) - DataFrame and error message (None if successful)
    """
    try:
        markets_df = load_markets(csv_path)
        return markets_df, None
    except MarketsLoadError as e:
        # Return empty DataFrame and error message
        empty_df = pd.DataFrame(columns=['contract_code', 'contract_name'])
        return empty_df, str(e)
