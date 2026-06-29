import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

st.set_page_config(page_title="맞춤형 여행 일정 플래너", page_icon="✈️", layout="wide")
st.title("✈️ 맞춤형 여행 일정 플래너")
st.write("목적지와 취향을 입력하면 주소, 상세 타임라인, 이동 경로, 총 비용 요약이 포함된 완벽한 일정을 짜드립니다.")

default_query = "일본 도쿄 3박 4일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

if st.button("일정 생성하기"):
    with st.spinner("최신 정보를 검색하고 이동 시간 및 총 비용을 계산하는 중입니다... (약 20~30초 소요)"):
        try:
            llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
            search_tool = TavilySearchResults(max_results=5) 
            tools = [search_tool]
            
            agent_executor = create_react_agent(llm, tools)
            
            # 🔥 일자별 표 분리 및 마지막 요약/총 비용 산출을 강력하게 지시합니다.
            system_prompt = """당신은 최신 여행 정보를 검색하고 완벽한 타임라인을 기획하는 수석 여행 가이드입니다. 
            사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 아래 양식에 맞게 아주 상세하고 깔끔하게 답변을 작성하세요.
            
            [일정표 작성 가이드라인]
            1. 일자별 분리: 반드시 '### 1일차', '### 2일차' 처럼 마크다운 헤딩을 사용해 날짜별로 구역을 확실히 나누고, 각 일자마다 별도의 표(Table)를 생성하세요. 통짜로 하나의 표를 만들지 마세요.
            2. 표의 열(Column) 구성 및 필수 포함 사항:
               - 시간 : 구체적인 체류 시간대 (예: 10:00 ~ 11:30)
               - 일정(장소)명 및 활동 내용
               - 🚶‍♂️다음 장소 이동 : 추천 이동 수단 및 소요 시간 (예: 도보 10분, 또는 지하철 15분)
               - 정확한 현지 주소
               - 구글 맵스 링크 : 반드시 `[지도 보기](https://www.google.com/maps/search/?api=1&query=장소이름)` 형식으로 작성
               - 예상 소요 비용 : 현지 통화 및 원화 병기
               - 방문 꿀팁
            3. 💰 총 비용 및 일정 요약 (Summary):
               모든 일자별 표가 끝난 후, 맨 마지막에 '### 📝 여행 총합 요약' 섹션을 만드세요.
               여기에는 여행의 전체적인 컨셉 요약과 함께, 전체 일정 동안 발생할 '총 예상 소요 비용(항공권, 숙박, 식비, 교통비, 기타 등등)'을 원화 단위로 한눈에 볼 수 있게 합산해서 적어주세요.
            """
            
            response = agent_executor.invoke({
                "messages": [
                    ("system", system_prompt),
                    ("user", user_input)
                ]
            })
            
            final_answer = response["messages"][-1].content
            
            st.success("일자별 상세 타임라인과 총 비용 요약이 완료되었습니다!")
            st.markdown("### 📋 추천 여행 일정표")
            st.markdown(final_answer)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
