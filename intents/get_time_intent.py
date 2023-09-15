from datetime import datetime

if __name__ == "__main__":
    # Get current date and time
    current_datetime = datetime.now()
    current_time = current_datetime.time()
    formatted_time = current_time.strftime("%H:%M")
    # Print the current date and time
    print(f"Current time: {formatted_time}")