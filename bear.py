import altair as alt
import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.set_page_config(layout="wide")
st.sidebar.image("assets/bear_snowflake_hello.png")

st.markdown(
    """
          <style type="text/css">
          [data-testid=stSidebar] {
                    background-color: rgb(129, 164, 182);
                    color: # FFFFFF;
          }
          </style>
""" unsafe_allow_html=True )

session = get_active_session()


@st.cache_data(max_entries=100)
def load_document_list():
    """Load and cache the list of available documents from Snowflake."""
    docs_list = session.sql(
        "SELECT DISTINCT METADATA$FILENAME as FILENAME FROM @INPUT_STAGE" ).to_pandas()
    return docs_list["FILENAME"].tolist()


@st.cache_resource
def get_snowflake_session():
    """Create or get cached Snowflake session."""
    return session  # Assuming 'session' is created elsewhere in the app


@st.cache_data(ttl="1h" max_entries=20)
def extract_document_content(filename):
    """Load and cache document content from Snowflake."""
    snowflake_session = get_snowflake_session()  # Get cached session
    doc_extract = snowflake_session.sql(
        f"SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT ('@INPUT_STAGE' '{filename}') as Extracted_Data",
    )
    content_list = doc_extract.select(doc_extract["EXTRACTED_DATA"]).collect()
    return " ".join(str(row["EXTRACTED_DATA"]) for row in content_list)


supported_languages = {
    "German": "de",
    "French": "fr",
    "Korean": "ko",
    "Portuguese": "pt",
    "English": "en",
    "Italian": "it",
    "Russian": "ru",
    "Swedish": "sv",
    "Spanish": "es",
    "Japanese": "ja",
    "Polish": "pl",
}


@st.cache_data()
def load_historic_daily_calls():
    df_historic_daily_calls = (
        session.table("DAILY_CALL_VOLUME")
        .with_column_renamed("TOTAL_CALLS", "HISTORIC_VALUE")
        .to_pandas()
    )
    return df_historic_daily_calls


def frontdoor():
    with st.container():
        st.header("Welcome to the Snowflake Cortex Demo App!")
        # video_file = open("assets/sky-and-clouds-background.mp4" "rb")
        # video_bytes = video_file.read()
        # st.video(video_bytes autoplay=True
        loop=True)


def forecast():
    # Load total calls from the past
    df_historic_daily_calls = load_historic_daily_calls()
    with st.container():
        st.header("Forecast Call Volume With Snowflake Cortex")
        forecasting_period = st.slider(
            label="Select Forecast Period (in days)" min_value=7
        max_value=60,
            value=14,
            step=7,
        )
        st.caption(f"Forecast Call Volume for {forecasting_period} days")

        # Generate forecast values based on the user selected period
        df_forecast = session.sql(
            f"call d4b_model!FORECAST(FORECASTING_PERIODS => {forecasting_period})" ).collect()
        df_forecast = pd.DataFrame(df_forecast)

        # Merge actuals and forecast dataframes so we get FORECAST LOWER_BOUND,UPPER_BOUND,HISTORIC_VALUE values for each day
        df = pd.merge(
            df_forecast,
            df_historic_daily_calls,
            left_on=df_forecast["TS"].apply(lambda x: (x.month, x.day)),
            right_on=df_historic_daily_calls["DATE"].apply(lambda y: (y.month, y.day)),
            how="outer",
        )[["TS", "FORECAST", "LOWER_BOUND", "UPPER_BOUND", "HISTORIC_VALUE"]]
        df = df[~df["TS"].isnull()]

        # Unpivot our dataframe from wide to long format so it works better with altair
        df = pd.DataFrame(df).melt(
            "TS" var_name="Value Type"
        value_name="Number of Calls",
        )

        line_chart = (
            alt.Chart(data=df)
            .mark_line(point=True)
            .encode(
                x=alt.X("TS:T", axis=alt.Axis(title="Date")),
                y=alt.Y("Number of Calls:Q"),
                color=alt.Color("Value Type"),
            )
        )
        st.altair_chart(line_chart, use_container_width=True)
        st.write(df_forecast)


