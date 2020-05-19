#!/usr/bin/env python3
#explores data about bike sharing systems in CH,NY and WA
import calendar
import string
import time
import pandas as pd
import numpy as np

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

VALID_MONTHS = [calendar.month_name[i].lower() for i in range(1, 7)]
VALID_DAYS = [d.lower() for d in calendar.day_name]
START_DATE_LABEL = 'Start Time'

def get_input(question, valid_inputs):
    """
    Helper function for asking a question and collect an input among valid
    possible options.

    Args:
        (str) question - The question to display.
        (List[str]) valid_inputs - The acceptable answers.
    Returns:
        (str) answer - The validated answer.
    """
    # Make sure that valid inputs are in lower case.
    answers = set([v.lower() for v in valid_inputs])
    # Make sure that valid inputs for display are in word capitalized.
    pp_valid_inputs = [string.capwords(v.lower()) for v in valid_inputs]
    answer = None
    # Loop untill a valid input is inserted.
    while answer not in answers:
        answer = input('\n%s. [Valid inputs: "%s"]\n' % (
            question, '", "'.join(pp_valid_inputs)))
        # We want to return lowercase (and we want to compare with lowercase).
        answer = answer.lower()
    return answer


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('Hello! Let\'s explore some US bikeshare data!')

    # Initialize month/day to "all".
    month = 'all'
    day = 'all'

    # City is a required parameter.
    city = get_input('Please insert the city to analyze', CITY_DATA.keys())

    filter_type = get_input(
        'Would you like to filter the data by month, day, both, or not at all? '
        'Type "none" for no time filter',
        ['month', 'day', 'both', 'none'])

    # We want to get the month in case the filter is by month or both month and
    # day.
    if filter_type in ('month', 'both'):
        month = get_input('Which month the rental started?', VALID_MONTHS)

    # We want to get the day in case the filter is by day or both month and day.
    if filter_type in ('day', 'both'):
        day = get_input('Which day the rental started?', VALID_DAYS)

    print('-'*40)
    return city, month, day


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    filename = CITY_DATA[city]
    try:
        df = pd.read_csv(filename, parse_dates=[1,2])
    except FileNotFoundError as e:
        print('Pandas wasn\'t able to open file "%s", do you have the needed '
              'CSV/data files in your path? Original exception "%s"' % (
                  filename, e))
        raise e

    filter = None
    # If we want to filter by month we want to update the filter.
    if month != 'all':
        # Months are in the range [1-12], indexes are in the range [0-11],
        # we need to add 1 for getting the right month id [1-12].
        month_id = VALID_MONTHS.index(month) + 1
        # Our filter is by month.
        filter = df[START_DATE_LABEL].dt.month == month_id

    # If we want to filter by day we want to update the filter.
    if day != 'all':
        # Days are between 0 (Monday) and 6 (Sunday), like in calendar.day_name.
        day_id = VALID_DAYS.index(day)
        filter2 = df[START_DATE_LABEL].dt.dayofweek == day_id
        if filter is None:
            # In case we filter only by day, we want to overwrite the filter.
            filter = filter2
        else:
            # Otherwise we want to put in AND the two conditions.
            filter &= filter2

    # If there is no filter, we just return the whole Dataframe.
    if filter is None:
        return df

    # Return the filtered DataFrame.
    return df[filter]


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    print("Most common start month... ", end='')
    # Month has small cardinality [1-12], no need to use uniq, bincount is
    # good enough.
    hist = np.bincount(df[START_DATE_LABEL].dt.month)
    print("%s (%d travels)" % (calendar.month_name[hist.argmax()], hist.max()))

    print("Most common start day of week... ", end='')
    # Same for day of week.
    hist = np.bincount(df[START_DATE_LABEL].dt.dayofweek)
    print("%s (%d travels)" % (VALID_DAYS[hist.argmax()].capitalize(),
                               hist.max()))

    print("Most common start hour (24h)... ", end='')
    # Same for hour.
    hist = np.bincount(df[START_DATE_LABEL].dt.hour)
    print("%s:00 (%d travels)" % (hist.argmax(), hist.max()))

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # There isn't much difference between Start/End station, we can "templatize"
    # it with a function.
    def most_common_station(column, name):
        print('Most commonly used %s... ' % name, end='')
        # We get an histogram of stations/frequencies. This reduces the
        # cardinality to the number of stations. max/argmax will be very fast.
        station, counts = np.unique(column, return_counts=True)
        print('"%s" (%d trips)' % (station[counts.argmax()], counts.max()))

    most_common_station(df['Start Station'], 'Start Station')

    most_common_station(df['End Station'], 'End Station')

    print('Most commonly used combination of start station and end station...')
    # We need to count by two columns, so groupby is necessary.
    counts = df.groupby(['Start Station', 'End Station']).size()
    top_itinerary = counts.index[counts.values.argmax()]
    print('"%s" -> "%s" (%d trips)' % (top_itinerary[0], top_itinerary[1],
                                       counts.values.max()))

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # We use the Timedelta because it has a nicer representation for large
    # numbers.
    print('Total travel time: %s' % (df['End Time'] - df['Start Time']).sum())

    # We use Trip Time that better suits smaller numers.
    print('Mean travel time: %.1f secs' % df['Trip Duration'].mean())

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Count of User Type and Gender is similar enough that we can put in a
    # function.
    def print_counts(column, type):
        print('\nCounts of %s' % type)
        labels, counts = np.unique(column, return_counts=True)
        # We use a DataFrame just for printing the table.
        res = pd.DataFrame({type: labels, 'Counts': counts})
        print(res.to_string(index=False, max_rows=None))

    # We need fillna() for dealing with lack of User Type in some rows.
    print_counts(df["User Type"].fillna(value='Unknown'), "User Type")

    # Not all data sets have Gender.
    if 'Gender' in df.keys():
        # We need fillna() for dealing with lack of User Type in some rows.
        print_counts(df["Gender"].fillna(value='Unknown'), 'Gender')
    else:
        print('No gender in this dataset, skipping statistics on gender.')

    if 'Birth Year' in df.keys():
        print('\nYear of birth stats...')
        years, counts = np.unique(df['Birth Year'].dropna(), return_counts=True)
        print('Earliest year: %d' % years.min())
        print('Most recent year: %d' % years.max())
        print('Most common year: %d (%s trips)' % (years[counts.argmax()], counts.max()))
    else:
        print('No Birth Year in this dataset, skipping statistics on Birth Year.')

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def raw_data(df):
    """Handles the output of raw data (when requested from the user)."""
    go_ahead = get_input('Do you want to see the first 5 raw items?', ['Yes', 'No'])

    if go_ahead == 'no':
        return

    # Give a more user friendly name to the ID.
    d = df.rename(columns={df.keys()[0]: "ID"})

    count = 0
    max_count = d.shape[0]

    while go_ahead == 'yes':
        for _ in range(5):
            # We don't want to overflow.
            if count >= max_count:
                return
            print(d.loc[count].to_string())
            count += 1
        go_ahead = get_input('Do you want to see the next 5 raw items?', ['Yes', 'No'])


def main():
    city, month, day = get_filters()
    df = load_data(city, month, day)

    time_stats(df)
    station_stats(df)
    trip_duration_stats(df)
    user_stats(df)
    raw_data(df)

    restart = input('\nWould you like to restart? Enter yes or no.\n').lower()
    return restart == 'yes' or restart == 'y'


if __name__ == '__main__':
    while main():
        pass
