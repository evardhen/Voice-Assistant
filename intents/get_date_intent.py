from datetime import datetime


if __name__ == "__main__":
    # Get current date and time
    current_datetime = datetime.now()
    # Extract date
    current_date = current_datetime.date()
    formatted_date = current_date.strftime("%d.%m.%Y")

    # Get the day of the week as an integer (0=Monday, 1=Tuesday, ..., 6=Sunday)
    day_of_week_int = current_date.weekday()

    # Define a list of weekday names
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get the actual name of the day of the week
    day_of_week_name = weekday_names[day_of_week_int]

    # Print the day of the week
    print(f"Today is {day_of_week_name}, the {formatted_date}.")