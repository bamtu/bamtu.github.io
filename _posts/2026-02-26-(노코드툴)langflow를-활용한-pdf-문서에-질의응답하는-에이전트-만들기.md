---
layout: post
title:  "(노코드)LangFlow를 활용한 PDF 문서에 질의응답하는 에이전트 만들기"
date:   2026-02-26 11:27:34 +0900
categories: No-code
---

### Background
---
요새는 n8n이나 오늘 작성할 LangFlow같은 노코드 툴(No-code tool)이 인기가 있다.  그 툴들은 공통점이 있는데, 복잡한 코드를 작성하는 대신, node를 이용해서 pipeline을 시각화해서 데이터가 어떤 컴포넌트를 거쳐 순차적으로 실행되는지 확인이 가능하다는 것이다. 덕분에 개발자가 아니더라도 LLM 어플리케이션의 흐름을 이해하고 직접 구축해볼 수 있다. 

이번에는 LangFlow를 활용해 복잡한 코딩없이 내 PDF 문서 내용을 이해하고 답변해 주는 AI 에이전트를 만들어본 과정을 공유하려고 한다.


### 본론
---
LangFlow는 각 각 프로젝트를 flow라고 지칭한다. 이 Flow라는 캔버스 위에 우리가 필요한 기능들을 드래그 앤 드롭으로 배치하고 선으로 연결하면 애플리케이션이 완성된다. 내가 이번에 간단하게 만들었던 PDF file에 답변하는 에이전트는 LangFlow 공식 유튜브를 참고하여 다음과 같이 만들었다. 

![](/assets/2026-02-26-11-35-23.png)

이 워크플로우를 따라오면 LangChain과 같은 LLM Application Framework 에서 어떤 명령들이 순차적으로 실행되는지 대략적으로 알 수 있다. 

1. 문서로드(Load): PDF 파일을 읽어온다. 
2. 분할(Split): 긴 문서를 AI가 이해하기 쉬운 단위(Chunk)로 쪼갠다.
3. 임베딩 & 저장 (Embed & Store): 쪼개진 텍스트를 벡터(숫자)로 변환하여 검색 가능한 저장소(Vector Store)에 담는다.
4. 검색하여 가져오기 & 답변 (Retrieve & Generate): 사용자의 질문과 관련된 내용을 찾아내고, LLM이 이를 바탕으로 답변을 생성한다. 


데이터의 흐름은 보통 왼쪽에서 오른쪽으로 진행된다. 
배치된 컴포넌트들은 노드들로 이어져있다. 그럼 배치된 컴포넌트를 왼쪽부터 살펴보자. 

![](/assets/2026-02-26-11-53-09.png)

① 문서 로드 (Read File)
먼저 샘플의 PDF 파일(대한민국헌법전문)을 로드했다. 여기에 파일만 올려도 PDF파일의 텍스트를 읽고 노드로 넘겨준다. 여기에서 Output을 보고 싶으면, Raw Content옆의 확대기 아이콘을 누르면 Output을 볼 수 있다.

② 텍스트 분할 (Split Text & Text Input)
여기에서는 Chunk size와 Chunk Overlap은 디폴트 사이즈로 정했다. 이 사이즈는 간단한 개념이니 설명하지 않는다. Separator는 줄바꿈 문자를 따로 text input으로 넣어주었다. 

③ 한국어 특화 임베딩 (Embedding Model - Ollama)
 보통 OpenAI의 임베딩을 많이 쓰지만, 여기서는 Ollama를 연동했다. 내 경험상 Embedding 모델은 로컬로 충분히 해결할 수 있고(Vram 문제), 로컬이 훨씬 빨랐다. Ollama의 서버 포트와, 한국어 임베딩에서는 자주 사용하는 bge-m3-korean 모델을 선택하였다. 

④ 벡터 저장소 및 검색 (Chroma DB)
쪼개진 텍스트(Chunk)와 임베딩 모델은 Chroma DB로 모인다. Persist Directory는 이 DB의 폴더 경로를 나타내고, search query로는 Chat input을 넣어준다. chat input은 다음 순서로 볼 Prompt에 넣는다. 그리고 임베딩 모델을 연결해준다. 



앞서 작성한 순서가 데이터를 찾고 저장하는 과정이었다. 다음으로 그 오른쪽 과정을 보면 찾은 데이터를 바탕으로 답변을 생성하는 과정이다.  

![](/assets/2026-02-27-22-24-56.png)

⑤ Parser (데이터 가공)
가장 왼쪽의 Parser 노드는 앞서 검색된(Retrieved) 결과물을 받는다. 자세히보면 노드들의 처음과 마지막 부분의 색깔이 다르다. 어떤 것은 빨간색이고, 파란색, 초록색으로 구성되어있다. 이것은 데이터의 타입이다. 첫 부분이 파란색으로 되어있는 것을 빨간색 끝부분에 연결하려고하면, 연결이 되지않는다. 그러므로 Parser를 이용해서 데이터의 타입을 바꿔준다. 여기에서는 Vector Store에서 나온 데이터를 String으로 바꿔주는 역할을 한다.

⑥ Prompt Template (프롬프트 구성)
RAG의 품질을 결정하는 중요한 단계다. LLM에게 "그냥 답해"라고 하는 것이 아니라, "이 문서를 참고해서 답해"라고 지시하는 곳이다. template 구성은 다음과 같이 되어있다.

[문서 내용]
{context}

[질문]
{question}

여기에서 {context}에는 Vector store에서 가져온 내용의 chunk가 들어갈 것이고, {question}에는 내가 질문으로 작성한 내용이 들어간다. 그래서 이렇게 LLM의 입력으로 넣은다음에, model의 response를 chat output 컴포넌트와 연결하면 다음과 같다. 



![](/assets/2026-02-27-22-42-08.png)

완성되었다. 


### 결론
---
요새 많이 사용하는 노코드 LangFlow를 이용해 간단한 PDF에 대해 답변하는 언어모델을 만들어보았다. 


### 출처
---
LangFlow 공식 유튜브(www.youtube.com/@Langflow)
LangFlow 공식 홈페이지(langflow.org)