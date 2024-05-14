import streamlit as st
import preprocessor
import helper
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    extracted_data = preprocessor.extract_chat_data(data)
    df = preprocessor.create_dataframe(extracted_data)
    temp = df[df['Message'] != '<Media omitted>']
    st.write(temp)

    user_list = df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Links Shared")
            st.title(num_links)

        import matplotlib.pyplot as plt
        import seaborn as sns
        import streamlit as st

        # Assuming selected_user and df are already defined

        # Set the title
        st.title("Monthly Timeline")

        # Generate the monthly timeline
        timeline = helper.monthly_timeline(selected_user, df)

        # Create the plot
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['Message'], color='green')

        # Customize the appearance of x-axis labels
        plt.xticks(rotation=90, ha='right',
                   fontsize=8)  # Rotate labels by 45 degrees, align them to the right, and reduce font size

        # Display the plot
        st.pyplot(fig)

        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['Message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        # Sort the user heatmap DataFrame by the x-axis values
        try:
            user_heatmap_sorted = user_heatmap.sort_index(axis=1)
        except Exception as e:
            st.error(f"Error occurred during sorting: {e}")
            st.stop()

        # Print sorted DataFrame for debugging
        st.write("Sorted DataFrame:", user_heatmap_sorted)

        # Create the heatmap plot
        fig, ax = plt.subplots()
        try:
            ax = sns.heatmap(user_heatmap_sorted)
        except Exception as e:
            st.error(f"Error occurred during heatmap creation: {e}")
            st.stop()

        # Display the plot in Streamlit
        st.pyplot(fig)

        if selected_user == 'Overall':
            st.title('Most Busy Users')

            # Get data for plotting
            x = helper.most_busy_user(df)
            name = x.index
            count = x.values

            # Plotting
            fig, ax = plt.subplots()
            ax.bar(name, count)
            plt.xticks(rotation=90, ha='right',fontsize=8)

            # Display plot using Streamlit
            st.pyplot(fig)

        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])

        st.title('Most commmon words')
        st.pyplot(fig)

        emoji_df = helper.emogis_used(selected_user, df)
        new_emoji_df = emoji_df.nlargest(5, 'Count')
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(new_emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(new_emoji_df['Count'], labels=new_emoji_df['Emoji'], autopct="%0.2f%%")
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Display the pie chart
            st.pyplot(fig)
