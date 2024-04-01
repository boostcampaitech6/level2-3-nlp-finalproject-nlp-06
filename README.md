<p align="center">
  <img src="https://github.com/boostcampaitech6/level2-3-nlp-finalproject-nlp-06/assets/82081872/4755bea6-bf2a-4748-8325-4e132eb15369">
</p>

### <p align="center">찐친이 되어줘</p>
<p align="center"> '지우'는 대화를 통해 여러분이 어떤 사람인지를 점차 이해합니다</p>
<p align="center"> 매일 '지우'와 이야기하다 보면 어느새 오랜 친구가 되어있을 거에요</p> 
<p align="center"> 매일 밤 10시, 여러분의 소중한 하루를 기억하고 정리해주는 '지우'를 만나보세요!</p>
<br>

## 서비스 예시

https://github.com/boostcampaitech6/level2-3-nlp-finalproject-nlp-06/assets/82081872/aa6c124a-e417-45bf-8c64-5a28d6f354ef



## 팀원
|김재현|서동해|송민환|장수정|황예원|황재훈|
|:--:|:--:|:--:|:--:|:--:|:--:|
|![재현](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/fa007f29-007b-42c0-bb1a-f95176ad7d93)|![동해-PhotoRoom png-PhotoRoom](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/7ba86ba4-cd7a-4366-97aa-7669e7994a78)|![민환](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/a3614eb6-4757-4390-9196-f82a455b4418)|![수정](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/39b8b55c-d1d8-4125-bbf2-11a695bcbc23)|![예원-PhotoRoom png-PhotoRoom](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/46ab92c3-e6cc-455a-b9c3-a225c8730048)|![재훈-removebg-preview](https://github.com/boostcampaitech6/level2-klue-nlp-06/assets/82081872/5d8cf554-d59a-44fa-802d-38bd66111263)|
|[Github](https://github.com/finn-sharp)|[Github](https://github.com/DonghaeSuh)|[Github](https://github.com/codestudy25)|[Github](https://github.com/jo9392)|[Github](https://github.com/yeowonh)|[Github](https://github.com/iloveonsen)|
|[Mail](penguin-klg@jnu.ac.kr)|[Mail](donghaesuh2@gmail.com)|[Mail](meenham_song@naver.com)|[Mail](jo23892389@gmail.com)|[Mail](yeowonh@sju.ac.kr)|[Mail](mgs05144@gmail.com)|

### 역할
|이름|역할|
|:--:|:--:|
| **김재현(T6036)** | ```Front-End``` | 
| **서동해(T6077)** | ```팀장``` ```프로젝트 기획``` ```페르소나 추출 Baseline 모델링``` ```데이터 수집 및 라벨링``` ```LLM QLoRA fine-tuning```|
| **송민환(T6086)** | ```페르소나 추출``` ```데이터 수집 및 라벨링``` ```Human-Evaluation``` |
| **장수정(T6148)** | ```Prompt Engineering``` ```회고``` ```Human-Evaluation``` ```데이터 라벨링``` |
| **황예원(T6191)** | ```Prompt Engineering``` ```G-EVAL``` ```Model Quantization``` |
| **황재훈(T6193)** | ```Back-End``` ```Front-End``` ```서비스 아키텍처 구상``` ```배포``` ```Infrastructure```  |

## Overview
### 문제정의
- 1인 가구들이 꾸준히 증가하고 있고
- 이들이 겪는 외로움 문제가 사회적으로 큰 문제가 되어가고 있습니다.

- 일상 속 외로움에 관련한 인식 조사 결과 다음 **두 가지**가 주된 이유로 뽑혔습니다.
  - **친구가 없다**
  - **시간적 여유가 없다** 

### 서비스 기획
- 이들을 위한 **오랜 교감을 할 수 있는 친구가 되어줄 수 있고** 
- 스치듯이 지나가는 **하루를 정리할 시간을 제공**해줄 챗봇 서비스를 구상했습니다.

## 간편 구조도
![image](https://github.com/boostcampaitech6/level2-3-nlp-finalproject-nlp-06/assets/82081872/fabd52bd-bb02-4bb9-ad97-efdf58a777d0)
- **사용자의 발화**에서 지속적으로 **사용자의 페르소나를 추출**하여 페르소나 DB에 저장하고
- **입력과 유사한 사용자의 페르소나**가 DB 내에 존재하는 경우, top-K개를 불러와 **Prompt에 반영**
- **매일 밤 10시**, 사용자가 오늘 챗봇과 대화한 내용을 정리하여 **회고** 형태로 사용자에게 전달

## 서비스 아키텍처
![최종 구조도](https://github.com/boostcampaitech6/level2-3-nlp-finalproject-nlp-06/assets/82081872/afeb57a9-3480-4f84-b0c7-4a198e3b903f)

## 디테일
- ```페르소나 추출```에 관련한 자세한 내용은 다음 [링크](https://blog.naver.com/gypsi12/223396121146)에서 확인할 수 있습니다.
- ```회고``` 및 ```G-EVAL```, ```Prompt Engineering```, ```Back-End``` 등 자세한 내용은 다음 [Notion 페이지](https://boostcampait.notion.site/6-NLP-cad0911b71664946986a12e2e8064319?p=a94574983fb940a49c9f1fb9a4e98bbe&pm=c) 확인 할 수 있습니다.

## Reference
[1] [1인 가구 비율 (통계청, 2000-2022)](https://www.index.go.kr/unity/potal/indicator/IndexInfo.do?popup=Y&clasCd=2&idxCd=5065)\
[2] [서울연구원, 1인 가구 실태 조사 (2022)](https://www.si.re.kr/node/66227)\
[3] [트랜드모니터, 한국 사회의 외로움 문제 (2019)](https://trendmonitor.co.kr/tmweb/trend/allTrend/detail.do?bIdx=1803&code=0501&trendType=CKOREA)\
[4] [BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, 
Translation, and Comprehension](https://arxiv.org/abs/1910.13461)\
[5] [ET5 (ETRI)](https://aiopen.etri.re.kr/et5Model)\
[6] [SOLAR 10.7B: Scaling Large Language Models with Simple yet Effective Depth Up-Scaling](https://aiopen.etri.re.kr/et5Model)\
[6] [NEW 한국어 멀티세션 대화 (AI HUB)](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)
****
