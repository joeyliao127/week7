from flask import *
import mysql.connector
import json
# import datetime
app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key = "0xffffffff"


db_connection = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "website"
}

try:
    connection = mysql.connector.connect(**db_connection) 
    if connection.is_connected():
        print("Connected to the database!")

except Exception as ex:
    print("Connection failed")
    print(ex)

cursor = connection.cursor(dictionary=True)

def createMember(name, username, password):
    queryString = "INSERT INTO member (name, username, password) VALUES (%s,%s,%s)"
    qureyValue = (name, username, password)
    try:
        cursor.execute(queryString, qureyValue)
        connection.commit()
        return True
    except Exception as ex:
        print("新增失敗...")
        print(f"來自DB的錯誤訊息：{ex}")
        return False
    
def find(qurey: str, qureyValue: tuple):
    try:
        print(f"============find()要執行的queryStr============\n{(qurey, qureyValue)}")
        cursor.execute(qurey, qureyValue)
        result = cursor.fetchall()
        res = []
        for item in result:
            res.append(item)
        return res

    except Exception as ex:
        print("查詢失敗...")
        print(f"來自DB的錯誤訊息：{ex}")
        return False

def verify(username: str, password: str):
    qureyStr = "SELECT id,name, username FROM member where username = %s and password = %s"
    qureyValue = (username, password)
    result = find(qureyStr, qureyValue)
    if(result):
        return result
    else:
        return None

def getComment(count: int):
    qureyStr = "SELECT member.id, member.name, message.time, message.content, message.id as msg_id FROM member JOIN message ON member.id = message.member_id ORDER BY message.id DESC LIMIT 5 OFFSET %s;"
    count = (count,)
    queryResult = find(qureyStr, count)
    result = []
    for data in queryResult:
        #data格式為：{'id': 2, 'name': 'Joey', 'time': datetime.datetime(2022, 6, 18, 0, 0), 'content': 'Hi here is Joey'}
        date = data["time"].date()        
        date = date.isoformat()
        result.append({
            "id": data["id"],
            "name": data["name"],
            "date": date,
            "comment": data["content"],
            "msg_id": data["msg_id"]
        })
    res = {
        "userInfo":{
            "id": session["id"],
            "name": session["name"]
        }
    }
    res["msg"] = result
    res = json.dumps(res)
    print("-----------------getComment return value-------------------", res)
    return res

def insertMsg(id, content):
    qureyStr = "INSERT INTO message(member_id, content) VALUES(%s,%s)"
    qureyValue = (id, content)
    try:
        cursor.execute(qureyStr, qureyValue)
        connection.commit()
    except Exception as ex:
        print(f"message新增失敗，錯誤訊息：{ex}")


@app.route("/")
def index():
    session["status"] = False
    return render_template("index.html")

@app.route("/signin", methods=["POST"])
def signin():
    verified = verify(request.form["username"], request.form["password"])
    print(f'sign裡面的verified():{verified}')
    if(verified):
        data = verified[0]
        session["status"] = True
        session["id"] = data["id"]
        session["name"] = data["name"]
        session["username"] = data["username"]
        return redirect("member")
    else:
        return redirect(url_for("error", message = "帳號或密碼輸入錯誤"))

@app.route("/signout")
def signout():
    session["status"] = False
    session["id"]=""
    session["name"] = ""
    session["username"] = ""
    return redirect("/")

@app.route("/error")
def error():
    message = request.args.get("message")
    return render_template("error.html", message = message)

@app.route("/member")
def member():
    if(session["status"]):
        return render_template("member.html", name = session["name"])
    else:
        return redirect("/")
    
@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]
    queryStr = "SELECT name FROM member WHERE name = %s"
    qureyValue = (username,)
    result = find(queryStr, qureyValue)
    print(f"檢查註冊的使用者，是否有返回帳號：{result}")
    if(result):
        return redirect(url_for("error", message="帳號已經被註冊"))
    else:
        createMember(name, username, password)
        return redirect("/")

@app.route("/init")
def init():
    result = getComment(0)
    print(f"------------------init裡面接收到的result---------------\n{result}")
    return result


@app.route("/loadMore/<count>")
def loadMore(count):
    result = getComment(count=int(count))
    print(f"loadMore回傳的API---------------------------------------------\n{result}")
    return result

@app.route("/createMessage", methods=["POST"])
def createMessage():
   content = request.form["comment"]
   insertMsg(id=session["id"], content=content)
   return redirect("member")

@app.route("/getUserInfo")
def getUserInfo():
    res = {
        "id": session["id"]
    }
    res = json.dumps(res)
    return res

@app.route("/deleteMessage/", methods=["POST"])
def deleteMessage():
    data = request.json
    verify_id = data["user_id"]
    msg_id = data["msg_id"]
    qureyValue = (msg_id,)
    if(int(verify_id) == session["id"]):
        print("驗證通過，執行刪除Fn")
        qureyStr = f"DELETE FROM message where id = %s"
        try:
            cursor.execute(qureyStr, qureyValue)
            connection.commit()
        except Exception as ex:
            print(f"刪除失敗，來自DB的錯誤訊息：{ex}")
    else:
        print("驗證失敗....")
    return "ok"

@app.route("/searchMemberMsg/<member_name>")
def searchMemberMsg(member_name):
    qureyStr = "SELECT member.id, member.name, message.time, message.content, message.id as msg_id FROM member JOIN message ON member.id = message.member_id WHERE member.name = %s ORDER BY message.id DESC;"
    print("要搜尋的人：", member_name)
    qureyValue = (member_name, )
    qureyResult = find(qurey=qureyStr, qureyValue=qureyValue)
    print(f"========search route找到的資訊為：===============\n{qureyResult}")
    result = []
    for data in qureyResult:
        date = data["time"].date()        
        date = date.isoformat()
        result.append({
            "id": data["id"],
            "name": data["name"],
            "date": date,
            "comment": data["content"],
            "msg_id": data["msg_id"]
        })
    res = {
            "userInfo":{
                "id": session["id"],
                "name": session["name"]
            }
        }
    res["msg"] = result
    res = json.dumps(res)
    return res

app.run(port=3000, debug=True, use_reloader=True)


