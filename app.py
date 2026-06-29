import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

st.set_page_config(page_title="맞춤형 여행 일정 플래너", page_icon="✈️", layout="wide")
st.title("✈️ 맞춤형 여행 일정 플래너")
st.write("목적지와 취향을 입력하면 최적의 숙소, 상세 타임라인, 이동 경로, 총 비용 요약이 포함된 완벽한 일정을 짜드립니다.")

# 기본 예시 질문에 웨이트 트레이닝 등의 구체적인 숙소 조건을 자연스럽게 추가했습니다.
default_query = "일본 도쿄 2박 3일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘. 그리고 매일 아침 웨이트 트레이닝을 할 수 있도록 피트니스 시설이 잘 갖춰진 숙소를 하나 추천해서 전체 일정의 베이스캠프로 삼아줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

if st.button("일정 생성하기"):
    with st.spinner("최신 정보를 검색하고 추천 숙소 및 상세 일정을 구성하는 중입니다... (약 20~30초 소요)"):
        try:
            llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
            search_tool = TavilySearchResults(max_results=5) 
            tools = [search_tool]
            
            agent_executor = create_react_agent(llm, tools)
            
            # 🔥 가이드라인 1번에 '추천 숙소' 섹션을 강력하게 지시했습니다.
            system_prompt = """당신은 최신 여행 정보를 검색하고 완벽한 타임라인을 기획하는 수석 여행 가이드입니다. 
            사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 아래 양식에 맞게 아주 상세하고 깔끔하게 답변을 작성하세요.
            
            [일정표 작성 가이드라인]
            1. 🏨 베이스캠프 추천 (숙소): 일자별 일정을 시작하기 전에 가장 먼저 '### 🏨 추천 숙소' 헤딩을 만들고, 사용자의 요구사항과 동선에 가장 잘 맞는 숙소 1~2곳을 제시하세요. (숙소명, 정확한 현지 주소, 1박 예상 비용, 구글 맵스 링크, 추천 이유를 반드시 포함할 것)
            
            2. 일자별 분리: 반드시 '### 1일차', '### 2일차' 처럼 마크다운 헤딩을 사용해 날짜별로 구역을 확실히 나누고, 각 일자마다 별도의 표(Table)를 생성하세요. 통짜로 하나의 표를 만들지 마세요.
            
            3. 표의 열(Column) 구성 및 필수 포함 사항:
               - 시간 : 구체적인 체류 시간대 (예: 10:00 ~ 11:30)
               - 일정(장소)명 및 활동 내용
               - 🚶‍♂️다음 장소 이동 : 추천 이동 수단 및 소요 시간 (예: 도보 10분, 또는 지하철 15분)
               - 정확한 현지 주소
               - 구글 맵스 링크 : 반드시 `[지도 보기](https://www.google.com/maps/search/?api=1&query=장소이름)` 형식으로 작성
               - 예상 소요 비용 : 현지 통화 및 원화 병기
               - 방문 꿀팁
               
            4. 💰 총 비용 및 일정 요약 (Summary):
               모든 일자별 표가 끝난 후, 맨 마지막에 '### 📝 여행 총합 요약' 섹션을 만드세요.
               전체적인 컨셉 요약과 함께, 전체 일정 동안 발생할 '총 예상 소요 비용(항공권, 숙박, 식비, 교통비, 기타 등등)'을 원화 단위로 한눈에 볼 수 있게 합산해서 적어주세요.
            """
            
            response = agent_executor.invoke({
                "messages": [
                    ("system", system_prompt),
                    ("user", user_input)
                ]
            })
            
            final_answer = response["messages"][-1].content
            
            st.success("숙소 추천과 상세 타임라인이 포함된 여행 일정이 완성되었습니다!")
            st.markdown(final_answer)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
