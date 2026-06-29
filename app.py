import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# 금고(Secrets)에서 키 자동 로드
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# 타이틀 및 설명 업그레이드
st.set_page_config(page_title="원클릭 트립 어시스턴트 PRO", page_icon="✈️", layout="wide")
st.title("✈️ 원클릭 트립 어시스턴트 PRO")
st.write("목적지와 취향을 입력하면 주소, 예상 비용, 지도 링크가 포함된 완벽한 실전용 일정을 짜드립니다.")

default_query = "일본 도쿄 3박 4일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

if st.button("실전 일정 생성하기"):
    with st.spinner("최신 정보를 검색하고 고도화된 일정을 구성하는 중입니다... (약 15~30초 소요)"):
        try:
            llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
            search_tool = TavilySearchResults(max_results=4) # 검색량 소폭 증가
            tools = [search_tool]
            
            agent_executor = create_react_agent(llm, tools)
            
            # 🔥 여기가 핵심입니다! AI에게 요구사항을 아주 구체적으로 지시합니다.
            system_prompt = """당신은 최신 여행 정보를 검색하고 완벽한 일정을 기획하는 수석 여행 가이드입니다. 
            사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 일자별 일정을 '마크다운 표(Table)' 형태로 깔끔하게 정리하세요.
            
            [표 작성 시 필수 포함 사항]
            1. 시간 및 일정(장소)명
            2. 정확한 현지 주소
            3. 구글 맵스 링크 (반드시 `[지도 보기](https://www.google.com/maps/search/?api=1&query=정확한+장소+이름)` 형식으로 작성할 것)
            4. 예상 소요 비용 (교통비, 식비, 입장료 등 대략적인 금액을 현지 통화 및 원화로 병기)
            5. 방문 시 꿀팁 또는 추천 이유
            """
            
            response = agent_executor.invoke({
                "messages": [
                    ("system", system_prompt),
                    ("user", user_input)
                ]
            })
            
            final_answer = response["messages"][-1].content
            
            st.success("세련된 여행 일정이 완성되었습니다!")
            st.markdown("### 📋 추천 여행 일정 (Pro Ver.)")
            st.markdown(final_answer)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
