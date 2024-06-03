import streamlit as st
import preprocessor
import helper
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import nltk
from nltk.corpus import stopwords

# Download NLTK stopwords
nltk.download('stopwords')

# Load English stopwords
stop_words = set(stopwords.words('english'))

# Function to remove stop words from a text
def remove_stopwords(text):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

# Apply remove_stopwords function to the 'message' column




def generate_pdf(data_dict, output_file, images):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 40, "WhatsApp Chat Analysis Report")

    # Top Statistics
    c.drawString(30, height - 80, "Top Statistics")
    c.drawString(30, height - 100, f"Total Messages: {data_dict['num_messages']}")
    c.drawString(30, height - 120, f"Total Words: {data_dict['words']}")
    c.drawString(30, height - 140, f"Links Shared: {data_dict['num_links']}")

    # Add graphs to PDF
    y_position = height - 160
    for img_path in images:
        if y_position < 100:
            c.showPage()
            y_position = height - 40
        c.drawImage(img_path, 30, y_position - 200, width=500, height=200)
        y_position -= 220

    c.save()
    buffer.seek(0)
    with open(output_file, "wb") as f:
        f.write(buffer.getvalue())


def display_initial_message(theme='dark'):
    st.warning("Your privacy is our priority: No data is stored, and your information remains 100% secure.")
    if theme == 'dark':
        background_color = "#00008B"
        text_color = "#FFFFFF"
    else:
        background_color = "#FFFFFF"
        text_color = "#000000"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div style="text-align: center; border: 2px solid {background_color}; padding: 20px; border-radius: 10px; background-color: {background_color}; color: {text_color}; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                <h2>Browse a file and click on 'Show Analysis' to get the detailed report.</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    extracted_data = preprocessor.extract_chat_data(data)
    df = preprocessor.create_dataframe(extracted_data)
    df['Message'] = df['Message'].apply(remove_stopwords)
    temp = df[df['Message'] != '<Media omitted>']
    st.write(temp)

    user_list = df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)
    if st.sidebar.button("Show Analysis"):
        with st.spinner("Generating report..."):
            num_messages, words, num_links = helper.fetch_stats(selected_user, df)

            st.title("Top Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Links Shared")
                st.title(num_links)

            images = []

            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['Message'], color='green')
            plt.xticks(rotation=90, ha='right', fontsize=8)
            st.pyplot(fig)
            img_path = tempfile.mktemp(suffix=".png")
            fig.savefig(img_path)
            images.append(img_path)

            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['Message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            img_path = tempfile.mktemp(suffix=".png")
            fig.savefig(img_path)
            images.append(img_path)

            st.title('Activity Map')
            col1, col2 = st.columns(2)
            with col1:
                st.header("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
                img_path = tempfile.mktemp(suffix=".png")
                fig.savefig(img_path)
                images.append(img_path)
            with col2:
                st.header("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
                img_path = tempfile.mktemp(suffix=".png")
                fig.savefig(img_path)
                images.append(img_path)

            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            try:
                user_heatmap_sorted = user_heatmap.sort_index(axis=1)
            except Exception as e:
                st.error(f"Error occurred during sorting: {e}")
                st.stop()
            st.write("Sorted DataFrame:", user_heatmap_sorted)
            fig, ax = plt.subplots()
            try:
                ax = sns.heatmap(user_heatmap_sorted)
            except Exception as e:
                st.error(f"Error occurred during heatmap creation: {e}")
                st.stop()
            st.pyplot(fig)
            img_path = tempfile.mktemp(suffix=".png")
            fig.savefig(img_path)
            images.append(img_path)

            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x = helper.most_busy_user(df)
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                plt.xticks(rotation=90, ha='right', fontsize=8)
                st.pyplot(fig)
                img_path = tempfile.mktemp(suffix=".png")
                fig.savefig(img_path)
                images.append(img_path)

            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)
            img_path = tempfile.mktemp(suffix=".png")
            fig.savefig(img_path)
            images.append(img_path)

            st.title('Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            st.pyplot(fig)
            img_path = tempfile.mktemp(suffix=".png")
            fig.savefig(img_path)
            images.append(img_path)

            st.title("Emoji Analysis")
            emoji_df = helper.emogis_used(selected_user, df)
            new_emoji_df = emoji_df.nlargest(5, 'Count')
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(new_emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(new_emoji_df['Count'], labels=new_emoji_df['Emoji'], autopct="%0.2f%%")
                ax.axis('equal')
                st.pyplot(fig)
                img_path = tempfile.mktemp(suffix=".png")
                fig.savefig(img_path)
                images.append(img_path)


            # Sentiment Analysis
            st.title("Sentiment Analysis")
            selected_columns = ["Message", "Sentiment"]
            display_df = df[selected_columns]

            st.dataframe(display_df)

            # Display Sentiment Scale Information
            st.markdown("### Sentiment Scale:")
            st.markdown("- **Negative:** Values close to -1 indicate strong negative sentiment.")
            st.markdown("- **Neutral:** A sentiment score of 0 indicates neutral sentiment.")
            st.markdown("- **Positive:** Values close to 1 indicate strong positive sentiment.")

            # Collect data for PDF
            data_dict = {
                'num_messages': num_messages,
                'words': words,
                'num_links': num_links,
                'timeline': timeline,
                'daily_timeline': daily_timeline,
                'busy_day': busy_day,
                'busy_month': busy_month,
                'user_heatmap_sorted': user_heatmap_sorted,
                'most_busy_users': x if selected_user == 'Overall' else None,
                'most_common_words': most_common_df,
                'emoji_analysis': new_emoji_df
            }

            pdf_output = BytesIO()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                generate_pdf(data_dict, tmp_file.name, images)
                with open(tmp_file.name, "rb") as f:
                    pdf_output.write(f.read())
            st.download_button(label="Download PDF", data=pdf_output.getvalue(), file_name="chat_analysis.pdf", mime="application/pdf")
            st.warning("Your privacy is our priority: No data is stored, and your information remains 100% secure.")

            # Add a clean up button
            if st.button("Clean Up"):
                st.experimental_rerun()
    else:
        display_initial_message()
else:
    display_initial_message()
