import pandas as pd

data = pd.read_csv('./Human_Eval_data.csv')
data['prev_dialog'] = data['prev_dialog'].apply(lambda x: eval(x))
data['prev_dialog'] = data['prev_dialog'].apply(lambda x: '\n'.join(x))

evaluate_df = pd.DataFrame(columns=['coherence_persona', 'engagingness_persona', 'groundedness_persona', 'naturalness_persona',
                                    'coherence_no_persona', 'engagingness_no_persona', 'groundedness_no_persona', 'naturalness_no_persona'])

metric_dict = {'일관성' : "주어진 챗봇의 응답이 이전 대화의 유효한 연속인지, **사용자 페르소나**를 제대로 반영하고 있는지 여부를 판단합니다.",
               '참여도' : "주어진 챗봇의 응답이 흥미로운지 지루한지, 사용자의 흥미를 유발하는지 평가합니다.",
               '근거성' : "챗봇의 페르소나 문장이 주어졌을 때, 챗봇의 응답이 **챗봇 본인의 페르소나**에 기반하여 생성된 문장인지 판단합니다.",
               '자연스러움' : "챗봇의 응답이 문법적으로 틀린 부분은 없는지, 사람이 자연스럽게 할 수 있는 말과 같은지 판단합니다."}

for idx in range(len(data)):
    print('====================================================================')
    print(f'현재 : {idx}/{len(data)} | 진행률 : {idx/len(data):.2%}')
    print('주어진 이전 5-turn 대화, 이전 대화로부터 추출된 사용자 페르소나, 챗봇 페르소나를 보고 아래 평가 지표에 대해 평가해주세요. 모든 평가점수는 1-5 사이의 정수 값으로 기입합니다.')
    print('\n------- 각 평가 지표에 대한 설명 -------')
    for name, desc in metric_dict.items():
        print(f"- {name} : {desc}")
    print('\n---------- 이전 대화로부터 추출된 사용자 페르소나 -------------')
    print(data.loc[idx, 'user_persona_predict'])
    print('\n---------- 챗봇 페르소나 ------------')
    print(data.loc[idx, 'bot_persona'])
    print('\n---------- 이전 5-turn의 대화 ----------')
    print(data.loc[idx, 'prev_dialog'])
    print('====================================================================')

    print("\n공백을 두고 각 응답에 대한 [일관성 참여도 근거성 자연스러움] 점수를 1-5 사이의 정수 값으로 기입해주세요.")
    print('## 입력 예시 : 5 2 1 3 / 1 1 1 5 / 5 5 5 5')
    print('\n[응답 1] : ', data.loc[idx, 'response_persona'])
    
    while True:
        try:
            dialog_score = [int(u) for u in input().split()]
            if len([x for x in dialog_score if x > 5 or x < 1]) >= 1:
                print("ERROR: 1 미만 혹은 5 초과 값이 입력되었습니다. 다시 입력해주세요.")
                continue
            evaluate_df.at[idx,'coherence_persona'] = dialog_score[0]
            evaluate_df.at[idx,'engagingness_persona'] = dialog_score[1]
            evaluate_df.at[idx,'groundedness_persona'] = dialog_score[2]
            evaluate_df.at[idx,'naturalness_persona'] = dialog_score[3]
            break
        except:
            print("ERROR: 잘못된 입력입니다. 다시 입력해주세요.")
            continue
    
    print('[응답 2] : ', data.loc[idx, 'response_no_persona'])
    while True:
        try:
            dialog_score = [int(u) for u in input().split()]
            if len([x for x in dialog_score if x > 5 or x < 1]) >= 1:
                print("ERROR: 1 미만 혹은 5 초과 값이 입력되었습니다.  다시 입력해주세요.")
                continue
            evaluate_df.at[idx,'coherence_no_persona'] = dialog_score[0]
            evaluate_df.at[idx,'engagingness_no_persona'] = dialog_score[1]
            evaluate_df.at[idx,'groundedness_no_persona'] = dialog_score[2]
            evaluate_df.at[idx,'naturalness_no_persona'] = dialog_score[3]
            break
        except:
            print("ERROR: 잘못된 입력입니다. 다시 입력해주세요.")
            continue
        
name = input('이름을 입력해주세요 ex)hyw : ')
evaluate_df.to_csv(f'./evaluate_data_{name}.csv', index=False)