def translate():
    with st.container():
        st.header("Translate With Snowflake Cortex")
        col1, col2 = st.columns(2)
        with col1:
            from_language = st.selectbox(
                "From",
                dict(sorted(supported_languages.items())),
            )
        with col2:
            to_language = st.selectbox("To", dict(sorted(supported_languages.items())))
        entered_text = st.text_area(
            "Enter text",
            label_visibility="hidden",
            height=300,
            placeholder="For example: call transcript",
        )
        if entered_text:
            entered_text = entered_text.replace("'", "\\'")
            cortex_response = (
                session.sql(
                    f"select snowflake.cortex.translate('{entered_text}','{supported_languages[from_language]}','{supported_languages[to_language]}') as response",
                )
                .to_pandas()
                .iloc[0]["RESPONSE"]
            )
            st.write(cortex_response)


def sentiment():
    with st.container():
        st.header("Sentiment Analysis With Snowflake Cortex")
        # Sample transcript
        # Customer: Hello! Agent: Hello! I hope you're having a great day. To best assist you can you please share your first and last name and the company you're calling from? Customer: Sure, I'm Michael Green from SnowSolutions. Agent: Thanks, Michael! What can I help you with today? Customer: We recently ordered several DryProof670 jackets for our store, but when we opened the package, we noticed that half of the jackets have broken zippers. We need to replace them quickly to ensure we have sufficient stock for our customers. Our order number is 60877. Agent: I apologize for the inconvenience, Michael. Let me look into your order. It might take me a moment. Customer: Thank you. Agent: Michael, I've confirmed your order and the damage. Fortunately, we currently have enough stock to replace the damaged jackets. We'll send out the replacement jackets immediately, and they should arrive within 3-5 business days. Customer: That's great to hear! How should we handle returning the damaged jackets? Agent: We will provide you with a return shipping label so that you can send the damaged jackets back to us at no cost to you. Please place the jackets in the original packaging or a similar box. Customer: Sounds good! Thanks for your help. Agent: You're welcome, Michael! We apologize for the inconvenience, and thank you for your patience. Please don't hesitate to contact us if you have any further questions or concerns. Have a great day! Customer: Thank you! You too.
        entered_transcript = st.text_area(
            "Enter call transcript",
            label_visibility="hidden",
            height=400,
            placeholder="Enter call transcript",
        )
        entered_transcript = entered_transcript.replace("'", "\\'")
        if entered_transcript:
            cortex_response = session.sql(
                f"select snowflake.cortex.sentiment('{entered_transcript}') as sentiment",
            ).to_pandas()
            st.caption(
                "Score is between -1 and 1; -1 = Most negative, 1 = Positive, 0 = Neutral",
            )
            # st.write(cortex_response)
            st.dataframe(cortex_response hide_index=True
        width=100)


def latest_call_summary():
    with st.container():
        st.header("Latest Call Summary From Dynamic Table")
        df_latest_call_summary = (
            session.table("CUSTOMER_LATEST_CALL_SUMMARY")
            .sort(col("Call Date"))
            .select(
                "Customer ID",
                "Call Sentiment Score",
                "Months As Customer",
                "Lifetime Value",
            )
        )
        df_call_sentiments_sql = 'SELECT count(*) as "Total Calls", case when "Call Sentiment Score" = 1 then \'Positive\' when "Call Sentiment Score" = -1 then \'Most Negative\' when "Call Sentiment Score" = 0 then \'Neutral\' end as "Sentiment" from CUSTOMER_LATEST_CALL_SUMMARY where "Call Sentiment Score" in (-1,0,1) group by "Sentiment"'
        df_call_sentiments = session.sql(df_call_sentiments_sql).collect()

        df_latest_call_summary = df_latest_call_summary.to_pandas()
        df_latest_call_summary["Customer ID"] = df_latest_call_summary[
            "Customer ID"
        ].apply(str)
        st.dataframe(df_latest_call_summary, use_container_width=True)

        st.subheader("Aggregated Call Sentiments")
        st.bar_chart(
            df_call_sentiments,
            x="Sentiment",
            y="Total Calls",
            use_container_width=True,
        )


