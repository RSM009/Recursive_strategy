def update_levels_csv(entered_level, to_next_level):
    # Load the CSV file into a DataFrame
    try:
        df = pd.read_csv('levels.csv')
    except FileNotFoundError:
        # If the file does not exist, create an empty DataFrame with the required columns
        df = pd.DataFrame(columns=['entered_level', 'to_next_level', 'cycle_count'])

    # Determine the next cycle count
    if not df.empty:
        last_cycle_count = df['cycle_count'].iloc[-1]
        new_cycle_count = last_cycle_count + 1
    else:
        new_cycle_count = 1  # Start with 1 if the CSV is empty

    # Add a new row with the given values and the incremented cycle count
    new_row = {
        'entered_level': entered_level,
        'to_next_level': to_next_level,
        'cycle_count': new_cycle_count
    }
    df = df.append(new_row, ignore_index=True)
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv('levels.csv', index=False)

    print(f"Updated CSV file with: entered_level={entered_level}, to_next_level={to_next_level}, cycle_count={new_cycle_count}")

update_levels_csv(100000, 101)
