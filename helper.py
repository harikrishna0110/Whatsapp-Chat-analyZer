from urlextract import URLExtract
from wordcloud import wordcloud, WordCloud
from collections import Counter
import pandas as pd
import regex as re
from textblob import TextBlob


extract = URLExtract()
def fetch_stats(selected_user, df):
        if selected_user == 'Overall':
          num_messages =df.shape[0]
          words =[]
          for messages in df['Message']:
            words.extend(messages.split())
          link = []
          for message in df['Message']:
            link.extend(extract.find_urls(message))
          return num_messages , len(words) ,len(link)

        else:
            new_df = df[df['Sender'] == selected_user]
            num_messages = new_df.shape[0]
            words = []
            for messages in new_df['Message']:
                 words.extend(messages.split())
            link = []
            for message in df['Message']:
              link.extend(extract.find_urls(message))
            return num_messages , len(words) ,len(link)

def most_busy_user (df):
    x = df['Sender'].value_counts().head()
    return x
def create_wordcloud(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group notification']
    temp = temp[temp['Message'] != '<Media omitted>']

    wc = WordCloud(width=500 ,height=500,min_font_size=10,background_color='white')
    df_wc = wc.generate(temp['Message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    words = []
    for message in temp['Message']:
        words.extend(message.split())
        df= pd.DataFrame(Counter(words).most_common(20))

    return df

def emogis_used(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group notification']
    temp = temp[temp['Message'] != '<Media omitted>']
    all_emojis = []

    for message in temp['Message']:
        # Define a regex pattern to match emojis
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)

        # Extract emojis from text
        emojis_in_message = emoji_pattern.findall(message)

        # Append the emojis found in this message to the list of all emojis
        all_emojis.extend(emojis_in_message)

    emoji_counts = Counter(all_emojis)

    emojis_df = pd.DataFrame(emoji_counts.items(), columns=['Emoji', 'Count'])

    return emojis_df
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    timeline = df.groupby(['Year', 'Month_Num', 'Month']).count()['Message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['Month'][i] + "-" + str(timeline['Year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['Message'].reset_index()

    return daily_timeline
def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    return df['Day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    return df['Month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    user_heatmap = df.pivot_table(index='Day_name', columns='period', values='Message', aggfunc='count').fillna(0)

    return user_heatmap


def sentiment_analysis_df(selected_user, df, message_column='Message', user_column='Sender'):
    """
    Perform sentiment analysis on messages of a selected user from a DataFrame.

    Args:
    - selected_user (str): The user for whom sentiment analysis is to be performed.
    - df (DataFrame): Input DataFrame containing messages.
    - message_column (str, optional): Name of the column containing messages. Default is 'Message'.
    - user_column (str, optional): Name of the column containing user names. Default is 'Sender'.

    Returns:
    - DataFrame: A pandas DataFrame containing the sentiment analysis scores for the selected user.
    """
    # Filter DataFrame for messages of the selected user
    user_df = df[df[user_column] == selected_user]

    # Initialize lists to store sentiment scores
    polarities = []
    subjectivities = []

    # Perform sentiment analysis for each message
    for message in user_df[message_column]:
        blob = TextBlob(message)
        polarities.append(blob.sentiment.polarity)
        subjectivities.append(blob.sentiment.subjectivity)

    # Add sentiment scores as new columns to the DataFrame
    user_df['Sentiment Polarity'] = polarities
    user_df['Sentiment Subjectivity'] = subjectivities

    return user_df

# Example usage:
# selected_user = 'User1'
# sentiment_df = sentiment_analysis_df(selected_user, df)






