import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# 금고(Secrets)에서 키를 자동으로 꺼내옵니다. 화면에 노출되지 않아 안전합니다!
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

st.set_page_config(page_title="원클릭 트립 어시스턴트", page_icon="✈️")
st.title("✈️ 원클릭 트립 어시스턴트")
st.write("목적지와 취향을 입력하면 최신 웹 검색을 통해 최적의 일정을 짜드립니다.")

default_query = "일본 도쿄 3박 4일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

if st.button("일정 생성하기"):
    with st.spinner("에이전트가 최신 정보를 검색하고 일정을 구성하는 중입니다... (약 10~20초 소요)"):
        try:
            llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
            search_tool = TavilySearchResults(max_results=3)
            tools = [search_tool]
            
            agent_executor = create_react_agent(llm, tools)
            system_prompt = "당신은 최신 여행 정보를 검색하고 완벽한 일정을 기획하는 수석 여행 가이드입니다. 사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 일자별 일정을 '마크다운 표(Table)' 형태로 깔끔하게 정리해서 답변하세요."
            
            response = agent_executor.invoke({
                "messages": [
                    ("system", system_prompt),
                    ("user", user_input)
                ]
            })
            
            final_answer = response["messages"][-1].content
            
            st.success("일정 생성이 완료되었습니다!")
            st.markdown("### 📋 추천 여행 일정")
            st.markdown(final_answer)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
