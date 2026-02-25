# Markets Configuration Guide

## Overview

The application uses a `markets.csv` file to define which futures markets are available for analysis. This file can be easily edited by end users without modifying any code.

## File Location

The markets configuration file is located at:
```
markets.csv
```

## File Format

The CSV file has two columns:
- **contract_code**: The unique identifier for the futures contract (e.g., "098662", "13874A")
- **contract_name**: The human-readable name of the market (e.g., "USD INDEX", "E-MINI S&P 500")

### Example Format

```csv
contract_code,contract_name
098662,USD INDEX
042601,UST 2Y NOTE
133741,BITCOIN
```

## How to Add a New Market

1. Open `markets.csv` in any text editor or spreadsheet application (Excel, Google Sheets, etc.)
2. Add a new row with the contract code and name:
   ```csv
   123456,NEW MARKET NAME
   ```
3. Save the file
4. Restart the application for changes to take effect

## How to Remove a Market

1. Open `markets.csv`
2. Delete the entire row for the market you want to remove
3. Save the file
4. Restart the application

## How to Edit a Market Name

1. Open `markets.csv`
2. Find the row with the market you want to edit
3. Change the `contract_name` value (keep the `contract_code` unchanged)
4. Save the file
5. Restart the application

## Important Notes

- **Do not modify the header row** (`contract_code,contract_name`)
- **Do not leave empty rows** in the middle of the file
- **Contract codes must be unique** - no duplicates allowed
- **Both columns are required** for each market
- The file must be saved as CSV format (not Excel .xlsx)

## Editing in Different Applications

### Text Editor (Notepad, VS Code, etc.)
- Simply edit the file and save
- Make sure to maintain the comma-separated format

### Excel or Google Sheets
1. Open the CSV file
2. Edit the cells as needed
3. **Important**: Save as CSV format, not Excel format
   - In Excel: File → Save As → Choose "CSV (Comma delimited)"
   - In Google Sheets: File → Download → Comma Separated Values (.csv)

## Troubleshooting

If the application fails to load markets after editing:

1. **Check for syntax errors**: Ensure each line has exactly two values separated by a comma
2. **Check for empty values**: Make sure no cells are empty
3. **Check the header**: The first line must be exactly `contract_code,contract_name`
4. **Check file encoding**: Save the file as UTF-8 encoding

If the CSV file is missing or invalid, the application will automatically fall back to the default list of 35 markets and display a warning message in the console.

## Current Markets

The default configuration includes 35 markets across these categories:
- **Indices & Bonds** (5): USD INDEX, Treasury notes/bonds
- **Currencies** (12): Major forex pairs
- **Commodities** (11): Precious metals, energy, agriculture
- **Equity Indices** (5): DJIA, NASDAQ, S&P 500, etc.
- **Cryptocurrencies** (2): BITCOIN, ETHER

## Need Help?

If you encounter issues editing the markets file, check the application console output for error messages that can help diagnose the problem.
