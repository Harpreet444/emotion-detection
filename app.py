import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import speech_recognition as sr
import joblib

pipe_lr = joblib.load(open("text_emotion.pkl", "rb"))

emotions_emoji_dict = {"anger": "😠", "disgust": "🤮", "fear": "😨😱", "happy": "🤗", "joy": "😂", "neutral": "😐", 
                       "sad": "😔", "sadness": "😔", "shame": "😳", "surprise": "😮"}

def predict_emotions(docx):
    results = pipe_lr.predict([docx])
    return results[0]

def get_prediction_proba(docx):
    results = pipe_lr.predict_proba([docx])
    return results

def record_and_convert():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
        try:
            st.info("Recognizing...")
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Could not understand the audio")
        except sr.RequestError:
            st.error("Error with the Google API")
    return ""

def main():
    st.title("Text Emotion Detection")
    st.subheader("Detect Emotions In Text or Voice")

    option = st.selectbox("Choose Input Method", ("Type Text", "Record Voice"))

    if option == "Type Text":
        with st.form(key='my_form'):
            raw_text = st.text_area("Type Here")
            submit_text = st.form_submit_button(label='Submit')

        if submit_text:
            process_text(raw_text)

    elif option == "Record Voice":
        if st.button("Record"):
            raw_text = record_and_convert()
            if raw_text:
                st.write("Transcribed Text: ", raw_text)
                process_text(raw_text)

def process_text(raw_text):
    col1, col2 = st.columns(2)
    prediction = predict_emotions(raw_text)
    probability = get_prediction_proba(raw_text)

    with col1:
        st.success("Original Text")
        st.write(raw_text)

        st.success("Prediction")
        emoji_icon = emotions_emoji_dict[prediction]
        st.write(f"{prediction}:{emoji_icon}")
        st.write(f"Confidence: {np.max(probability)}")

    with col2:
        st.success("Prediction Probability")
        proba_df = pd.DataFrame(probability, columns=pipe_lr.classes_)
        proba_df_clean = proba_df.T.reset_index()
        proba_df_clean.columns = ["emotions", "probability"]
        fig = alt.Chart(proba_df_clean).mark_bar().encode(x='emotions', y='probability', color='emotions')
        st.altair_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
