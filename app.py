from flask import *
import mysql.connector
import json
import threading
app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key = "0xffffffff"

dbconfig = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root", 
    "password": "root",
    "database": "website",
}

connectionPool = mysql.connector.pooling.MySQLConnectionPool(pool_name="website",pool_size=5,**dbconfig)

def connectionDecorator(operationFn):
    def connectDB(queryStr: str, queryArgs: tuple):
        print("建立db_connection...")
        print(f"CRUD Fn的args = {queryStr}")
        try:
            print("嘗試使用connection pool取得連線....")
            with connectionPool.get_connection() as connection:
                print("Connected to database!")
                with connection.cursor(dictionary=True) as cursor:
                    result = operationFn(cursor,connection,queryStr,queryArgs)  
                    return result
        except Exception as ex:
            print("連線失敗:")
            print(f"來自DB的錯誤訊息：{ex}")
        print(f"關閉connection", {connection.is_connected()})
        print(f"關閉cursor")                               
    return connectDB

# @connectionDecorator
# def test(cursor, connection, queryStr, queryArgs):
#     print("test連線成功！！")
# test()

#依照以下格式輸入：
#1. create(query字串, query參數)
#2. queryStr需為完整的句子，如"INSERT INTO member (name, username, password) VALUES (%s, %s, %s)"
#3. queryArgs為tuple，如queryArgs = ("EEE", "EEE", "EEE")
@connectionDecorator
def insert_data(cursor,connection, queryStr: str,queryParameter: tuple):
    try:
        cursor.execute(queryStr, queryParameter)
        connection.commit()           
        print("create交易完成")
        return True
    except Exception as ex:
        print("create交易失敗...")
        print(f"來自DB的錯誤訊息：{ex}")
        return False

#依照以下格式輸入：
#1. find(query字串, query參數)
#2. queryStr需為完整的句子，如SELECT * FROM member where name = %s
#3. queryAargs為tuple，如("Joey",)
#4. find return一個list，裡面包含了多個字典。[{}, {}, {}]
@connectionDecorator
def find(cursor,connection,queryStr: str, queryParameter: tuple):
    try:
        print(f"============find()要執行的queryStr============\n{(queryStr, queryParameter)}")
        cursor.execute(queryStr, queryParameter)
        result = cursor.fetchall()
        res = []
        for item in result:
            res.append(item)
        print("find Fn返回的res： ", res)
        return res

    except Exception as ex:
        print("find Fn：查詢失敗...")
        print(f"來自DB的錯誤訊息：{ex}")
        return False

@connectionDecorator
def update(cursor, connection, queryStr: str, queryParameter: tuple):
    try:
        cursor.execute(queryStr, queryParameter)
        connection.commit()
        print(f"update Fn：更新成功！")
        return True
    except Exception as ex:
        print(f"update Fn：更新失敗，以下是來自DB的錯誤訊息:\n{ex}")
        return False

@connectionDecorator
def delete(cursor, connection, queryStr: str, queryParameter: tuple):
    try:
        cursor.execute(queryStr, queryParameter)
        connection.commit()           
        print("delete：交易完成")
        return True
    except Exception as ex:
        print("delete：交易失敗")
        print(f"來自DB的錯誤訊息：{ex}")
        return False


# queryString = "SELECT * FROM member wh｀ere name = %s"
# find(queryString, ("Joey",))

#verify return一個list，裡面裝一個tuple。
#result[{id: , name:, username: }]
def verify(username: str, password: str):
    qureyString = "SELECT id,name, username FROM member where username = %s and password = %s"
    result = find(qureyString, (username, password))
    print(f"verify接收到的查詢結果：{result}")
    if(result):
        return result
    else:
        return None

def createMember(name :str, username :str, password :str):
    queryStr = "INSERT INTO member(name, username, password) VALUES(%s,%s,%s)"
    queryArags = (name, username, password)
    try:
        status = insert_data(queryStr, queryArags)
        if(status):
            print("新增會員成功！")
            return True
    except Exception as ex:
        print("新增會員失敗")
        return False

#getComment會return一個json格式的物件
#內容包含兩個字典{ "userInfo": {...}, "msg": [{}. {}. {}]}  
def getComment(count: int):
    qureyStr = "SELECT member.id, member.name, message.time, message.content, message.id as msg_id FROM member JOIN message ON member.id = message.member_id ORDER BY message.id DESC LIMIT 5 OFFSET %s;"
    count = (count,)
    queryResult = find(qureyStr, count)
    res = msgJsonMaker(queryResult)
    return res

