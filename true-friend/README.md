# 찐친이 되어줘 



## Installation

### Prerequisites

#### Security group

NCP (ACG), AWS (Security group) 등 클라우드 환경에서 띄울 경우에는 방화벽 설정의 Inbound rule 에서 80번 포트에 대한 접속을 허용해야 합니다. 새로운 group 을 생성한후 서버 instance 에 붙여주세요. 만약 각 app 에 직접 접속해서 사용해보고 싶다면, 8000번 `main_app`, 8001번 `generation_app`, 8002번 `persona_app`, 8003번 `retrospective_app`, 8005번 `RedisInsight ` 포트를 추가로 열어주시면 됩니다.

#### Docker

> Ubuntu Linux 기준으로 설명되어 있으니, 윈도우에서 띄우실때는 [docker-desktop](https://www.docker.com/products/docker-desktop/) 을 설치해주세요.

1. [Docker Engine / Install / Ubuntu / Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) 를 참조해서 docker engine 을 설치합니다.

2. [Docker Compose / Install / Install Compose plugin / Install using the repository](https://docs.docker.com/compose/install/linux/#install-using-the-repository) 를 참조해서 docker compose 를 설치합니다.

3. [Installilng the NVIDIA Container Toolkit / Installation / Installing with Apt](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) 를 참조해서 nvidia container toolkit 을 설치합니다. (GPU support)

4. nvidia container toolkit 을 사용할수 있도록 docker daemon 설정을 변경해줍니다.

   ```bash
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

5. [Sample Workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html) 를 돌려서 gpu 가 잘 인식되는지 확인합니다.

   ```bash
   sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
   ```

#### Docker Volumes

1. 서비스들에 사용되는 5개의 volume 을 미리 생성합니다.

   ```bash
   docker volume create model_data
   docker volume create postgres_data
   docker volume create redis_data
   docker volume create static_data
   docker volume create media_data
   ```

   - `model_data` 는 local 모델 파일을 저장하는 저장소로써, langchain 의 [Llama.cpp](https://python.langchain.com/docs/integrations/llms/llamacpp) 를 통해 불러올수 있는 `.gguf` 형태의 모델들이 위치하게 됩니다. 각 모델들은 `generation_app` 에서 대화를 생성할때, `retrospective_app` 에서 회고를 생성할때 사용되게 됩니다.
   - `postgres_data` 는 PostgreSQL 컨테이너에 마운트되는 볼륨이며, 실제 데이터가 저장됩니다. `persona_app`  의 유저 페르소나 정보와, `retrospective_app` 의 회고가 이곳에 저장됩니다.
   - `redis_data` 는 Redis 컨테이너에 마운트되며, 1초에 한번씩 서버에 올라와있는 전체 데이터를 이곳에 쓰게 됩니다 (`--appendfsync everysec`). Redis 서버 에는 `generation_app` 에 들어오는 user input 에 대해 생성된 bot response를 한 turn 으로 묶어서 저장됩니다.
   - `static_data` 와 `media_data` 는 Django 로 개발된 `main_app` 의 `static_root` 와 `media_root` 경로에 각각 mount 되며, `static_data` 에는 css, js 파일들, `media_data` 에는 사진을 포함한 파일 들이 저장되고, 이들은 Nginx 컨테이어에 동시에 마운트되어 서비스됩니다.

2. 사용할 `.gguf ` 파일을 다운로드 받습니다. 

3. 다운로드 받은 `.gguf` 파일은 `model_data` volume 에 넣어줍니다.

   - 임시로 Linux 컨테이너를 만들어 `model_data` volume 을 마운트해줍니다. (alpine 등 다른 리눅스를 사용하셔도 무방합니다.)

     ```bash
     docker run -dit --name temp-container -v model_data:/app/model ubuntu:latest
     ```

   - `.gguf` 모델 파일을 마운트된 볼륨의 경로로 복사해줍니다.

     ```bash
     docker cp /path/to/your/model.gguf temp-container:/app/model
     ```

   - 임시 컨테이너를 삭제해줍니다.

     ```bash
     docker stop temp-container
     docker rm -f temp-container
     ```

### Environment variables

> 환경변수는 `.env.template` 의 형태로 제공되며, 각 서비스에 대한 설정을 변경할수 있습니다.

프로젝트 폴더 내부의 `.env.template` 파일을 복사하여 `.env` 파일을 생성후 설정 진행해주세요.

```.env
OPENAI_API_KEY=""
DJANGO_SECRET_KEY=""
GENERATION_LLM_MODEL_PATH=/app/models/.gguf
RETROSPECTIVE_LLM_MODEL_PATH=/app/models/.gguf
PERSONA_TF_MODEL_ID=NLPBada/et5-persona-extraction
PERSONA_HF_TOKEN=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
RETROSPECTIVE_TF_MODEL_ID=alaggung/bart-r3f
DJANGO_DB_NAME=djangodb
API_DB_NAME=apidb
DB_USERNAME=
DB_PASSWORD=
DB_NAME=
DB_HOST=postgres_db
DJANGO_ADMIN_USERNAME=
DJANGO_ADMIN_PASSWORD=
DJANGO_BOT_NAME=
DJANGO_HOST_NAME=
HF_HOME=/app/models/.cache
```

- `OPENAI_API_KEY` :  사용에 필요하며, [사이트](https://platform.openai.com/)에서 미리 요금을 충전해 놓아야 합니다.
  - `generation_app` 에서 user input에 대한 답변을 생성할때 ([OpenAI](https://python.langchain.com/docs/integrations/llms/openai))
  - `persona_app` 에서 생성된 유저 페르소나 문장 각각을 embedding 할때 ([OpenAIEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/openai))

- `DJANGO_SECRET_KEY` : `main_app` 에서 사용되는 키로, Django 내부에서 데이터 암호화 및 다양한 토큰 생성에 사용됩니다.
  - 키는 필요하신 분들에게 따로 배포되거나, (우선 `main_app` 컨테이너를 띄운 다음에) [가이드](https://codinggear.org/django-generate-secret-key/)를 보시고 직접 생성하셔야 합니다.
- `GENERATION_LLM_MODEL_PATH` : `generation_app` 에서 bot response 생성을 위해 사용될 모델로, `/app/models/` 는 고정이며, 뒤에 `.gguf` 파일 이름만 위에서 `model_volume` 에 복사했던 파일 이름으로 설정해주세요.
  - (24.03.23) `generation_app` 에서 openai api 를 사용하도록 설정되어 있으므로 명시된 모델은 사용되지 않습니다.
- `RETROSPECTIVE_LLM_MODEL_PATH` : `retrospective_app` 에서 회고 생성에 사용되는 모델입니다. 방식은 위와 동일하며, 서로 다른 모델을 사용하셔도 됩니다.
- `PERSONA_TF_MODEL_ID`, `PERSONA_HF_TOKEN` : `persona_app` 에서 대화 데이터로부터 유저 페르소나를 추출하는데 사용되는 huggingface 모델 입니다.
  - (24.03.23) 모델이 비공개 되어있는 관계로 사용할때 토큰이 필요합니다. 
- `RETROSPECTIVE_TF_MODEL_ID` : `retrospective_app` 에서 회고를 생성할때 사용되는 대화 데이터의 양 (토큰 갯수) 를 줄이기 위해 summarization 을 진행할때 사용되는 huggingface 모델 입니다. [`alaggung/bart-r3f`](https://huggingface.co/alaggung/bart-r3f) 를 고정적으로 사용합니다.
- `DJANGO_DB_NAME` : Django 로 작성된 `main_app` 에서 사용되는 DB 의 이름을 지정합니다. 
- `API_DB_NAME` : Fastapi 로 작성된 `persona_app` 과 `retrospective_app` 에서 사용할 DB 이름을 지정합니다. 
  - Postgres 컨테이너는 하나를 띄우지만, Django project 에서 사용되는 테이블과 Fastapi app 들에서 사용되는 테이블을 서로 다른 DB 를 통해 분리해서 관리합니다.
- `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` : [Postgres 이미지](https://hub.docker.com/_/postgres)를 띄울때 설정하는 환경변수 입니다. 최초 run 할때 `DB_USERNAME`, `DB_PASSWORD` 를 기준으로 루트 계정이 생성되고, `DB_NAME` 의 새로운 DB 를 생성합니다. 
- `DB_HOST` : Postgres 컨테이너에 연결할때 사용하는 host 이름이며, `postgres_db` 를 고정으로 사용합니다. (`docker-compose.yml` 의 `services` 참고)
- `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_PASSWORD` : `main_app` 을 띄울때, Django admin 에서 사용할 계정을 자동으로 생성할때 사용됩니다.
- `DJANGO_BOT_NAME` : `main_app` 의 `chat` 앱 내에서 표시될 챗봇 프로파일의 이름을 설정합니다. 챗봇 프로파일이 생성되지 않으면 앱이 동작하지 않으므로 필수로 정해줘야 합니다.
- `DJANGO_HOST_NAME` : 서버가 돌아갈 기기의 public ip 값을 그대로 입력해주세요. `main_app` 의 js 파일들에서 fetch api 를 사용할때 host 를 식별하는 용도로 사용됩니다.
  - 외부 client 에서 서버쪽으로 요청을 보내도록 하기위함입니다.
- `HF_HOME` : 위에서 설정했던 huggingface 모델들의 cache 를 `model_data` 볼륨에 저장해놓고 재사용 하기 위함입니다. 그대로 사용해주세요.

### Nginx configuration

위에 방화벽에서 80번 포트를 허용해서 http request 가 들어오도록 하였습니다. Nginx 로 하여금 그 요청을 처리 하도록 하기 위해서는 (`/nginx` 폴더 내부의) `nginx.conf` 파일에 `server_name` 을 지정해줘야 합니다.

```nginx
http {
    server {
        listen 80;
        server_name localhost;

        location /static/ {
            alias /vol/static/;
        }

        location /media/ {
            alias /vol/media/;
        }
    }
}
```

- `server_name` 을 본인의 머신에서 띄울경우 `localhost` , 아닌 경우 클라우드 인스턴스의 public ip 를 넣어주세요.
- `location` 부분은 이전에 만들었던 `static_data` 볼륨과 `media_data` 볼륨을 마운트 시켜주는 부분입니다. 각 볼륨들 내부 데이터는 `main_app` 에 Django 서버에 의해 생성/변경되지만 nginx 서버에서 직접 호스팅되게 됩니다.

### Docker compose

> compose 를 띄우고 이미지를 실행합니다.

#### Build

> 다시 빌드하는 경우에는 `docker image prune` 을 통해 사용되지 않는 `<none>` 이미지를 삭제하고 새로 build 해주세요.

```bash
docker compose build
```

8 종류의 이미지가 새로 다운로드 또는 생성 됩니다.

- Docker compose 이미지
  - `turefriend/django-main-app:latest` 
  - `turefriend/fastapi-generation-app:latest`
  - `turefriend/fastapi-persona-app:latest`
  - `turefriend/fastapi-retrospecive-api:latest`
  - `turefriend/nginx-reverse-proxy:latest`
- Base 이미지
  - [`iloveonsen/fastapi-llamacpp-conda:latest`](https://hub.docker.com/r/iloveonsen/fastapi-llamacpp-conda)
  - [`pgvector/pgvector:0.6.2-pg16`](https://hub.docker.com/r/pgvector/pgvector)
  - [`redis/redis-stack:latest`](https://hub.docker.com/r/redis/redis-stack)

#### Up

```bash
docker compose up
```

- 생성된 이미지들로 부터 컨테이너를 띄웁니다.
  - `postgres-vector-db  | LOG:  database system is ready to accept connections`
  - `retrospective-nginx  | /docker-entrypoint.sh: Configuration complete; ready for start up` 
  - `retrospective-api   | INFO: Application startup complete.`
  - 와 같이, 각 서비스로부터 ready log 가 뜨면 정상입니다.
- 완료후 브라우저를 키고 `http://{서버의 public ip}` 으로 접속했을때, 로그인 화면이 뜨면 성공입니다.
  - nginx 컨테이너를 통해 배포되므로 80번 포트로 서비스됩니다.

#### Down

```bash
docker compose down
# 또는 Ctrl+C
```

- 컨테이너들을 shutdown 합니다.



