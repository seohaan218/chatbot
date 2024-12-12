import streamlit as st
import pandas as pd
from openai import OpenAI

# Load dataset
file_path = 'OIL_PRICE_OF_SEOUL_KOREA_DATASET.csv'  # 데이터셋 경로 수정 필요
oil_price_data = pd.read_csv(file_path)

# GPT API 설정
openai_api_key = ""  # OpenAI API 키를 입력하세요
client = OpenAI(api_key=openai_api_key)

# Streamlit 설정
st.set_page_config(page_title="서울 주유소 추천 챗봇", layout="wide")

st.title("서울 주유소 추천 챗봇")
st.write("대화를 통해 서울 내 적합한 주유소를 추천해드립니다.")

# Step 1: 가격 한도 설정
st.header("1. 가격 설정")
price_limit = st.slider(
    "리터당 최대 휘발유 가격을 설정하세요 (100원 단위)", 
    min_value=1000, 
    max_value=2300, 
    step=100, 
    value=1800
)

# Step 2: 위치 입력
st.header("2. 현재 위치")
user_location = st.text_input("현재 위치를 입력하세요 (예: 서울 강남구)")

# Step 3: 추가 요구 사항 입력
st.header("3. 추가 요구 사항")
additional_requirements = st.text_area(
    "추가 조건을 입력하세요 (예: 세차 가능, 24시간 운영, 특정 브랜드 등)"
)

# GPT 메시지 생성 및 RAG 처리
if st.button("주유소 추천 받기"):
    # GPT에 보낼 메시지 생성
    system_message = "서울 지역 주유소를 추천하는 챗봇입니다. 사용자 요청을 분석하여 적합한 주유소를 추천하세요."
    user_message = f"""
    사용자 요청: 
    - 리터당 최대 가격: {price_limit}원
    - 위치: {user_location}
    - 추가 요구 사항: {additional_requirements if additional_requirements else '없음'}
    """

    # GPT API 호출 (Streaming 방식)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )

    # Streamlit에서 실시간으로 GPT 응답 표시
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    # RAG: 데이터 필터링
filtered_data = oil_price_data[oil_price_data["Price of gasoline"] <= price_limit]
if user_location:
    filtered_data = filtered_data[filtered_data["Address"].str.contains(user_location)]

if additional_requirements:
    if "세차" in additional_requirements:
        filtered_data = filtered_data[filtered_data["Car Wash"] == True]
    if "24시간" in additional_requirements:
        filtered_data = filtered_data[filtered_data["24h open"] == True]
    if "셀프" in additional_requirements:
        filtered_data = filtered_data[filtered_data["Self"] == True]
    if "SK" in additional_requirements:
        filtered_data = filtered_data[filtered_data["Brand"].str.contains("SK")]
    if "GS" in additional_requirements:
        filtered_data = filtered_data[filtered_data["Brand"].str.contains("GS")]

# 열 이름 변경 (Latitude -> latitude, Longitude -> longitude)
filtered_data = filtered_data.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})

# 추천 결과 출력
if not filtered_data.empty:
    st.subheader("추천 결과")
    st.map(filtered_data[["latitude", "longitude"]])  # 수정된 열 이름 사용
    st.dataframe(filtered_data[["Name", "Address", "Brand", "Price of gasoline", "Car Wash", "24h open"]])
else:
    st.warning("조건에 맞는 주유소를 찾을 수 없습니다. 조건을 변경해보세요!")
