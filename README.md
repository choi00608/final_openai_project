# 1. 가상환경 만들기
- uv 명령어를 사용해서 가상환경을 만들어 준다.  
없으면 설치하면 된다.
```bash
    pip install uv
    py -3.10 -m pip install uv
```
- 초기설정은 아래와 같이 하면된다.
``` bash
    uv init
```
- 설정을 하고 나면 이상한 파일이 막 생기는데, 없애진 말고, 소중히 다뤄야 한다.  
필요한 의존 라이브러리를 추가해 보자
```bash
    uv add openai numpy dotenv pprint flask yaml json base64 #이런 식으로 추가하면 됨
    #그러면 파일이 하나 더생긴다
```

# 2. config.yaml 만들기
- openai에게 넘겨줄 프롬프트 정보, 변수, 서비스티어 등 파라미터로 넘겨줄 정보를 파일로 저장한다. 예시는 아래와 같다

```yaml
    prompt:
        id: "pmpt_68ac1a14fd4881959da68057b65c0fd80fe833400bc94b11"
        version: "5" # 없으면 기본값
        variables:
            user_name: "멀린"
            my_pdf:
                type: "input_file"
                file_id: "file-........"
            my_image:
                type: "input_image"
                ile_id: "file-........"
    service_tier: "auto" # auto, flex, default, priority
    truncation: "auto"   # auto, disabled
```
- variables 값을 추가 할 때는, openai platform 에서 꼭 변수 이름에 맞는 값을 추가 해 줘야함.  
또한 Developer message 에서 사용자 이름: {{user_name}} 와 같이 명시적으로 값을 지정해야지 저장해도 안사라짐 <- 이거 안하면 저장하고 다시 들어가면 변수 없어져 있음  

# 3. ".env" 만들기
- api 키를 안전하게 사용하기 위해서는 .env 파일을 만들어서 키를 따로 관리해야한다.  
아래 코드를 터미널에 입력하면 .env 파일이 생성된다.

```bash
    echo 'OPENAI_API_KEY=여기다가_키를_입력하면_됨' > .env
```

# 5. 깃허브 연동하기
- 적당히 코드보고 따라하면 된다.
```bash
    git init
    git remote add origin [원격 저장소 주소]
    git branch -m main
```

# 5. ".gitignore" 수정하기
- push 하기 전에 민감한 정보는 마스킹 해야한다. uv나 flask, git이 만든 파일은 건들지 말고, 테스트코드나 쓸모없는 사진, 대용량 데이터 등을 명시해서 github에 업로드 되는걸 방지 해 준다.  
특히 .env 파일이 업로드되는 대참사를 막아준다.  
아래는 예시코드
```text
    # Python-generated files
    __pycache__/
    *.py[oc]
    build/
    dist/
    wheels/
    *.egg-info

    # Virtual environments
    .venv

    .env    #개중요함
    test*
```

# 6. 마저 업로드 하기
- 개인정보 마스킹을 했으면 github에 마저 업로드 해 준다.
```bash
    git add .
    git commit -m "initial commit"
    git push origin main
```
- 이제 깃허브 페이지로 가서 멀쩡히 올라갔는지 확인 해 보자.

# 7. 개발 시작하기
- 해당 프로젝트의 app.py 파일의 내용을 참고하여 openai api의 작동방식을 보고, 잘 활용하면 된다.