import datetime
import hashlib

import jwt

from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for

client = MongoClient('mongodb+srv://text:sparta@cluster0.44vwqnl.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta



app = Flask(__name__)

SECRET_KEY = 'Lee'


@app.route('/')
def page1():
    return render_template('index.html')


@app.route("/register")
def page2():
    return render_template('index2.html')


# 테스트 코드영역 (이미지 연동 시도코드)
# @app.route("/uploadimage", methods=['POST'])
# def upload():
#     img = request.files['image']
#     print(img)
#     fs = gridfs.GridFS(db)
#     print(fs)
#     fs.put(img, filename='name')
#
#     return jsonify({'msg':'저장에 성공했습니다.'})


@app.route("/like_post", methods=['POST'])
def like_post():
    title_receive = request.form['title_give']

    target_post = db.users_post.find_one({'title': title_receive})
    current_like = target_post['like']
    new_like = current_like + 1

    db.users_post.update_one({'title': title_receive}, {'$set': {'like': new_like}})

    return jsonify({'result': 'success', 'msg': '❤'})


@app.route("/home", methods=["GET","POST"])
def page12():
    if request.method == 'POST':
        title_receive = request.form['name_give']
        content_receive = request.form['content_give']

        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        ID = payload['ID']
        print(ID)
        print("aaaaa");
    ## 입력한 제목값이 이미 존재하는지, 몽고DB에 검색하여 조회함
        result = db.users_post.find_one({"title": title_receive})

    ## 만약 있을 경우,
        if result is not None:
            return jsonify({'msg': "이미 존재하는 글제목입니다!"})

    ## 없을 경우, 몽고 DB에 타이틀,글내용, 이미지를 저장한다.
        else:
            db.users_post.insert_one({'ID':ID,'title': title_receive, 'content': content_receive, 'like':0})
            return jsonify({'msg': '등록완료!'})

    elif request.method == 'GET':



        # img = request.files['image']
        # fs = gridfs.GridFS(db)
        # fs.put(img, filename='name')
        # return jsonify({'msg': '저장에 성공했습니다.'})


        userpost_list = list(db.users_post.find({}, {'_id': False}))
        return jsonify({'usersPost': userpost_list})

    else:
        return render_template('index3.html')

@app.route("/post")
def page4():
    return render_template('index4.html')

# def login_required():
# return redirect(url_for("page1", msg="로그인 정보가 존재하지 않습니다."))

## 메인페이지
@app.route("/main")
def login_required():
    token_receive = request.cookies.get('mytoken')
    print(token_receive)
    try:
        ## 쿠키에 담겨있는 토큰값을 시크릿키로 디코딩한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        ## 디코딩한 값의 ID와, 몽고DB ID값이 같은 것을 추출한 후,
        ## 같은 것이 있다면 index3페이지와 몽고DB ID키값을 리턴한다.
        user_ID = db.users.find_one({"ID": payload['ID']})
        return render_template('index3.html', ID=user_ID["ID"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("page1", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("page1", msg="로그인 정보가 존재하지 않습니다."))

## -------------------무시해주세요. 테스트코드영역입니다.---------------
# return render_template('index3.html')

## 로그인 사용자만 통과하는 API / 메인페이지
# @app.route("/main/tokenpass", methods=["GET"])
# def nonName():

#    token_receive = request.cookies.get('mytoken')
#    payload = jwt.decode(token_receive, SECRET_KEY, algorithms='HS256')
#    print(payload)
#    return jsonify({"msg":token_receive})
## -------------------무시해주세요. 테스트코드영역입니다.---------------

## 로그인
@app.route("/login", methods=["POST"])
def web_users_POST():
    ID_receive = request.form['ID_give']
    PW_receive = request.form['PW_give']

    ## index.html에서 입력된 PW_receive값을 해쉬화한 다음 몽고 DB안에 있는 ID/PW와 같은 것을 서칭한다
    ## EX) qq를 PW로 하고 몽고DB에 저장한다음, qq를 시험삼아 해쉬화하여 msg에 찍어보니 둘은 똑같았다.
    PW_hash = hashlib.sha256(PW_receive.encode('utf-8')).hexdigest()
    ## result변수 안에 ID/PW가 입력된 것과 동일한 것을 찾아 넣는다.
    result = db.users.find_one({'ID': ID_receive, 'PW': PW_hash})

    if result is not None:  # 일치한다면
        payload = {
            'ID': ID_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1000)  # 로그인 24시간 유지
        }
        # 유저 아이디와 유효기간을 담고 있는 payload 생성

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # jwt기반 토큰 생성

        return jsonify({'msg': '로그인 성공!', 'token': token})
        # 토큰을 유저에게 부여

        # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


## 회원가입
@app.route("/register", methods=["POST"])
def web_register_post():
    ID_receive = request.form['ID_give']
    PW_receive = request.form['PW_give']
    ## PW_receive 해쉬화하여 암호화 진행
    PW_hash = hashlib.sha256(PW_receive.encode('utf-8')).hexdigest()

    ## 입력한 아이디값이 이미 존재하는지, 몽고DB에 검색하여 조회함
    result = db.users.find_one({"ID": ID_receive})

    ## 만약 있을 경우,
    if result is not None:
        return jsonify({'msg': "이미 존재하는 ID입니다!"})

    ## 없을 경우,
    ## 해쉬화한 암호를 몽고DB에 insert하였음
    ## 이제 해당 데이터를 index.html에 input된 ID/PW와 대조하여 일치하면
    ## token발행을 하면되니, POST방식으로 index.html에서 input값 받아오자
    else:
        db.users.insert_one({'ID': ID_receive, 'PW': PW_hash})
        return jsonify({'msg': '가입완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
