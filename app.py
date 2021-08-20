from flask import Flask, request, jsonify, abort
import time
import requests
import asyncio
import asgiref

app = Flask(__name__)

wait_count = 0
message_list = []
count_start = False

async def waiting():
    global wait_count
    global message_list

    # hello_code가 실행될때마다 wait_count 가 0으로 초기화
    # 새로운 대화가 넘어오지 않으면 1초마나 wait_count가 1씩 누적
    while wait_count < 6:
        wait_count = wait_count + 1
        time.sleep(1)
        # 아무동작 없이 5초가 흐르면 누적된 대화 리스트를 합쳐 모델API로 보냄
        if wait_count > 4:
            global count_start
            count_start = False
            message_to_model = "".join(message_list)
            # API로 리턴 받은 대답을 리턴해줌
            result = await requests.post('model/api/', message_to_model)
            # 대화 내용과 결과를 DB에 저장


            # 대답후 사용자의 대화를 받기 위해 리스트 초기화
            message_list = []
            return result
            


@app.route('/')
def hello_open():
    return 'Hello World!'


@app.route('/api',methods=['POST'])
async def hello_code():
    global count_start
    global wait_count
    # 입력이 들어올때마다 카운트 0으로
    wait_count = 0

    # 넘어온 JSON에서 메세지 받아 임시 리스트에 append
    body = request.get_json()
    message_to_model = body['name']
    message_list.append(message_to_model)

    # 처음 대화가 시작되는 순간에만 사용하기 위해 count_start 를 바꿔줌
    # 두번째 말풍선부턴 실행되지 않음
    if count_start == False:
        count_start = True
        # waiting() 으로 완성된 문구를 리턴받음
        result = await waiting()
        return result

    return "loading..."

if __name__ == '__main__':
    app.run(debug=True)