import streamlit as st

st.title("Datyx")
st.caption("Empresa dedicada a la ciencia de datos")

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")