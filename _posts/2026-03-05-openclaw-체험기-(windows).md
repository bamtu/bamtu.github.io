---
layout: post
title:  "openclaw 체험기 (Windows)  - browser control"
date:   2026-03-05 15:53:32 +0900
categories: openclaw
---

### Background
---
요즘 자동화 부분에서 OpenClaw가 핫하다. OpenClaw를 안쓰는 컴퓨터(Windows, WSL2 사용X)에 설치하여 웹 브라우저를 제어시키게 하는 것까지 체험해보았다. 이 글에서는 Windows에 OpenClaw를 설치하고 웹 브라우저도 에이전트가 제어할 수 있게 만드는 과정까지 소개한다. 

### 설치
---

```
Node.js 설치 -> Git 설치 -> OpenClaw 설치
```

OpenClaw를 설치하려면 일단 node.js가 필요하다. 

https://nodejs.org/ko/download 

에서 LTS 버전을 다운받고, 설치한다.(Add to PATH 체크 필수, default로 되어있다.) 

아래 필요한 툴들도 설치하는 옵션을 체크해주었다. 

![](/assets/2026-03-05-16-05-47.png)

그 다음으로는 git을 설치한다. -> https://git-scm.com/install/windows

그리고나서 openclaw를 설치한다.

윈도우에서는 PowerShell(관리자 권한)을 이용하여 설치한다. 먼저,
```bash
node -v
```
위의 명령어를 이용하여 node.js가 잘 설치되었는지 확인한 후에 다음 명령어를 입력하여 설치한다. 

```bash
iwr -useb https://openclaw.ai/install.ps1 | iex
```
이렇게 하면 node.js 어쩌구 에러가 날 수도 있다. 권한 때문이니 꼭 사용하지 않는, 예민한 정보가 없는 컴퓨터에서 이렇게 설치하도록하고, 권한을 풀어주는 명령어를 찾아 입력한 후에, 위의 명령어로 설치해주면 된다. 


### LLM과 연결
---
이제 호출하는 LLM과 연결해야한다. 주의해야할 점은 구독제(claude pro같은)로 사용하는 LLM은 여기서 사용이 아마 불가능하다. 소문으로는 Github의 gpt-5 mini 모델을 사용하면 무제한으로 사용할 수 있다고 한다.(26/03/05 기준)Openai API 혹은 gemini API를 구글에 검색하여 API키를 발급해주는 곳에서 API키를 얻을 수 있다.

설치하면 시작 세팅에서도 추가할 수 있고, 나중에도 OpenClaw configure에 접근할 수 있다. OpenClaw configure에 접근하려면 powershell에서 
```bash
openclaw config
```
를 입력하면 openclaw 설정이 뜬다. 여기서 Model에서 Provider를 선택하고,API키를 입력하고, 모델을 선택해주면 된다. 

![](/assets/2026-03-05-16-29-28.png)


### 텔레그램과 연결
---
텔레그램(OpenClaw에서는 Channel이라고 한다.)과 연결하면 텔레그램을 이용해서 내 봇과 대화할 수 있다. 내 봇은 OpenClaw의 Agent가 된다. 그래서 텔레그램으로 OpenClaw 에이전트에게 명령을 내릴 수 있다. 

먼저 봇을 만들어야한다. @BotFather에게 메시지를 보낸다. 텔레그램 메시지로 
```bash
/start
```
을 입력하고 보내면, BotFather가 봇을 만드는 것을 도와준다. 그 다음으로,

```bash
/newbot
```

을 입력한 후, 봇 이름을 정하면 API 접근을 위한 token이 발행된다. 이 토큰을 알아두었다가, openclaw 설정-channel에 붙여넣으면 된다. 그리고 그 다음으로 텔레그램과 연결하려면 pairing setting도 해주어야 한다.

텔레그램에서 내가 만든 봇을 검색하여 추가한다음에, 다음과 같이 메시지를 보낸다. 

```bash
/start
```

그러면 pairing code를 말해주는데 다시 powershell로 돌아가 

```bash
openclaw pairing approve telegram <페어링코드>
```
입력해주고 그 후로 메시지를 보내면 내 OpenClaw 봇과 대화할 수 있다. user id값은 나밖에 대화한 사람이 없어서 사용하지 않았다. 


### UI 접근
---
OpenClaw 대시보드로 들어가고 싶다면, 게이트웨이 토큰을 알아내야한다. 알아낸 게이트웨이 토큰을 그림과 같이 대시보드의 Overview의 Gateway Access 부분에 넣어준다. 그렇게되면 우측 상단의 Health가 초록색, OK가 된다.

![](/assets/2026-03-05-16-55-05.png)



### 웹 브라우저를 제어하기위한 세팅 
---
이후 버전에서는 필요없을 수도 있지만, 나의 경우 웹 브라우저 제어가 안되었다. 그래서 다음의 설정을 바꿔주어야만 웹 브라우저 제어를 할 수 있었는데(이것 때문에 6시간 헤맴), Settings -> Config -> Tools에서 Tool Profile이 messaging으로 되어있었는데 이것을 full로 바꿔주는 것이다. 이 문제를 해결한 후에 웹 브라우저 제어가 정상적으로 가능했다.  

![](/assets/2026-03-05-16-56-28.png)


그 이후에 정상적으로 검색이 되었다. 

![](/assets/2026-03-05-17-01-14.png)

### 여담
---

웹 브라우저를 제어하게 만드는데 어마어마하게 많은 토큰 비용이 들었다. 

![](/assets/2026-03-05-17-02-47.png)

gpt-5-mini 기준으로 2번 간단한 일을 요청하고 Usage를 확인했더니 0.85 달러가 지출되었다. 간단한 검색같은 경우, web search(tool) API를 따로 받아서 사용하는게 비용을 줄이는 방법이 될 것이다. 혹은 앞에서 설명한 Github copilot을 구독해서 gpt mini 버전을 무제한으로 이용하는 것도 좋은 방법이 될 것이다. 


### 결론
---
간단하게 OpenClaw를 사용해서 Agent에게 웹 브라우징을 시켜보았다. 

