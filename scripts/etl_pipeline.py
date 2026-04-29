# Import the pandas library which helps us work with data like tables (dataframes)
import pandas as pd
# Import numpy for math and missing values
import numpy as np
# Import os to work with file paths
import os

def run_etl(input_path, output_path):
    print("Starting the ETL (Extract, Transform, Load) Pipeline!")
    print(f"1. Extract: Reading data from {input_path}")
    
    # Load the CSV file into a pandas DataFrame (like a spreadsheet)
    df = pd.read_csv(input_path)
    print("Data loaded successfully! Here are the first 5 rows:")
    print(df.head())
    
    print("\n2. Transform: Cleaning the data and adding new columns (KPIs)")
    
    # Clean the column names so they are easier to work with
    # Example: 'Total Fare USD' becomes 'total_fare_usd'
    df.columns = df.columns.str.strip()  # remove spaces at beginning/end
    df.columns = df.columns.str.lower()  # make all letters lowercase
    df.columns = df.columns.str.replace(' ', '_') # replace spaces with underscores
    print("Column names have been cleaned.")
    
    # Drop columns that we don't need for our analysis to keep the data clean
    columns_to_drop = ['brent_crude_usd_barrel', 'jet_fuel_usd_barrel_surcharge_policy']
    for col in columns_to_drop:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"Dropped column: {col}")
            
    # Replace infinity values with NaN (Not a Number) so they don't break our math later
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # If a flight has no surcharge band listed, we fill it with 'No Surcharge'
    if 'surcharge_band' in df.columns: 
        df['surcharge_band'] = df['surcharge_band'].fillna('No Surcharge')
        print("Filled missing surcharge bands with 'No Surcharge'.")
        
    print("\nAdding New Key Performance Indicators (KPIs):")
    # KPI 1: Price Pass-Through 
    # This helps us see how the fuel price affects the ticket fare
    if 'total_fare_usd' in df.columns and 'jet_fuel_usd_barrel' in df.columns:
        df['price_pass_through'] = df['total_fare_usd'] / df['jet_fuel_usd_barrel']
        print("Calculated 'price_pass_through' (total_fare_usd / jet_fuel_usd_barrel)")
        
    # KPI 2: Fuel Price Change Percentage and Fuel Shock Flag
    # This helps us see if the airline experienced a sudden jump in fuel costs
    if 'jet_fuel_usd_barrel' in df.columns and 'airline' in df.columns:
        # Calculate percentage change in fuel price for each airline
        df['fuel_price_change_pct'] = df.groupby('airline')['jet_fuel_usd_barrel'].pct_change() * 100
        
        # Flag if the fuel price increased by more than 10%
        df['fuel_shock_flag'] = df['fuel_price_change_pct'] > 10
        print("Calculated 'fuel_price_change_pct' and 'fuel_shock_flag' (flags >10% change)")

    print(f"\n3. Load: Saving the cleaned data to {output_path}")
    # Make sure the folder exists before we try to save the file
    folder_path = os.path.dirname(output_path)
    os.makedirs(folder_path, exist_ok=True)
    
    # Save the dataframe back to a new CSV file
    df.to_csv(output_path, index=False)
    print("ETL Pipeline finished successfully!")

# This is where the script starts running
if __name__ == "__main__":
    # Get the folder where this script is located
    current_folder = os.path.dirname(__file__)
    
    # Go up one folder to the main project folder
    base_folder = os.path.abspath(os.path.join(current_folder, '..'))
    
    # Set the input and output file paths
    input_file = os.path.join(base_folder, 'data/processed/3_ticket_prices_and_surcharges.csv')
    output_file = os.path.join(base_folder, 'data/cleaned_dataset/cleaned_ticket_prices_with_kpis.csv')
    
    # Run the function we created above
    run_etl(input_file, output_file)
