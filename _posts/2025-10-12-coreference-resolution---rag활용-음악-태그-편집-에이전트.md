---
layout: post
title:  "Coreference resolution - RAG활용 음악 태그 편집 에이전트(8)"
date:   2025-10-12 19:41:59 +0900
categories: AIagent
---

### Coreference resolution
---

과거 포스트 [multi-turn conversation 대응 - RAG활용 음악 태그 편집 에이전트 (4)](https://bamtu.github.io/2025/06/02/)에서 이런 예를 들면서 multi-turn conversation을 설명했다.

위의 포스트에서는 벡터 스토어를 업데이트함으로써 해결하였다. 여기서 LangChain에서 제공하는 Memory를 이용하면 대화내용을 저장하여 다음 대화에서 응답을 할 때 사용해 더 풍부한 응답을 제공할 수 있다. 
메모리를 이용하지 않는다면, stateless라고 볼 수 있다.


```
User: 이순신이 누구야?
AI: 조선시대의 장군으로, 임진왜란 당시 활약했어요.

User: 그 사람이 한산도 대첩에서 한 일은?
AI: 한산도 대첩에서 학익진 전술을 사용해 일본 수군을 크게 무찔렀어요.
```

여기에서 '그 사람'이 이순신을 가리킨다는 것을 파악하는 것이 Coreference Resolution이다. 이를 통해서 LLM은 텍스트의 맥락을 정확하게 해석한다. 

메모리를 위해서는 프롬프트에 과거 conversation을 담아 전달한다는 것을 직관적으로 떠올릴 수 있다.

```
"Given the {past_conversation} answer my question"
Past Conversation:
User 1: Hi. I like to drink Cold Brew Coffee, where can i find this?
Bot 1: You can find cold breed coffee at Starbucks
...

Qustion: Where Can I ....
```

하지만 입력 토큰의 수는 제한되어있다. 과거의 대화가 길어진다면 분명 답변의 시간이 오래걸리는 등의 문제가 발생한다. 그래서 Langchain에서는 세가지의 방법을 취한다.

```
- 이전 메시지들을 그대로 LLM에 전달(구현이 간단)
- 더 오래된 메시지들을 없애서 최근의 메시지를 위주로 전달
- 메시지들을 요약하는 방법으로 토큰의 수를 줄여 LLM에게 전달 
```

### 두번째 방법 (최근의 메시지 위주 전달)
---
LangChain v0.3 이상에서는 LangGraph 기반의 상태 저장(persistence)을 추천하고 있고, MemorySaver 같은 체크포인터를 통해 상태를 보존하게 할 수 있다.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage

workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    system_prompt = "You are a helpful assistant. Answer all questions well."
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": response}

workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```
이렇게 하면, app.invoke(...)를 할 때마다 MemorySaver가 대화 상태를 저장하고 관리해준다.


### 세번째 방법 (메시지 요약 전달)
---
```python
from langchain_core.messages import trim_messages
# 각 메시지를 1 '토큰'으로 센다. 그래서 아래 코드는 마지막 2메시지만 남긴다.
trimmer = trim_messages(strategy="last", max_tokens=2, token_counter=len)
```
이 trimmer를 적용하면 지정된 수만큼 최근 메시지들만 남기고 나머지는 없애버리도록 처리가 가능하다.

### 정리
---
Langchain에서는 여러가지 Memory(이전 대화 저장)을 유지시키는 방법을 제안한다. 


### 출처
---
https://python.langchain.com/docs/how_to/chatbots_memory/
Eden Marco Udemy 강의