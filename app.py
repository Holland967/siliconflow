import streamlit as st

if "login_state" not in st.session_state:
    st.session_state.login_state = False
if "api" not in st.session_state:
    st.session_state.api = ""

def main():
    if not st.session_state.login_state:
        from note import regester, notes

        st.subheader("Interact with AI models through SiliconFlow API key", anchor=False)

        st.markdown(regester, unsafe_allow_html=True)

        api_key = st.text_input("API KEY", st.session_state.api, key="api_key", type="password", placeholder="sk-...")
        st.session_state.api = api_key
        submit_btn = st.button("Submit", key="submit_btn", type="primary", disabled=not api_key)

        st.markdown("---")

        with st.container(border=True, key="note_container"):
            st.markdown(notes, unsafe_allow_html=True)
        
        if submit_btn and st.session_state.api:
            st.session_state.login_state = True
            st.rerun()
        elif submit_btn and not st.session_state.api:
            st.error("Please enter your SiliconFlow API key!")
    else:
        siliconflow()

def siliconflow():
    function_list = ["General Chat", "Visual Chat", "Reasoning Chat", "Image Generation", "Audio to Text"]
    function_item = st.sidebar.selectbox("Function", function_list, index=0, key="func_")

    st.subheader(function_item, anchor=False)

    if function_item == "General Chat":
        from general_chat import generalChat
        generalChat(api_key=st.session_state.api)
    elif function_item == "Visual Chat":
        from visual_chat import visualChat
        visualChat(api_key=st.session_state.api)
    elif function_item == "Reasoning Chat":
        from reasoning_chat import reasoningChat
        reasoningChat(api_key=st.session_state.api)
    elif function_item == "Image Generation":
        from image_generation import imageGeneration
        imageGeneration(api_key=st.session_state.api)
    elif function_item == "Audio to Text":
        from audio_text import audioText
        audioText(api_key=st.session_state.api)
    
    st.sidebar.markdown("---")

    if st.sidebar.button("Log Out", key="logout_btn"):
        st.session_state.login_state = False
        st.session_state.api = ""
        st.rerun()

if __name__ == "__main__":
    main()
