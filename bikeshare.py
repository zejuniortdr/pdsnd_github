from datetime import datetime, timedelta
import os
import platform
import sys
import time

import pandas as pd


CITY_DATA = {
    "chicago": "chicago.csv",
    "new york city": "new_york_city.csv",
    "washington": "washington.csv",
}

MONTHS_NAMES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
}

WEEKDAYS_NAMES = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]


def clear_terminal():
    """Function to clear terminal and improve readability"""
    if platform.system() != "Windows":
        os.system("clear")
    else:
        os.system("cls")


def get_most_commum(df):
    """
    Function to get the most commum value and count it occurrencies
    Args:
        (df) df - DataFrame filtered by the collum to count
    Returns:
        (str) most_common - Most commum name in the collum informed
        (int) count - Number of occurrecies
    """
    df_most_common = df.value_counts().to_frame()
    most_common = df_most_common.index.values[0]
    count = df_most_common.values[0][0]
    return most_common, count


def age_range(row, step=10):
    """
    Function to calculate date range from users
    Args:
        (pd row) row - Row of DataFrame
    Returns:
        (str) Date Range, for example: "0-10", "10-20", "20-30"
        (str) "N/A" when non applicable
        (str) "" (empty string) Some cities do not have year of birth
    """
    try:
        age = datetime.now().year - int(row["Birth Year"])
        age_range_min = (age // step) * step
        age_range_max = age_range_min + step
        return f"{age_range_min}-{age_range_max}"
    except ValueError:
        return "N/A"
    except KeyError:
        return ""


def get_route(row):
    """
    Function to join Start and End Station as a Route
    Args:
        (pd row) row - Row of DataFrame
    Returns:
        (str) "FROM: [Start Station] TO: [End Station]"
    """
    return f"FROM: {row['Start Station']} TO: {row['End Station']}"


def get_dict_key_name_from_value(input_dict, value):
    """
    Function to get dict key name from a key value
    Args:
        (dict) input_dict - dict to search for the value
        (int) value - value used in search
    Returns:
        (str) key - key from dict with the value informed
        None - if it was not found
    """
    try:
        key = list(input_dict.keys())[list(input_dict.values()).index(value)]
        return key
    except ValueError:
        return None


def get_input_data(label, validation_data, enable_all=False):
    """
    Generic function to get data from input and validate until is correct

    Returns:
        (str) label - label for messages to user. Examples: city, month or day
        (list) validation_data - list to be compare against user input
        (boolean) enable_all - allow the user to type [all] for a filter
    """
    while True:
        try:
            enable_all_message = " or type 'all'" if enable_all else ""

            user_input = input(
                f"Choose a {label} ({validation_data}{enable_all_message}): "
            ).lower()

            if user_input == "exit":
                sys.exit()

            allow_all = user_input == "all" and enable_all
            if user_input in validation_data or allow_all:
                return user_input

            print(
                f"Invalid {label} name '{user_input}'. "
                "Please choose one of the following: "
                f"{validation_data}{enable_all_message}"
            )
        except KeyboardInterrupt:
            # Exit program when user interrupts
            sys.exit()


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by
        (str) day - name of the day of week to filter by
        "all" is a valid input to month and day
    """
    print("Hello! Let's explore some US bikeshare data!")
    print("If you want to quit, just type 'exit' anytime\n\n")
    # get user input for city (chicago, new york city, washington).
    # HINT: Use a while loop to handle invalid inputs
    city = get_input_data("city", list(CITY_DATA.keys()))

    # get user input for month (all, january, february, ... , june)
    month = get_input_data("month", list(MONTHS_NAMES.keys()), enable_all=True)

    # get user input for day of week (all, monday, tuesday, ... sunday)
    day = get_input_data("day of week", WEEKDAYS_NAMES, enable_all=True)

    print("-" * 40)
    return city, month, day


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month
    and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by
        (str) day - name of the day of week to filter by
        "all" is a valid input to month and day
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    try:
        df = pd.read_csv(CITY_DATA[city])
    except FileNotFoundError:
        print(
            f"Missing file [{CITY_DATA[city]}]"
            "\nPlease place this data file in the same "
            "folder as the bikeshare.py file and restart."
        )
        sys.exit()

    df["Start Time"] = pd.to_datetime(df["Start Time"])

    # extract month from Start Time to create new column
    df["month"] = df["Start Time"].dt.month
    
    # extract day of week from Start Time to create new column
    df["day_of_week"] = df["Start Time"].dt.day_name()
    
    # extract hour from Start Time to create new column
    df["hour"] = df["Start Time"].dt.hour

    # Concatenate Start and End station to create new column route
    df["route"] = df.apply(lambda row: get_route(row), axis=1)
    if "Birth Year" in df:
        df["age_range"] = df.apply(lambda row: age_range(row), axis=1)

    # Filter by Month when different from all
    if month != "all":
        df = df[df["month"] == MONTHS_NAMES[month]]

    # Filter by day of week when different from all
    if day != "all":
        df = df[df["day_of_week"] == day.title()]

    return df


def format_percent(num, total):
    """Calculate and format percent message"""
    return f"{num / total* 100:.2f}%"


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print("\nCalculating The Most Frequent Times of Travel...\n")
    start_time = time.time()
    total_count = len(df)

    # display the most common month
    month, count = get_most_commum(df["month"])
    month = get_dict_key_name_from_value(MONTHS_NAMES, month)
    print(
        f"The most common month is {month.title()}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    # display the most common day of week
    day_of_week, count = get_most_commum(df["day_of_week"])
    print(
        f"The most common day of week is {day_of_week}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    # display the most common start hour
    hour, count = get_most_commum(df["hour"])
    print(
        f"The most common start hour is {hour}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    print(f"\nThis took {time.time() - start_time} seconds.")
    print("-" * 40)
    print("\n\n")


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print("\nCalculating The Most Popular Stations and Trip...\n")
    start_time = time.time()
    total_count = len(df)

    # display most commonly used start station
    start_station, count = get_most_commum(df["Start Station"])
    print(
        f"The most commonly used start station is {start_station}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    # display most commonly used end station
    end_station, count = get_most_commum(df["End Station"])
    print(
        f"The most commonly used end station is {end_station}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    # display most frequent combination of start station and end station trip
    # TODO: most frequent combination
    route, count = get_most_commum(df["route"])
    print(
        f"The most commonly route is {route}. "
        f"Count: {count} ({format_percent(count, total_count)})"
    )

    print(f"\nThis took {time.time() - start_time} seconds.")
    print("-" * 40)
    print("\n\n")


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print("\nCalculating Trip Duration...\n")
    start_time = time.time()

    # display total travel time
    total_time_in_seconds = int(df["Trip Duration"].sum())
    print(
        f"Total travel time is {total_time_in_seconds} seconds "
        f"({timedelta(seconds=total_time_in_seconds)})"
    )

    # display mean travel time
    mean_time_in_seconds = int(df["Trip Duration"].mean())
    print(
        f"Mean travel time is {mean_time_in_seconds} seconds "
        f"({timedelta(seconds=mean_time_in_seconds)})"
    )

    # display max travel time
    max_time_in_seconds = int(df["Trip Duration"].max())
    print(
        f"Max travel time is {max_time_in_seconds} seconds "
        f"({timedelta(seconds=max_time_in_seconds)})"
    )

    # display min travel time
    min_time_in_seconds = int(df["Trip Duration"].min())
    print(
        f"Min travel time is {min_time_in_seconds} seconds "
        f"({timedelta(seconds=min_time_in_seconds)})"
    )

    print(f"\nThis took {time.time() - start_time} seconds.")
    print("-" * 40)
    print("\n\n")


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print("\nCalculating User Stats...\n")
    start_time = time.time()

    # Display counts of user types
    df_users_types = df.groupby(["User Type"])["User Type"].count()
    print()
    print(df_users_types.to_string())

    try:
        # Display counts of gender
        df_gender = df.groupby(["Gender"])["Gender"].count()
        print("\n")
        print(df_gender.to_string())
        empty = len(df) - sum(df_gender.values.tolist())
        print(f"Empty {empty}")
    except KeyError:
        # Some cities do not have gender
        pass

    try:
        # Display earliest, most recent, and most common year of birth
        df_erliest_year = int(df["Birth Year"].min())
        df_recent_year = int(df["Birth Year"].max())
        mode_year, _ = get_most_commum(df["Birth Year"])

        print(f"\nThe most erliest year of birth: {df_erliest_year}")
        print(f"The most recent year of birth: {df_recent_year}")
        print(f"The most common year of birth: {int(mode_year)}")

        print("\n\nUser's date range\n")
        df_age_range = df.groupby(["age_range"])["age_range"].count()
        print(df_age_range.sort_values(ascending=False).to_string())

    except KeyError:
        # Some cities do not have year of birth
        pass

    print(f"\nThis took {time.time() - start_time} seconds.")
    print("-" * 40)
    print("\n\n")


def raw_data(df):
    start = 0
    step_min, step_max = 1, 60
    total_rows = len(df)

    try:
        step = int(
            input(
                "\nHow many rows do you want to see? "
                "(min: 1, max: 60) (Default: 5) "
            )
        )
        step = max(step_min, min(step, step_max))
    except ValueError:
        step = 5

    end = start + step
    while True:
        print("\n")
        print(df.iloc[start:end, :-4])
        print(f"Showing {step} rows ({start}:{end}) rows of {total_rows}")
        user_input = input(
            f"\nDo you want to see the next {step} rows? (yes/no): "
        ).lower()

        if user_input != "yes":
            break

        start += step
        end += step


def menu():
    """Displays menu to users."""
    print("-" * 40)
    print(
        "To analise the data, please choose a menu number, "
        "or type 9 to restart or 0 to exit"
    )
    print("1 - Time Stats")
    print("2 - Station Stats")
    print("3 - Trip Duration Stats")
    print("4 - User Stats")
    print("5 - Raw Data")
    print("9 - Restart")
    print("0 - Exit")
    print("-" * 40)
    option = get_input_data("menu", ["1", "2", "3", "4", "5", "9", "0"])

    if option == "0":
        print("Bye!")
        sys.exit()

    return option


def header(city, month, day):
    """Displays header with the chosen filters to users."""
    print("\n\n\n")
    print("=" * 50)
    print("Chosen Filters:")
    print(f"City: {city}")
    print(f"Month: {month}")
    print(f"Day of Week: {day}")


def main():
    while True:
        clear_terminal()
        try:
            city, month, day = get_filters()
        except KeyboardInterrupt:
            break

        df = load_data(city, month, day)

        while True:
            option = int(menu())
            clear_terminal()

            if 1 <= option <= 4:
                header(city, month, day)
            if option == 1:
                time_stats(df)
            elif option == 2:
                station_stats(df)
            elif option == 3:
                trip_duration_stats(df)
            elif option == 4:
                user_stats(df)
            elif option == 5:
                raw_data(df)
            elif option == 9:
                break


if __name__ == "__main__":
    main()
