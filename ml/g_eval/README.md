# 챗봇 응답 평가 실험 (G-EVAL & Human Evaluation)

## 개요

- 사용자 페르소나 유무에 따른 챗봇 응답의 유창성을 평가하고자 [한국어 MSC 데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)을 이용한 실험을 고안했습니다.

- 실험 과정의 전체적인 Flow는 [G-EVAL 논문](https://arxiv.org/abs/2303.16634)을 참고하였습니다.

- 실험 결과의 신뢰성을 더욱 높이기 위하여, 두 가지 실험을 진행했습니다.
    - GPT-4를 Evaluator로 사용한 G-EVAL
    - Human Evaluator 4명이 참가한 Human Evaluation


``` bash
├── Human_Eval_data.csv # 인간 평가자에게 제공된 데이터셋
├── README.md
├── cot # 사용된 CoT
│   ├── coherence.txt # 일관성
│   ├── coherence_KOR3.txt
│   ├── engagingness.txt # 참여도
│   ├── engagingness_KOR3.txt
│   ├── groundedness.txt # 근거성
│   ├── groundedness_KOR3.txt
│   ├── naturalness.txt # 자연스러움
│   └── naturalness_KOR3.txt
├── g_eval_calculate.ipynb # 최종 평가 결과 
├── g_eval_evaluate.ipynb # GPT-4를 통한 응답 평가
├── g_eval_make_cot.ipynb # GPT-4를 이용한 CoT 생성
├── g_eval_make_form.ipynb # 인간 평가를 위한 형식 제작
├── g_eval_model_prediction.ipynb # OPEN-SOLAR-KO-10.7B를 이용한 다음 턴 발화 생성
├── g_eval_preprocessing_msc_new.ipynb # 한국어 MSC 데이터셋 가공 과정
├── results # 평가 결과
│   ├── GEVAL_solar_vl2.json
│   └── GEVAL_solar_vl2_no_persona.json
├── scoring.py # 인간 평가를 위한 도구
└── utils.py # csv to json

```



## G-EVAL

### 평가 방법

1. [선행 논문](https://arxiv.org/abs/2210.07197)을 바탕으로 챗봇의 응답에 대해 총 4개의 metric에 대해 **1~5** 사이의 정수 값으로 평가를 진행

    - **일관성(coherence)** : 대화 기록과 사용자 페르소나를 보고 주어진 챗봇의 응답이 이전 대화의 유효한 연속인지 여부를 판단
    - **참여도(engagingness)** 주어진 챗봇의 응답이 흥미로운지 지루한지 판단
    - **근거성(groundedness)** 챗봇의 페르소나 문장이 주어졌을 때, 챗봇의 응답이 해당 페르소나에 기반하여 생성된 문장인지 판단
    - **자연스러움(naturalness)** 챗봇의 응답이 사람이 자연스럽게 할 수 있는 말과 같은지 판단


2. Metric을 설정한 이후, G-EVAL 논문에 따라서 GPT-4에 세부 평가 단계(이하 CoT) 설계를 요청
3. 생성된 CoT 중 문맥적으로 어색한 부분, 중복된 부분을 수정
    - CoT 생성 예시
        ```txt
        사용자와 챗봇 사이의 대화와 챗봇이 생성한 응답이 주어집니다. 이 지침을 주의 깊게 읽고, 응답을 평가하는 동안 이 문서를 열어 두었다가 필요할 때 참조하시기 바랍니다.

        평가 기준:
        일관성(1-5) 대화 기록을 고려할 때 일관성 있는 응답인가요? 주어진 챗봇의 응답이 이전 대화의 유효한 연속인지 여부를 판단합니다.

        세부 평가 단계:
        1. 대화의 내용을 읽고, 대화에 참여한 챗봇과 사용자의 발언, 그들이 논의하고 있는 주제에 주목하세요.
        2. 주어진 사용자 페르소나, 이전 대화를 기반으로 챗봇의 응답을 읽고 분석하세요.
        - 응답이 이전 대화에서 언급된 주제나 아이디어와 일치하는지 확인하십시오.
        - 응답이 사용자 페르소나 문장에서 언급된 성격 및 경험을 고려하고 있는지 확인하십시오.
        3. 이전 단계들을 바탕으로 일관성에 대한 최종 점수를 1-5의 범위에서 결정합니다.
        - 1점: 응답이 매우 일관성이 없음을 의미하며 대화의 어조나 주제와 일치하지 않는 경우
        - 3점: 응답이 어느 정도 일관성이 있음을 의미하며, 전체 대화에 어느 정도 부합하는 경우 
        - 5점: 응답이 매우 일관성이 있음을 의미하며, 대화의 주제와 어조를 모두 완벽하게 따르는 경우

        사용자 페르소나:
        {{user_persona}}

        챗봇 페르소나:
        {{bot_persona}}

        이전 대화:
        {{prev_dialog}}

        챗봇 응답:
        {{response}}

        평가 양식 (점수만 표시):
        - 일관성:
        ```

    - user_persona : 사용자의 발화를 통해 추출한 유저 페르소나 (페르소나 O 경우에만 존재)
    - bot_persona : [한국어 MSC 데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)에서 주어진 해당 speaker의 페르소나 문장
    - prev_dialog : 이전 5-turn의 대화
    - response : OPEN-SOLAR-KO 모델이 정보를 토대로 생성한 다음 턴 발화


4. [한국어 MSC 데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)에 주어진 발화와 페르소나 문장을 가공
    - 21개의 토픽 대화 중 각 토픽마다 3개씩 균등 추출
    - 학습된 페르소나 추출모델과 마찬가지로 [korean-style-converter-6b](https://huggingface.co/squarelike/korean-style-converter-6b)를 사용하여 발화를 반말로 변환
    - 사용자 페르소나 추출을 위해 **7-turn** 이상의 user_dialog가 존재하는 row만 추출
    - 페르소나가 추출된 총 **54개**의 row에 대해 실험 진행
    - 실제 챗봇 사용 환경과 동일하게 bot_persona, user_persona, prev_dialog (5-turn의 대화), new_input (사용자의 새 입력) 총 4개의 정보를 토대로 다음 턴 발화를 생성


5. 이 때 비교를 위해 동일한 모델 [beomi/OPEN-SOLAR-KO-10.7B](https://huggingface.co/beomi/OPEN-SOLAR-KO-10.7B)를 두고, 두 가지 세팅에서 다음 턴 발화를 생성
    * user_persona를 입력 받아 다음 턴 발화를 생성한 모델 (페르소나 O)
    * user_persona를 입력 받지 않고 다음 턴 발화를 생성한 모델 (페르소나 X)

6. 데이터, 모델의 예측 발화를 CoT input 부분에 추가

7. **GPT-4** api를 Evaluator로 사용 -> 6번에서 완성된 프롬프트를 토대로 4개의 평가지표에 대한 평가 수행
    - 총 **10번**의 응답을 추출하고, 출현 빈도에 따른 **가중합** 점수 계산
        
        > 원문에는 20번의 응답 추출 후 가중합을 계산했으나, 비용 이슈로 인하여 10번으로 축소
        
    - Json file에 각 응답의 평가 점수가 기록됨
    ```json
    // user persona O
    {
        "response": "정말? 그럼 나중에 우리 같이 동물의 숲 게임 하자",
        "user_persona": [
            "나는 체험 여행을 자주 간다",
            "나는 주말에 제주도로 여행을 간다",
            "나는 콘솔 게임을 한다"
        ],
        "bot_persona": [
            "나는 여자이다.",
            "나는 20대이다.",
            "나는 강아지에 관심이 없다.",
            "나는 사회복지학과 전공이다.",
            "나는 태블릿을 잘 활용한다."
        ],
        "prev_dialog": [
            "User:나는 오늘 약속이 없어서 게임이나 하려고. 너는?",
            "Bot:나도 게임하려고 했는데, 난 주로 콘솔 게임을 해.",
            "User:아 정말? 나도 콘솔 게임해. 어떤 게임해?",
            "Bot:나는 요즘 동물의 숲에 빠졌어. 너는?",
            "User:나랑 똑같네. 나도 동물의 숲을 하고 있어."
        ],
        "coherence": 5.0,
        "engagingness": 4.9,
        "naturalness": 5.0,
        "groundedness": 4.9
    },

    // user persona X
    {
        "response": "게임에 푹 빠졌구나. 나도 게임 얘기하니까 게임하고 싶다.",
        "user_persona": "",
        "bot_persona": [
            "나는 여자이다.",
            "나는 20대이다.",
            "나는 강아지에 관심이 없다.",
            "나는 사회복지학과 전공이다.",
            "나는 태블릿을 잘 활용한다."
        ],
        "prev_dialog": [
            "User:나는 오늘 약속이 없어서 게임이나 하려고. 너는?",
            "Bot:나도 게임하려고 했는데, 난 주로 콘솔 게임을 해.",
            "User:아 정말? 나도 콘솔 게임해. 어떤 게임해?",
            "Bot:나는 요즘 동물의 숲에 빠졌어. 너는?",
            "User:나랑 똑같네. 나도 동물의 숲을 하고 있어."
        ],
        "coherence": 4.9,
        "engagingness": 3.3,
        "naturalness": 4.3,
        "groundedness": 4.5
    },
    ```

## Human Evaluation

GPT-4가 평가한 것과 동일한 데이터를 제공하고, 4개 metric에 대한 평가를 진행했습니다. scorings.py를 통해 점수를 매기기 편리하게 만들었고, 각 평가자마다 csv 파일을 쉽게 산출할 수 있었습니다.


## Results

**54개**의 평가 row에 대해 4가지 metric score를 산술평균한 결과

### G-EVAL

||사용자 페르소나 O|사용자 페르소나 X|diff|
|---|---|---|---|
|일관성 (coherence)|4.35|4.12|0.23|
참여도 (engagingness)|3.33|3.19|0.14|
근거성 (groundedness)|4.34|4.00|0.34|
자연스러움 (naturalness)|3.63|3.46|0.17|


### Human Evaluation
||사용자 페르소나 O|사용자 페르소나 X|diff|
|---|---|---|---|
|일관성 (coherence)|3.85|3.73|0.12|
참여도 (engagingness)|4.01|3.85|0.16|
근거성 (groundedness)|3.06|2.87|0.19|
자연스러움 (naturalness)|4.15|3.84|0.31|

- ‘참여도’를 제외한 나머지 지표에서 두 모델 모두 전반적으로 GPT-4 evaluator보다 낮은 점수가 부여됨
- 추후 사용자 페르소나 추출 방식 변경, 더 많은 프롬프트 실험을 통해 발화 성능 개선 기대




## Reference
[1] [Towards a Unified Multi-Dimensional Evaluator for Text Generation](https://arxiv.org/abs/2210.07197)

[2] UniEval ([paper](https://arxiv.org/abs/2210.07197) | [github](https://github.com/maszhongming/UniEval))

[3] G-EVAL ([paper](https://arxiv.org/abs/2303.16634) | [github](https://github.com/nlpyang/geval))