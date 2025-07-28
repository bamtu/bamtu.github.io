---
layout: post
title:  "프로젝트 1 - RAG활용 음악 태그 편집 에이전트 (7) - AgentExecutor"
date:   2025-07-28 22:28:47 +0900
categories: AIagent
---

### AgentExecutor를 이용한 Agent
---

Langchain 프레임워크를 사용해서 개발을 할 때, Chain을 주로 사용한다. 

![](/assets/202507Mo224212.png)

Chain은 LangChain에서 제공되는 python 클래스인데, 복잡한 파이프라인을 만들기 위해 결합될 수 있다. 하지만 나는 음악 태그 편집 에이전트를 개발할 때, LCEL을 사용해 Chain을 사용하는 등의 과정을 거치지않고, AgentExecutor라는 framework를 사용하였다. 

```python
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

Chain대신에 AgentExecutor를 사용하면 여러 이점이 있다. Chain은 실행 순서가 LCEL등으로 서술하여 코드 내에 미리 정의되어있지만 AgentExecutor는 Chain의 일종으로, 결정 기반(action-driven) 동적인 루프 실행 흐름을 가진 체인이다. 

따라서 Agent가 필요에 따라 특정 툴을 선택, 호출하고, 동적인 의사 결정을 한다. 참고 웹에서는 reasoning-action-observation loop를 스스로 에이전트가 조직한다고 나와있다. Chain과 비교하면 Chain은 단일 요청-응답에 적합하고, AgentExecutor는 조건에 따라 툴 호출, 반복 실행이 필요한 상황에 적합하다. 하지만 AgentExecutor는 latency가 길고, token 비용이 높다는 단점이 있다.

reasoning: 에이전트는 사용자 입력을 분석하여 작업을 결정하고 필요한 단계를 식별한다. 
action: 추론 결과를 바탕으로 에이전트는 가장 적절한 도구를 선택하고 실행한다.
observation: 에이전트는 도구에서 생성된 출력을 처리하고 이를 추론 과정에 다시 통합하여 추가로 정교화한다.


### 참고
---
https://www.geeky-gadgets.com/langchain-agent-executor-framework/?utm_source=chatgpt.com
https://rudaks.tistory.com/entry/LangChain-%EC%B2%B4%EC%9D%B8Chain%EC%9D%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80