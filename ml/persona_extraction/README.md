# Chat Persona extraction Model for Korean

## Chat Persona extraction Model이란?

- 사용자의 일상 채팅에서 사용자의 페르소나를 추출하는 모델입니다.
- 해당 모델을 개선할 수 있는 여러 Ablation 실험들은 다음 [블로그](https://blog.naver.com/gypsi12/223396121146)에서 확인하실 수 있습니다.

## How to Use
- 🤗[Huggingface Hub](https://huggingface.co/NLPBada/kobart-chat-persona-extraction-v2)에 업로드된 모델을 곧바로 사용할 수 있습니다
```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("NLPBada/kobart-chat-persona-extraction-v2")
tokenizer = AutoTokenizer.from_pretrained("NLPBada/kobart-chat-persona-extraction-v2")
```

## Finetuning

|                         | Hardware | Max len |   LR | Batch | Train Step |
| :---------------------- | -------: | ------: | ---: | ----: | ---------: |
| **Encoder** | Tesla V100 32G   |    500 | 1e-5 |    16 |         1M |
| **Decoder** | Tesla V100 32G   |    200 | 1e-5 |    16 |         1M |


## Evaluation Result

| 모델 | batch_size | epoch | 어투 | Rouge-1-f1 | Rouge-2-f1 | Rouge-L-f1 | BLEU | 전체 데이터셋 개수 | 데이터셋 |
| --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- |
| KoBART | 16 | 4 | 존댓말 | 0.5913 | 0.3789 | **0.5882** | 0.4493 | 41316 | [데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)
| ET5 | 8 | 4 | 존댓말 | 0.6127 | 0.3838 | **0.6086** | 0.4248 | 41316 | [데이터셋](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71630)
| KoBART | 16 | 8 | 반말 | 0.5500 | 0.3306 | **0.5512** | 0.4373 | 10328 | [데이터셋](https://huggingface.co/datasets/NLPBada/korean-persona-chat-dataset-v2)
| ET5 | 8 | 10 | 반말 | 0.6068 | 0.3811 | **0.6026** | 0.4218 | 10328 | [데이터셋](https://huggingface.co/datasets/NLPBada/korean-persona-chat-dataset-v2)

## 재현 방법

### 1. requirements
cuda version : 11.2, linux-64 에서
```
# $ conda env create --name [가상환경이름] -f requirements.yaml
```

### 2. Config 설정
- configs폴더 내에 config 파일을 생성
  ```
  {"model_name": "gogamza/kobart-base-v2", # 모델 이름
  "model_detail" : "kobart-baeline-rouge-bleu-by-val_bleu_avg", # 모델 세부 설명
  "resume_path" : "./checkpoints/gogamza/kobart-base-v2kobart-baeline-rouge-bleu-by-val_bleu_avg.ckpt", # 만약 학습을 이어서 하고 싶을 경우 checkpoint 파일 경로
  
  "metric": "val_rouge-l-f1", # 평가지표
  "metric_mode": "max", # 평가지표 기준

  "wandb_entity" : "gypsi12", # wandb entity이름
  "wandb_project" : "persona_extraction", # wandb 프로젝트 이름
  "wandb_run_name" : "kobart-baeline-rouge-bleu-by-val_bleu_avg", # wandb상 실행 이름
  
  "batch_size": 16, # 배치 크기
  "shuffle": true, # 학습 데이터 shuffle 여부
  "learning_rate":1e-5, # learning rate
  "epoch": 10, # 최대 epoch
  
  "train_path":"./data/train/train.csv", # 학습 데이터 경로
  "dev_path":"./data/val/validation.csv", # 검증 데이터 경로
  "test_path":"./data/val/validation.csv", # 테스트 데이터 경로
  "predict_path":"./data/val/validation_csv"} # 예측 데이터 경로
  ```

### 3. 학습
```
python [모델]_train.py --config "[모델]/[모델 config.json]"
```

### 4. 학습 결과
- 학습 결과는 ./best_model/ 경로에 .pt로 저장됨
- checkpoint들을 ./checkpoints/ 경로에 .ckpt로 저장됨
