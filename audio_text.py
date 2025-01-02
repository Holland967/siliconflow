from openai import OpenAI
import streamlit as st

def audio_transcription(api_key, audio_file):
    api_key = api_key
    base_url = "https://api.siliconflow.cn/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)

    transcription = client.audio.transcriptions.create(
        model="FunAudioLLM/SenseVoiceSmall",
        file=audio_file
    )

    return transcription

def audioText(api_key: str):
    if "uploaded_audio" not in st.session_state:
        st.session_state.uploaded_audio = None
    if "input_audio" not in st.session_state:
        st.session_state.input_audio = None
    
    if st.session_state.uploaded_audio == None and st.session_state.input_audio == None:
        disable = True
    elif st.session_state.uploaded_audio != None and st.session_state.input_audio == None:
        disable = False
    elif st.session_state.uploaded_audio == None and st.session_state.input_audio != None:
        disable = False
    
    audio_uploader = st.file_uploader("Upload an Audio", type=["MP3", "WAV"], key="audio_uploader", disabled=st.session_state.input_audio!=None)
    if audio_uploader is not None:
        st.session_state.uploaded_audio = audio_uploader
    elif audio_uploader is None:
        st.session_state.uploaded_audio = None
    audio_input = st.audio_input("Record an Audio", key="audio_input", disabled=st.session_state.uploaded_audio!=None)
    if audio_input is not None:
        st.session_state.input_audio = audio_input
    elif audio_input is None:
        st.session_state.input_audio = None
    
    transcript_btn = st.button("Transcript", "transcript_btn", type="primary")

    transcription_str = ""

    if transcript_btn:
        if st.session_state.uploaded_audio is not None and st.session_state.input_audio is None:
            try:
                with st.spinner("Processing..."):
                    transcription = audio_transcription(api_key, st.session_state.uploaded_audio)
                if transcription:
                    transcription_str = transcription.text
            except Exception as e:
                st.error(f"Error occured: {e}")
        elif st.session_state.uploaded_audio is None and st.session_state.input_audio is not None:
            try:
                with st.spinner("Processing..."):
                    transcription = audio_transcription(api_key, st.session_state.input_audio)
                if transcription:
                    transcription_str = transcription.text
            except Exception as e:
                st.error(f"Error occured: {e}")
        elif st.session_state.uploaded_audio is None and st.session_state.input_audio is None:
            st.info("Please upload an audio or record an audio!")
    
    if transcription_str:
        with st.container(border=True, key="trans_container"):
            st.markdown(transcription_str)
