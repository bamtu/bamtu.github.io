---
layout: post
title:  "Human-In-The-Loop(HITL) 구현(LangGraph) - RAG활용 음악 태그 편집 에이전트(9)"
date:   2025-10-27 11:11:47 +0900
categories: AIagent
---


### Human-In-The-Loop 구현(LangGraph)
---

HITL 구현을 위해 LangChain으로 구현했던 음악 태그 편집 에이전트를 LangGraph의 Graph형식으로 노드와 엣지, state를 구현했다. 
![](/assets/2025-12-25-19-19-06.png)

가장 먼저 사용자의 입력 프롬프트를 받으면, retriever 노드에서 VectorStore에 접근해 입력 프롬프트에서 원하는 여러 개의 음원파일의 이름(ex: C:music_files/별 보러 갈래.mp3)을 가져온다. 다음으로 update_tool 노드에서는 Agent가 여러 개의 tool 중에 어떤 정보를 업데이트하는 funciton을 고를지 선택하고, 아래 화면처럼 Approve / Reject를 선택하게 만든다. _interrupt 옵션은 tool_executor노드를 실행하기 전에 interrupt를 준다는 의미이다. 

![](/assets/2025-12-25-19-19-16.png)

여기서 Approve를 선택하면 음원파일의 메타데이터를 업데이트하고 다음의 프롬프트 입력을 기다리게 된다. 입력 프롬프트가 명확하지 않을 경우, 예를 들어서 바꾸고 싶은 음원파일의 정보를 제대로 주지않았다거나 한다면, conditional edge의 오른쪽이 아닌 왼쪽으로 가서 바로 graph가 끝나게 된다.

LangGraph 구조
```python
flow = StateGraph(MessagesState)

# Add nodes
flow.add_node("retriever", retrieve_node)  # Start: search for files
flow.add_node("update_tool", tool_node)    # Decide which metadata update tool to use
flow.add_node("tool_executor", tool_executor)  # Execute tools after human approval

# Set entry point to retriever
flow.set_entry_point("retriever")

# retriever -> update_tool (always go to update_tool after retrieval)
flow.add_edge("retriever", "update_tool")

# Conditional routing from human_review
# After human approval, either execute tool or end
flow.add_conditional_edges(
    "update_tool",
    route_after_tool_choice,
    {
        "tool_executor": "tool_executor",
        "end": END
    }
)

# After tool execution, end the flow
flow.add_edge("tool_executor", END)

# 마지막으로, 컴파일함
app = flow.compile(interrupt_before=["tool_executor"])
```


### 노드 간의 정보 유지 - MessagesState
---

이 프로젝트에서는 MessagesState와 thread_id를 조합하여 노드 간 정보를 유지한다. 각 노드에서는 

retrieve_node (nodes.py:84-107)
```python 
def retrieve_node(state: MessagesState):
    messages = state["messages"]          # 1. State에서 읽기
    last_message = messages[-1]           # 2. 마지막 메시지 접근

    # 검색 로직...

    return {"messages": [AIMessage(content=result_message)]}  # 3. 새 메시지 추가
```
tool_node (nodes.py:110-126)
```python
def tool_node(state: MessagesState):
    messages = state["messages"]          # 1. 전체 대화 이력 읽기

    messages_with_system = [{"role": "system", "content": SYSTEM_MESSAGE}] + messages
    response = llm_with_tools.invoke(messages_with_system)  # 2. LLM에 전체 컨텍스트 전달     

    return {"messages": [response]}       # 3. LLM 응답 추가
```
route_after_tool_choice (nodes.py:128-139)
```python
def route_after_tool_choice(state: MessagesState) -> Literal["tool_executor", "end"]:
    messages = state["messages"]          # State 읽기
    last_message = messages[-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_executor"            # 조건부 라우팅 결정
```



정보의 흐름 예시는 다음과 같다.
```
[사용자 입력] "팝 장르 파일 찾아줘"
↓
State: {"messages": [HumanMessage("팝 장르 파일 찾아줘")]}
↓
[retrieve_node]
State: {"messages": [
    HumanMessage("팝 장르 파일 찾아줘"),
    AIMessage("검색된 파일들: file1.mp3, file2.mp3")  ← 추가
]}
↓
[사용자 입력] "artist를 BTS로 바꿔줘"
State: {"messages": [
    HumanMessage("팝 장르 파일 찾아줘"),
    AIMessage("검색된 파일들: file1.mp3, file2.mp3"),
    HumanMessage("artist를 BTS로 바꿔줘")  ← 추가
]}
↓
[tool_node] - LLM이 전체 대화 이력을 보고 파일과 작업 파악
State: {"messages": [
    ... (이전 메시지들),
    AIMessage(tool_calls=[{name: "batch_update_to_same_artist_tool",
                            args: {filepaths: [file1, file2], artist: "BTS"}}])  ← 추가
]}
↓
[interrupt - human approval]
↓
[tool_executor] - 실제 실행
State: {"messages": [
    ... (이전 메시지들),
    ToolMessage(content="2개 성공")  ← 추가
]}
```

이렇게 관리하여 다음 노드는 이 전의 노드의 응답까지 받을 수 있고, 매번 파일 경로를 명시해야하는 불편함에서 벗어날 수 있다.

### 결론
---

음악 태그 편집 에이전트를 LangGraph로 구현하여 HITL과 같은 기능을 추가할 수 있었다. 


전체 코드는 아래에서 확인할 수 있다.
https://github.com/bamtu/agent-for-audio-metadata_langG