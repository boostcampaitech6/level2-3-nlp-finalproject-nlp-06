# persona_extraction_model

## Huggingface 공개
### Model
- [한국어 존댓말 사용자 발화에서 사용자의 페르소나 추출](https://huggingface.co/NLPBada/kobart-chat-persona-extraction)
- [한국어 반말 사용자 발화에서 사용자의 페르소나 추출](https://huggingface.co/NLPBada/kobart-chat-persona-extraction-v2)
### Dataset
- [(한국어 반말 사용자 발화-사용자 페르소나) 쌍 데이터 구축](https://huggingface.co/datasets/NLPBada/korean-persona-chat-dataset/tree/main)

<br/>

## 실행 방법

### 1. requirements
cuda version : 11.4, linux-64 에서
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
