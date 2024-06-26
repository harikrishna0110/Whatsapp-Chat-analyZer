import pandas as pd

from textblob import TextBlob

import re

def extract_chat_data(chat_data):
    messages = []
    patterns = [
        r'^\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\s?(?:AM|PM)?\] (.+?): (.+)$',
        r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})(?: (?:am|pm)|\s-\s)(.+?): (.+)$'
    ]
    for line in chat_data.split('\n'):
        matched = False
        for pattern in patterns:
            try:
                match = re.match(pattern, line)
                if match:
                    date = match.group(1)
                    time = match.group(2)
                    sender = match.group(3)
                    message = match.group(4)
                    messages.append((date, time, sender, message))
                    matched = True
                    break  # Break the loop if a match is found
            except AttributeError:
                # Handle the case when the pattern doesn't match
                print(f"Warning: Pattern didn't match for line: {line}")
        if not matched:
            print(f"Warning: No pattern matched for line: {line}")
    return messages




def create_dataframe(messages):
    df = pd.DataFrame(messages, columns=['Date', 'Time', 'Sender', 'Message'])
    # Combine Date and Time columns to create a new column 'Datetime'
    try:
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
    except ValueError:
        # Handle datetime conversion errors
        print("Error: Unable to convert to datetime")

    # Extract year, month, day, hour, and minute from 'Datetime' column
    df['only_date'] = df['Datetime'].dt.date
    df['Year'] = df['Datetime'].dt.year
    df['Month_Num'] = df['Datetime'].dt.month
    df['Month'] = df['Datetime'].dt.month_name()
    df['Day'] = df['Datetime'].dt.day
    df['Day_name'] = df['Datetime'].dt.day_name()
    df['Hour'] = df['Datetime'].dt.hour
    df['Minute'] = df['Datetime'].dt.minute
    df['Sentiment'] = df['Message'].apply(lambda x: TextBlob(x).sentiment.polarity)

    period = []
    for hour in df[['Day_name', 'Hour']]['Hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period
    return df



