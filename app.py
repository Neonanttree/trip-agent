import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

st.set_page_config(page_title="맞춤형 여행 일정 플래너", page_icon="✈️", layout="wide")
st.title("✈️ 맞춤형 여행 일정 플래너")
st.write("목적지와 취향을 입력하면 주소, 상세 타임라인, 이동 경로, 비용이 포함된 완벽한 일정을 짜드립니다.")

default_query = "일본 도쿄 3박 4일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

if st.button("일정 생성하기"):
    with st.spinner("최신 정보를 검색하고 이동 시간까지 고려한 타임라인을 구성 중입니다... (약 20~30초 소요)"):
        try:
            llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
            search_tool = TavilySearchResults(max_results=5) 
            tools = [search_tool]
            
            agent_executor = create_react_agent(llm, tools)
            
            # 🔥 다음 장소까지의 '이동 방법과 시간'을 필수 열(Column)로 추가했습니다.
            system_prompt = """당신은 최신 여행 정보를 검색하고 완벽한 타임라인을 기획하는 수석 여행 가이드입니다. 
            사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 일자별 일정을 '마크다운 표(Table)' 형태로 아주 상세하고 깔끔하게 정리하세요.
            특히, 장소와 장소 사이의 현실적인 이동 수단과 소요 시간을 반드시 구글 지도 등을 기반으로 검색하여 반영해야 합니다.
            
            [표 작성 시 열(Column) 구성 및 필수 포함 사항]
            1. 일자 및 시간 : 구체적인 체류 시간대 (예: 10:00 ~ 11:30)
            2. 일정(장소)명 및 활동 내용
            3. 🚶‍♂️다음 장소 이동 : 다음 목적지까지의 추천 이동 수단 및 예상 소요 시간 (예: 도보 10분, 또는 지하철 긴자선 약 15분)
            4. 정확한 현지 주소
            5. 구글 맵스 링크 : 반드시 `[지도 보기](https://www.google.com/maps/search/?api=1&query=정확한+장소+이름)` 형식으로 작성
            6. 예상 소요 비용 : (현지 통화 및 원화 병기)
            7. 방문 꿀팁
            """
            
            response = agent_executor.invoke({
                "messages": [
                    ("system", system_prompt),
                    ("user", user_input)
                ]
            })
            
            final_answer = response["messages"][-1].content
            
            st.success("상세한 이동 경로가 포함된 여행 일정이 완성되었습니다!")
            st.markdown("### 📋 추천 여행 일정표")
            st.markdown(final_answer)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
