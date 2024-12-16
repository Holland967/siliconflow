from bs4 import BeautifulSoup
import streamlit as st
import requests
import re

# Fetch 微信公众号文章，返回纯文本
def fetch_wx(url: str) -> str:
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取文章标题
    title = soup.find('h1', id='activity-name').get_text(strip=True)
    
    # 获取文章内容
    article = soup.find('div', class_='rich_media_content')
    if article:
        # 去除空格、空行和换行符
        article_text = article.get_text(separator=' ')
        article_text = ' '.join(article_text.split())
    else:
        article_text = ''
    
    return f"{title}\n\n{article_text}"

def is_url(string):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(regex.match(string))

def fetch_chatting(api_key: str, base_url: str):
    from chat_completion import ChatCompletion
    from template import article_summarization

    system_prompt: str = article_summarization
    model: str = "Qwen/Qwen2.5-72B-Instruct-128K"
    max_tokens: int = 4096
    temperature: float = 0.80
    top_p: float = 0.90
    frequency_penalty: float = 0.00
    presence_penalty: float = 0.00

    chat = ChatCompletion(api_key=api_key, base_url=base_url)

    if "article" not in st.session_state:
        st.session_state.article = ""

    if "user_msg" not in st.session_state:
        st.session_state.user_msg = []
    
    if "msg_cache" not in st.session_state:
        st.session_state.msg_cache = []
    
    with st.sidebar:
        reset_btn: bool = st.button("Reset", "reset_btn", type="primary", use_container_width=True)
    
    if st.session_state.article != "":
        with st.expander("Article", False):
            st.markdown(st.session_state.article)
    
    for i in st.session_state.msg_cache:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="summarization_query"):
        if st.session_state.user_msg == []:
            if not is_url(query):
                st.warning("Please input a url please!")
            elif is_url(query):
                st.session_state.article = fetch_wx(query)
                with st.expander("Article", False):
                    st.markdown(st.session_state.article)
                messages: list = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": st.session_state.article}]
                with st.chat_message("assistant"):
                    response = chat.chat_completions(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
                    result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.user_msg.append({"role": "assistant", "content": result})
                st.session_state.msg_cache = st.session_state.user_msg
                st.rerun()
        elif st.session_state.user_msg != []:
            st.session_state.user_msg.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            messages: list = [
                {"role": "system", "content": article_summarization},
                {"role": "user", "content": st.session_state.article}] + st.session_state.user_msg
            with st.chat_message("assistant"):
                response = chat.chat_completions(model, messages, max_tokens, temperature, top_p)
                result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.user_msg.append({"role": "assistant", "content": result})
            st.session_state.msg_cache = st.session_state.user_msg
            st.rerun()
    
    if reset_btn:
        st.session_state.article = ""
        st.session_state.user_msg = []
        st.session_state.msg_cache = []
        st.rerun()