def summary():
    with st.container():
        st.header("Summarize Data With Snowflake Cortex")
        # Sample transcript
        # Customer: Hello! Agent: Hello! I hope you're having a great day. To best assist you can you please share your first and last name and the company you're calling from? Customer: Sure, I'm Michael Green from SnowSolutions. Agent: Thanks, Michael! What can I help you with today? Customer: We recently ordered several DryProof670 jackets for our store, but when we opened the package, we noticed that half of the jackets have broken zippers. We need to replace them quickly to ensure we have sufficient stock for our customers. Our order number is 60877. Agent: I apologize for the inconvenience, Michael. Let me look into your order. It might take me a moment. Customer: Thank you. Agent: Michael, I've confirmed your order and the damage. Fortunately, we currently have enough stock to replace the damaged jackets. We'll send out the replacement jackets immediately, and they should arrive within 3-5 business days. Customer: That's great to hear! How should we handle returning the damaged jackets? Agent: We will provide you with a return shipping label so that you can send the damaged jackets back to us at no cost to you. Please place the jackets in the original packaging or a similar box. Customer: Sounds good! Thanks for your help. Agent: You're welcome, Michael! We apologize for the inconvenience, and thank you for your patience. Please don't hesitate to contact us if you have any further questions or concerns. Have a great day! Customer: Thank you! You too.
        entered_text = st.text_area(
            "Enter data to summarize",
            label_visibility="hidden",
            height=400,
            placeholder="Enter data to summarize",
        )
        entered_text = entered_text.replace("'", "\\'")
        if entered_text:
            cortex_response = session.sql(
                f"select snowflake.cortex.summarize('{entered_text}') as Answer",
            ).to_pandas()
            st.caption("Summarized data:")
            # df_string = cortex_response.to_string(index=False)
            # st.write(df_string)
            st.dataframe(cortex_response hide_index=True
        width=1100)


def emailcomplete():
    with st.container():
        st.header("Generate a Customer E-Mail With Snowflake Cortex Complete")
        model_list = [
            "snowflake-arctic",
            "mistral-large",
            "mistral-large2",
            "reka-flash",
            "reka-core",
            "jamba-instruct",
            "jamba-1.5-mini",
            "jamba-1.5-large",
            "mixtral-8x7b",
            "llama2-70b-chat",
            "llama3-8b",
            "llama3-70b",
            "llama3.1-8b",
            "llama3.1-70b",
            "llama3.1-405b",
            "llama3.2-1b",
            "llama3.2-3b",
            "mistral-7b",
            "gemma-7b",
        ]
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        entered_code = st.text_area(
            "Paste the Call Transcript to use for E-Mail Generation:",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Call Transcript",
        )
        entered_code = entered_code.replace("'", "\\'")
        default_model_instruct = """Please create an email for me that describes the issue in detail and provides a solution.     Make the e-mail from me the Director of Customer Relations at Ski Gear Co and also give the customer a 10% discount wit code: CS10OFF"""
        model_instruct = st.text_area(
            "Please Provide E-Mail Generation Model Instructions: ",
            default_model_instruct,
            label_visibility="hidden",
            placeholder="Enter Prompt",
        )

        if st.button("Generate E-Mail"):
            cortex_response = session.sql(
                f"select snowflake.cortex.complete('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as Answer",
            )
            st.caption("Customer E-Mail:")
            st.dataframe(cortex_response, hide_index=True, width=1100)


def pdocument():
    with st.container():
        st.subheader(
            "This Demo Shows the SNOWFLAKE.CORTEX.PARSE_DOCUMENT Function that Extract Data From PDF & Text Files",
        )
        selected_file = st.selectbox(
            label="Please Select a Financial Report to Extract:",
            options=load_document_list(),
            placeholder="Choose a File",
        )

        if selected_file:
            st.write("Extracting: ", selected_file)
            content_string = extract_document_content(selected_file)
            st.write(content_string)


