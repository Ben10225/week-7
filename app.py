from flask import Flask, render_template, redirect, request, session, jsonify 
from mysql.connector import pooling
from mysql_pwd import sqlPwd
import json
import base64

app = Flask(__name__, static_folder="public", static_url_path="/")
app.debug = True

app.secret_key="anytxt"


def connectPool():
  connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host='localhost',
                                                user='root',
                                                database='week7',
                                                password=sqlPwd())
  connection_object = connection_pool.get_connection()
  return connection_object

# mycursor = connection_pool.cursor()
selectUid = "SELECT name FROM users WHERE uid=%s"
insertSql = "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)"
signUpSelectSql = "SELECT * FROM users WHERE username=%s"
msgSql = "INSERT INTO message (name_id, msg) VALUES (%s, %s)"
showMsgSql = "SELECT u.name, m.msg, m.time FROM users AS u INNER JOIN message As m ON u.uid=m.name_id ORDER BY m.time DESC"
showMsgParamsSql = ()
signInSelectSql = "SELECT * FROM users WHERE username=%s and password=%s"
msgUidSelectSql = "SELECT uid FROM users WHERE name=%s"
updateUid = "UPDATE users SET name=%s WHERE uid=%s"



def decoded_session(session, status):
  session = session.split("=")[1]
  base64_message = session
  base64_message = base64_message.split(".")[0] + "==="
  msg = base64.urlsafe_b64decode(base64_message).decode("utf-8") 
  msg = msg.split(":")[1]
  if status == "logout":
    msg = msg[1:-2]
  if status == "login":
    msg = msg[:-1]
  return msg



# 首頁
@app.route("/")
def index():
  return render_template("index.html")

# 會員頁
@app.route("/member")
def member():
  uid = session["uid"]
  if not uid:
    return redirect("/")

  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(selectUid, (uid,))
  name = mycursor.fetchone()[0]

  mycursor.execute(showMsgSql)
  msgs = mycursor.fetchall()
  mycursor.close()
  db.close()
  time = []
  for i in msgs:
    s = str(i[2]).split(" ")[1][:5]
    time.append(s)
  return render_template("member.html", user=name, msgs=msgs, time=time, len=len(time))


# 錯誤頁
@app.route("/error")
def error():
  err = request.args.get("message", "輸入錯誤")
  return render_template("error.html", message=err)


# 註冊
@app.route("/signup", methods=["POST"])
def signup():
  name = request.json["name"]
  username = request.json['username']
  password = request.json['password']
  if name == "" or username == "" or password == "":
    return {"result": "請輸入註冊資訊"}

  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(signUpSelectSql, (username, ))
  exists = mycursor.fetchone()

  if exists:
    mycursor.close()
    db.close()
    return {"result": "帳號已存在"}
  else:
    val = (name, username, password)
    mycursor.execute(insertSql, val)
    db.commit()
    mycursor.close()
    db.close()
    return {"result": "OK"}


# 登入
@app.route("/signin", methods=["POST"])
def sign():
  username = request.json['username']
  password = request.json['password']
  if username == "" or password == "":
    return {"result": "請輸入登入資訊"}

  params = (username, password)

  db = connectPool()
  mycursor = db.cursor(dictionary=True) 
  mycursor.execute(signInSelectSql, params)
  exists = mycursor.fetchone()
  mycursor.close()
  db.close()

  if not exists:
    return {"result": "帳號或密碼輸入錯誤"}
  
  session["uid"] = exists["uid"]
  return {"result": "OK"}
  


# 登出
@app.route("/signout")
def signout():
  session["uid"] = False
  # session.clear()
  return redirect("/")


# 留言
@app.route("/message", methods=["POST"])
def message():
  uid = session["uid"]
  msg = request.json["msg"]
  if not uid:
    return {"routeName": "message", "feedback": "無登入狀態"}

  if not msg:
    return {"routeName": "message", "feedback": "請輸入文字"}

  val = (uid, msg)

  # 寫入
  db = connectPool()
  mycursor = db.cursor()
  mycursor.execute(msgSql, val)
  db.commit()
  mycursor.close()
  db.close()
  return {"routeName": "message", "feedback": "留言完成"}



# 查詢會員
@app.route("/query", methods=["POST"])
def query():
  uid = session["uid"]
  username = request.json["msg"]
  if not uid:
    return {"routeName": "query", "feedback": "無登入狀態"}

  if not username:
    return {"routeName": "query", "feedback": "請輸入查詢姓名"}

  db = connectPool()
  mycursor = db.cursor(dictionary=True) 
  mycursor.execute(signUpSelectSql, (username, ))
  exists = mycursor.fetchone()
  mycursor.close()
  db.close()
  if exists:
    return {"routeName": "query", "feedback": "查詢成功", "data": {"name": exists["name"], "username": exists["username"]}}
  else:
    return {"routeName": "query", "feedback": "查詢失敗", "data": None}



# 更改姓名
@app.route("/modify", methods=["PATCH"])
def modify():
  uid = session["uid"]
  msg = request.json["msg"]

  if not uid:
    return {"routeName": "modify", "feedback": "無登入狀態"}

  if not msg:
    return {"routeName": "modify", "feedback": "請輸入更新姓名"}
    
  db = connectPool()
  mycursor = db.cursor(dictionary=True)
  mycursor.execute(selectUid, (uid,))
  name = mycursor.fetchone()["name"]

  if name == msg:
    mycursor.close()
    db.close()
    return {"routeName": "modify", "feedback": "更新名字請與原本不同"}

  val = (msg, uid)
  mycursor.execute(updateUid, val)
  db.commit()
  mycursor.close()
  db.close()

  return {"routeName": "modify", "feedback": "更新成功", "newName": msg, "oldName": name}


# API
@app.route("/api/member", methods=["GET", "PATCH"])
def get_api():
  # GET
  if request.method == "GET":
    session = request.headers.get('Cookie')
    if not session:
      return jsonify({"data": None})
    params = decoded_session(session, "logout")
    if params == "als":
      return jsonify({"data": None})

    username = request.args.get("username", "")
    db = connectPool()
    mycursor = db.cursor(dictionary=True) 
    mycursor.execute(signUpSelectSql, (username, ))
    exists = mycursor.fetchone()
    mycursor.close()
    db.close()

    if exists:
      result = {
        "data" :{
          "id": exists["uid"],
          "name": exists["name"],
          "username": exists["username"]
        }
      }
    else:
      result = {
        "data": None,
      }
    return jsonify(result)
  
  # PATCH
  if request.method == "PATCH":
    session = request.headers.get('Cookie')
    if not session:
      return jsonify({"data": None})
    params = decoded_session(session, "logout")
    if params == "als":
      return jsonify({"error": True})

    uid = decoded_session(session, "login")

    db = connectPool()
    mycursor = db.cursor(dictionary=True)

    mycursor.execute(selectUid, (uid,))
    name = mycursor.fetchone()["name"]

    data = request.json
    if data["name"] != name:
      result = {
        "ok": True,
      }
    else:
      result = {
        "error": True,
      }
    
    val = (data["name"], uid)
    mycursor.execute(updateUid, val)
    db.commit()
    mycursor.close()
    db.close()

    return jsonify(result)



app.run(port=3000)

