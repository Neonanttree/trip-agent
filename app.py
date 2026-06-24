import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="원클릭 트립 어시스턴트", page_icon="✈️")
st.title("✈️ 원클릭 트립 어시스턴트")
st.write("목적지와 취향을 입력하면 최신 웹 검색을 통해 최적의 일정을 짜드립니다.")

# 2. 사이드바: API 키 입력란
with st.sidebar:
    st.header("🔑 API 키 입력")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")
    st.markdown("---")
    st.info("💡 API 키는 저장되지 않으며, 현재 창을 닫으면 사라집니다.")

# 3. 사용자 입력창
default_query = "일본 도쿄 3박 4일 일정 짜줘. 스시와 사시미가 맛있는 현지 맛집을 꼭 넣고, 저녁에 사진 찍으면서 산책하기 좋은 조용한 공원 방문 일정도 포함해줘."
user_input = st.text_area("어떤 여행을 떠나고 싶으신가요?", value=default_query, height=100)

# 4. 실행 버튼 및 에이전트 구동 로직
if st.button("일정 생성하기"):
    if not openai_api_key or not tavily_api_key:
        st.warning("👈 왼쪽 사이드바에 OpenAI와 Tavily API 키를 모두 입력해주세요!")
    else:
        with st.spinner("에이전트가 최신 정보를 검색하고 일정을 구성하는 중입니다... (약 10~20초 소요)"):
            try:
                # API 키 세팅
                os.environ["OPENAI_API_KEY"] = openai_api_key
                os.environ["TAVILY_API_KEY"] = tavily_api_key
                
                # LLM 및 검색 도구 설정
                llm = ChatOpenAI(temperature=0.2, model="gpt-4o")
                search_tool = TavilySearchResults(max_results=3)
                tools = [search_tool]
                
                # 오류의 원인이었던 부분 제거: 아주 심플하게 에이전트 조립
                agent_executor = create_react_agent(llm, tools)
                
                # 시스템 프롬프트(역할 부여)
                system_prompt = "당신은 최신 여행 정보를 검색하고 완벽한 일정을 기획하는 수석 여행 가이드입니다. 사용자의 요청을 분석하고 도구를 사용해 최신 정보를 찾은 뒤, 일자별 일정을 '마크다운 표(Table)' 형태로 깔끔하게 정리해서 답변하세요."
                
                # 일을 시킬 때(invoke) 역할과 질문을 리스트로 한 번에 전달 (버전 무관 100% 호환 방식)
                response = agent_executor.invoke({
                    "messages": [
                        ("system", system_prompt),
                        ("user", user_input)
                    ]
                })
                
                # 결과 도출
                final_answer = response["messages"][-1].content
                
                # 화면에 결과 출력
                st.success("일정 생성이 완료되었습니다!")
                st.markdown("### 📋 추천 여행 일정")
                st.markdown(final_answer)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")