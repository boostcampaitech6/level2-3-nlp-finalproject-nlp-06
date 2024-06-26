from prettytable import PrettyTable

def convert_to_json(user_persona, bot_persona, prev_dialog, response):
    """
        Convert the data into the json format.

        user_persona : 페르소나 추출 모델로 추출해낸 top-3개 (threshold=0.8) 의 유저 페르소나
        bot_persona : MSC 데이터셋에서 제공된 fix된 페르소나 문장
        prev_dialog : 이전 5-turn의 대화
        response : 다음 turn에 발화할 것으로 예측되는 챗봇의 답변
    """
    json_data = []
    for i in range(len(response)):
        cur = {}
        cur['response'] = response[i]
        if user_persona is not None:
            cur['user_persona'] = user_persona[i]
        if bot_persona is not None:
            cur['bot_persona'] = bot_persona[i]
        if prev_dialog is not None:
            cur['prev_dialog'] = prev_dialog[i]
        json_data.append(cur)
    return json_data


def add_question(dimension, output, src=None, ref=None, context=None, task=None):
    """
        Add questions to generate input in Bool-QA format for UniEval.
        
        dimension: specific dimension to be evaluated
        src: source input for different NLG tasks. For example, source document for summarization 
             and dialogue history for dialogue response generation.
        output: output text generated by the models
        ref: human-annotataed groundtruth
        context: the context needed to evaluate several specific dimension. For example,
                 additional factual information when evaluating engagingness and groundedness in dialogues.
    """
    
    input_with_question = []
    for i in range(len(output)):
        # For summarization
        if task == 'summarization':
            if dimension == 'fluency':
                cur_input = 'question: Is this a fluent paragraph? </s> paragraph: ' + output[i]
            elif dimension == 'coherence':
                cur_input = 'question: Is this a coherent summary to the document? </s> summary: ' + output[i] + ' </s> document: ' + src[i]
            elif dimension == 'consistency':
                cur_input = 'question: Is this claim consistent with the document? </s> claim: ' + output[i] + ' </s> document: ' + src[i]
            elif dimension == 'relevance':
                cur_input = 'question: Is this summary relevant to the reference? </s> summary: ' + output[i] + ' </s> reference: ' + ref[i]
            else:
                raise NotImplementedError('The input format for this dimension is still undefined. Please customize it first.')
        # For dialogues
        elif task == 'dialogue':
            if dimension == 'naturalness':
                cur_input = 'question: Is this a natural response in the dialogue? </s> response: ' + output[i]
            elif dimension == 'coherence':
                cur_input = 'question: Is this a coherent response given the dialogue history? </s> response: '\
                            + output[i] + ' </s> dialogue history: ' + src[i]
            elif dimension == 'engagingness':
                cur_input = 'question: Is this an engaging and informative response according to the dialogue history and fact? </s> response: '\
                            + output[i] + ' </s> dialogue history: ' + src[i] + ' </s> fact: ' + context[i]
            elif dimension == 'groundedness':
                cur_input = 'question: Is this response consistent with knowledge in the fact? </s> response: '\
                            + output[i] + ' </s> fact: ' + context[i]
            elif dimension == 'understandability':
                cur_input = 'question: Is this an understandable response in the dialogue? </s> response: ' + output[i]
            else:
                raise NotImplementedError('The input format for this dimension is still undefined. Please customize it first.')
        # For data-to-text
        elif task == 'data2text':
            if dimension == 'naturalness':
                cur_input = 'question: Is this a fluent utterance? </s> utterance: ' + output[i]
            elif dimension == 'informativeness':
                cur_input = 'question: Is this sentence informative according to the reference? </s> sentence: '\
                            + output[i] + ' </s> reference: ' + ref[i]
            else:
                raise NotImplementedError('The input format for this dimension is still undefined. Please customize it first.')
        # For factual consistency detection
        elif task == 'fact':
            if dimension == 'consistency':
                cur_input = 'question: Is this claim consistent with the document? </s> claim: ' + output[i] + ' </s> document: ' + src[i]
            else:
                raise NotImplementedError('No other dimensions for the factual consistency detection task.')
        # For new customized tasks
        else:
            raise NotImplementedError('Other tasks are not implemented, please customize specific tasks here.')
        input_with_question.append(cur_input)
    return input_with_question


def print_scores(scores):
    table = PrettyTable(['Dimensions','Score'])
    print('\nEvaluation scores are shown below:')
    dims = list(scores[0].keys())
    for dim in dims:
        cur_score = 0
        for i in range(len(scores)):
            cur_score += scores[i][dim]
        table.add_row([dim, round(cur_score / len(scores), 6)])
    print(table)