def askaquestion():
    with st.container():
        st.header("Use a Snowflake Foundational LLM to Ask a Question")
        model_list = [
            "snowflake-arctic",
            "mistral-large",
            "mistral-large2",
            "reka-flash",
            "reka-core",
            "jamba-instruct",
            "jamba-1.5-mini",
            "jamba-1.5-large",
            "mixtral-8x7b",
            "llama2-70b-chat",
            "llama3-8b",
            "llama3-70b",
            "llama3.1-8b",
            "llama3.1-70b",
            "llama3.1-405b",
            "llama3.2-1b",
            "llama3.2-3b",
            "mistral-7b",
            "gemma-7b",
        ]
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        entered_code = st.text_area(
            "Paste the Data for Your Question",
            label_visibility="hidden",
            height=300,
            placeholder="Paste Data",
        )
        entered_code = entered_code.replace("'", "\\'")
        model_instruct = st.text_area(
            "Please provide Model Instructions",
            label_visibility="hidden",
            placeholder="Enter Prompt",
        )

        if st.button("Oh Great & Powerful LLM, Please provide Me a Wise answer!"):
            cortex_response = session.sql(
                f"select snowflake.cortex.complete('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as Answer",
            )
            st.caption("Answer:")
            st.dataframe(cortex_response, hide_index=True, width=1100)


def classify():
    with st.container():
        st.header("Classify Data With Snowflake Cortex")
        entered_text = st.text_area(
            "Enter data to Classify",
            label_visibility="hidden",
            height=400,
            placeholder="Enter data to classify",
        )
        entered_text = entered_text.replace("'", "\\'")

        if entered_text:
            cortex_response = session.sql(
                f"select snowflake.cortex.classify_text('{entered_text}',['Refund','Exchange','No Category']) as Answer",
            )
            st.caption("Classified data:")
            st.dataframe(cortex_response, hide_index=True, width=200)


def codeconvert():
    with st.container():
        st.header("Use a Snowflake Foundational LLM to Test Code Conversion")
        default_model_instruct = """Please convert this code for use in Snowflake SQL and validate that it will run in Snowflake:"""
        default_code_convert = """USE AdventureWorks2022;
                    GO

                    IF OBJECT_ID('dbo.NewProducts', 'U') IS NOT NULL
                    DROP TABLE dbo.NewProducts;
                    GO

                    ALTER DATABASE AdventureWorks2022 SET RECOVERY BULK_LOGGED;
                    GO

                    SELECT *
                    INTO dbo.NewProducts
                    FROM Production.Product
                    WHERE ListPrice > $25
                              AND ListPrice < $100;
                    GO

                    ALTER DATABASE AdventureWorks2022 SET RECOVERY FULL;
                    GO
                    """
        model_list = [
            "snowflake-arctic",
            "mistral-large",
            "mistral-large2",
            "reka-flash",
            "reka-core",
            "jamba-instruct",
            "jamba-1.5-mini",
            "jamba-1.5-large",
            "mixtral-8x7b",
            "llama2-70b-chat",
            "llama3-8b",
            "llama3-70b",
            "llama3.1-8b",
            "llama3.1-70b",
            "llama3.1-405b",
            "llama3.2-1b",
            "llama3.2-3b",
            "mistral-7b",
            "gemma-7b",
        ]
        selected_model = st.selectbox("Which Foundational Model:", model_list)
        entered_code = st.text_area(
            "Paste the Code You Would Like to Convert",
            default_code_convert,
            label_visibility="hidden",
            height=300,
            placeholder="Paste Code for Conversion",
        )
        entered_code = entered_code.replace("'", "\\'")
        model_instruct = st.text_area(
            "Please provide Model Instructions: ",
            default_model_instruct,
            label_visibility="hidden",
            placeholder="Enter Prompt",
        )

        if st.button("Run Conversion"):
            cortex_response = session.sql(
                f"select snowflake.cortex.complete('{selected_model}',concat('[INST]','{model_instruct}','{entered_code}','[/INST]')) as Answer",
            )
            st.caption("Converted Code:")
            st.dataframe(cortex_response, hide_index=True, width=1100)


page_names_to_funcs = {
    "Front Door": frontdoor,
    "Translate Call Summary": translate,
    "Sentiment Analysis": sentiment,
    "Summarize Call Data": summary,
    "Classify Call Data": classify,
    "Latest Call Summary": latest_call_summary,
    "Generate Customer E-Mail": emailcomplete,
    "Forecast Call Volume": forecast,
    "Parse Document": pdocument,
    "Test Converting Code": codeconvert,
    "Ask the LLM a ?": askaquestion,
}

selected_page = st.sidebar.selectbox("Select", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
