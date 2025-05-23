import os
import streamlit as st

st.write("현재 작업 디렉토리:", os.getcwd())
st.write("디렉토리 내 파일 목록:", os.listdir())
st.write("json 파일 존재 여부:", os.path.isfile('statistics-festival-178f7f9532ad.json'))