def searchMsg(member_name):
    queryStr = "SELECT member.id, member.name, message.time, message.content, message.id as msg_id FROM member JOIN message ON member.id = message.member_id WHERE member.name = %s ORDER BY message.id DESC;"
    queryArgs = (member_name,)
    queryResult = find(queryStr, queryArgs)
    print(f"searchMsg Fn：取得的queryResult為：{queryResult}")
    res = msgJsonMaker(queryResult)
    print(f"searchMsg Fn：轉換後的queryResult為\n{res}")
    return res


def insertMsg(id, content):
    queryStr = "INSERT INTO message(member_id, content) VALUES(%s,%s)"
    queryArgs = (id, content)
    try:
        status = insert_data(queryStr, queryArgs)
        if(status):
            print("inserMsg Fn：新增留言成功！")
            return True
    except Exception as ex:
        print("inserMsg Fn：新增留言失敗")
        print(ex)    
        return False
    # try:
    #     cursor.execute(qureyStr, qureyValue)
    #     connection.commit()
    # except Exception as ex:
    #     print(f"message新增失敗，錯誤訊息：{ex}")

def msgJsonMaker(queryResult: list):
    print("Json Maker收到的資訊：\n", queryResult)
    transform = []
    for data in queryResult:
        #data格式為：{'id': 2, 'name': 'Joey', 'time': datetime.datetime(2022, 6, 18, 0, 0), 'content': 'Hi here is Joey'}
        date = data["time"].date()        
        date = date.isoformat()
        transform.append({
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
    res["msg"] = transform
    res = json.dumps(res, ensure_ascii=False)
    print("-----------------JsonMaker回傳結果-------------------\n", res)
    return res

def searchUsername(username):
    queryStr = "SELECT id,name,username FROM member where username = %s"    
    queryArgs = (username,)
    result = find(queryStr, queryArgs)
    print(f"searchUsername Fn： 查詢結果為 '{result}'")
    if(result):
        return result
    else:
        return None

def updateName(new_name):
    queryStr = "UPDATE member SET name = %s where username = %s"
    queryArgs = (new_name, session["username"])
    print(f"update Fn：\n更新目標：{session['username']}\n更新名稱：{new_name}")
    status = update(queryStr, queryArgs)
    if(status):
        return True
    else:
        return False
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
        print(f"data = {data}")
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
        status = createMember(name, username, password)
        if(status):
            return redirect("/")
        else:
            return render_template("error.html", message = "發生未知的錯誤")

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
    res = json.dumps(res, ensure_ascii=False)
    return res

@app.route("/deleteMessage/", methods=["POST"])
def deleteMessage():
    data = request.json
    verify_id = data["user_id"]
    msg_id = data["msg_id"]
    queryStr = f"DELETE FROM message where id = %s"
    queryArgs = (msg_id,)
    if(int(verify_id) == session["id"]):
        print("驗證通過，執行刪除Fn")
        try:
            status = delete(queryStr, queryArgs)
            print(f"刪除id = '{msg_id}'成功")
            return True
        except Exception as ex:
            print(f"刪除id = '{msg_id}'失敗\n來自DB的錯誤訊息：{ex}")
            return False
    else:
        print("驗證失敗....")
        return False

@app.route("/searchMemberMsg/<member_name>")
def searchMemberMsg(member_name):
    print(f"searchMemberMsg route：要搜尋的人為'{member_name}'")
    try:
        result = searchMsg(member_name)
        print("searchMemberMsg route：搜尋成功")
        print(f"搜尋結果為：{result}")
    except:
        print("searchMemberMsg route: 搜尋留言失敗")

    print("searchMemberMsg route：轉換JSON\n", result)
    return result

@app.route("/api/member", methods=["GET", "PATCH"])
def apiMember():
    print("========================================================")
    if not "status" in session:
        return json.dumps({"data": None})
    contentType = request.headers.get("Content-Type","")
    print("API Member route： http header = ", contentType)
    if(contentType=="application/json"):
        new_name = request.json
        status = updateName(new_name["name"])
        if(status):
            return json.dumps({"ok": True})
        else:    
            return json.dumps({"error": True})
    else:
        target = request.args.get("username")
        print(f"api member route：前端發來的target為 '{target}'")
        result = searchUsername(target)
        print(f"apiMember route：取得的name為{result}, type = {type(result)}")
        if(result):
            result = result[0]
            result = {
                "data": {
                    "id":result["id"],
                    "name":result["name"],
                    "username": result["username"]
                }
            }
            jsonData = json.dumps(result, ensure_ascii=False)
            print("apiMember route：回傳的JSON為", jsonData)
            return jsonData
        else:
            return json.dumps({"data": None})


app.run(port=3000, debug=True, use_reloader=True, threaded=True)


