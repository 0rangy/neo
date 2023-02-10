import flask
import os
import json
import hashlib
import classes
import werkzeug.utils
import ast

#its ok ill do it

#keys = db.keys()
ALLOWED_EXTENSIONS = {'txt', 'pdf' , 'doc', 'docx', 'odt', 'csv', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'tif', 'tiff', 'gif', 'svg', 'mp3', 'm4a', 'wav', 'mp4', 'mov', 'm4v', 'avi', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'ppt', 'pptx', 'odp', 'key', '7z', 'pkg', 'rar', 'tar.gz', 'z', 'zip','html'}

app = flask.Flask(__name__, subdomain_matching = True)

app.config['UPLOAD_FOLDER'] = "simulatedDirectories"


def allowed_file(filename):
    return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def serveFile(fileDirectory):
  return flask.send_file(fileDirectory, as_attachment=True)



@app.route("/delacc")
def delacc():
  try:
    cookies = flask.request.cookies
    user = cookies.get("userID")
    session = cookies.get("sessionID")
    with open("users/" + user + ".json", "r+") as f:
      data = json.load(f)
      if data["sessionCookie"] == hashlib.sha3_512(session.encode()).hexdigest():
        os.remove("users/" + user + ".json")
        return flask.redirect("/")
      else:
        print("session no match")
        return flask.redirect("/signin")    
  except:
    print("error")
    return flask.redirect("/myaccount")


@app.route("/favicon.ico")
def favicon():
  return flask.send_file("images/NeoLogo.png")





@app.route('/')
def home():
  return flask.render_template("index.html")

#Amaury keep this routing, this is spare so i can test shit




@app.route('/test')
def test():
  
  return flask.send_file('images/neo_black.png', as_attachment=True)





@app.route('/urmom')
def index():
  return flask.render_template("subdomain.html")
#ook then





@app.route("/hashing.js")
def hashing():
  return flask.send_file("code/hashing.js")



@app.route('/uploads/<school>/<clas>/<name>')
def download_file(school, clas, name):
    return flask.send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], school, clas), name)


@app.route('/fileSubmit', methods = ['GET', 'POST'])
def fileSubmit():
  if flask.request.method == 'POST':
   form = flask.request.form
   clas = form.get("class")
   school = form.get("school")
   file = flask.request.files["file"]
   print(str(form))
   print(str(file))
   if file.filename == '':
      print('No selected file')
      return flask.redirect(flask.request.url)
   if allowed_file(file.filename):
      filename = werkzeug.utils.secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], school, clas, filename))
      return flask.redirect("/uploads/" + school + "/" + clas + "/" + filename)

  return flask.render_template('fileSubmit.html')

@app.route("/class/<classid>")
def redir(classid):
  return flask.redirect("/class/" + classid + "/stream")


@app.route("/class/<classid>/new", methods=["POST", "GET"])
def new(classid):
  if flask.request.method == "POST":
    form = flask.request.form
    type = form.get("type")
    print(classid)
    if type == "assignment":
      return flask.render_template("newassignment.html", classid=classid)
    if type == "resource":
      return flask.render_template("newresource.html", classid=classid)
    if type == "post":
      return flask.render_template("newpost.html", classid=classid)
    else:
      return flask.redirect("/class/" + classid + "/new")
  elif flask.request.method == "GET":
    print(classid)
    return flask.render_template("classnew.html", classid=classid)

@app.route("/class/<classid>/del", methods=["POST", "GET"])
def dele(classid):
  if flask.request.method == "POST":
    form = flask.request.form
    type = form.get("type")
    print(classid)
    if type == "assignment":
      return flask.render_template("delassignment.html", classid=classid)
    if type == "resource":
      return flask.render_template("delresource.html", classid=classid)
    if type == "post":
      return flask.render_template("delpost.html", classid=classid)
    else:
      return flask.redirect("/class/" + classid + "/del")
  elif flask.request.method == "GET":
    print(classid)
    return flask.render_template("classdel.html", classid=classid)





@app.route("/adminpanel", methods=["POST", "GET"])
def adminpanel():
  if flask.request.method == "GET":
    try:
      cookies = flask.request.cookies
      sessionid = cookies.get("sessionID")
      userid = cookies.get("userID")
      if not classes.checkIfLoggedIn(userid, sessionid):
        return flask.redirect("/signin")
      with open("users/" + userid + ".json") as f:
        data = json.load(f)
        if data["accountType"] != "admin":
          return flask.redirect("/myaccount")
        userslist = os.listdir("users")
        classeslist = os.listdir("simulatedDirectories/" + data["school"])
        classeslistnames = []
        usernames = []
        for clas in classeslist:
          with open("classes/" + clas + ".json") as f:
            clasdata = json.load(f)
            classeslistnames.append(clasdata["name"])
        for user in userslist:
            print(user)
            with open("users/" + user, "r+") as f:
                userdata = json.load(f)
                if userdata["school"] == data["school"]:
                    usernames.append(userdata["name"])
        return flask.render_template("adminpnl.html",userslist=usernames, school=data["school"], classeslist=classeslistnames)
    except:
      print("oops")
      return flask.redirect("/myaccount")





@app.route("/class/<classid>/newpost", methods=["POST"])
def newpost(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if not classes.checkIfLoggedIn(userid, sessionid):
      return flask.redirect("/signin")
    form = flask.request.form
    title = form.get("title")
    body = form.get("body")
    with open("classes/" + classid + ".json", "r+") as f:
      data = json.load(f)
      if data["teacher"] == userid:
        streamdata = json.loads(str(data["stream"]))
        print(str(data))
        print(str(streamdata))
        titles = streamdata["announcements"]
        descs = streamdata["description"]
        dests =streamdata["destinations"]
        titles.append(title)
        descs.append(body)
        dests.append("#")
        streamdata["announcements"] = titles
        streamdata["descriptions"] = descs
        streamdata["destinations"] = dests
        print(str(streamdata))
        data["stream"] = str(streamdata).replace("'","\"")
        print(str(data))
        f.truncate()
      with open("classes/" + classid + ".json" , "w") as g:
        json.dump(data, g)
      return flask.redirect("/class/" + classid + "/stream")
  except:
    print("newpost error")
    return flask.redirect("/class/" + classid)




@app.route("/class/<classid>/newresource", methods=["POST"])
def newres(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if classes.checkIfLoggedIn(userid, sessionid):
      form = flask.request.form
      file = flask.request.files["file"]
      print(str(file))
      if file.filename == '':
        print('No selected file')
      if allowed_file(form.get("filename")):
        with open("classes/" + classid + ".json") as f:
          data = json.load(f)
          if data["teacher"] == userid:
            school = data["school"]
            clas = classid
            filename = werkzeug.utils.secure_filename(form.get("filename"))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], school, clas, filename))
            return flask.redirect("/class/" + classid + "/resources")
          else:
            return flask.redirect("/class/" + classid)
      else:
        return flask.redirect("/class/" + classid)
    else:
      return flask.redirect("/signin")
  except:
    return flask.redirect("/classes")



    
@app.route("/class/<classid>/stream")
def classstream(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if classes.checkIfLoggedIn(userid, sessionid):
      with open("classes/" + classid + ".json") as f:
        data = json.load(f)
        classname = data["name"]
        stream3 = data["stream"]
        stream2 = stream3.replace("'","")
        teacher = data["teacher"]
        if teacher == userid:
          return flask.render_template("teacherstream.html", classname = classname, stream =stream2, classid=classid)
        else:
          return flask.render_template("classstream.html", classname = classname, stream =stream2, classid=classid)
    else:
      print(sessionid)
      print(userid)
      return flask.redirect("/signin")
  except:
    print("Error")
    return flask.redirect("/signin")



@app.route("/class/<classid>/newassignment", methods=['POST'])
def newassign(classid):
  #try:
    cookies = flask.request.cookies
    form = flask.request.form
    title = form.get("title")
    body = form.get("body")
    print(str(form))
    print(flask.request.files)
    duedate = form.get("duedate")
    userid = cookies.get("userID")
    sessionid = cookies.get("sessionID")
    if not classes.checkIfLoggedIn(userid, sessionid):
      return flask.redirect("/signin")
    with open("classes/" + classid + ".json", "r") as f:
      data = json.load(f)
      if data["teacher"] == userid:
        print("is teaacher")
        file = flask.request.files["file"]
        print(str(file))
        if file.filename == '':
          print('No selected file')
          fileurl = "#"
        if allowed_file(form.get("filename")):
          filename = werkzeug.utils.secure_filename(form.get("filename"))
          file.save(os.path.join(app.config['UPLOAD_FOLDER'], data["school"], classid, filename))
          fileurl = "/uploads/" + data["school"] + "/" + classid + "/" + filename
        classes.newAssignment(classid, title, body, duedate, fileurl)
        return flask.redirect("/class/" + classid + "/assignments")
      else:
        return flask.redirect("/class/" + classid + "/assignments")
  #except:
   # return flask.redirect("/classes")
    
      

@app.route("/class/<classid>/assignments")
def assignmentss(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if not classes.checkIfLoggedIn(userid, sessionid):
      return flask.redirect("/signin")
    with open("classes/" + classid + ".json") as f:
      data = json.load(f)
      teacher = data["teacher"]
      assignments1 = data["assignments"]
      assignments2 = assignments1.replace("'","")
    if teacher == userid:
      return flask.render_template("teacherassign.html", assignments = assignments2, classname = data["name"], classid = classid)
    else:
      return flask.render_template("classassign.html", assignments = assignments2, classname = data["name"], classid = classid)
  except:
    return flask.redirect("/classes")


@app.route("/class/<classid>/people")
def classpeople(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if classes.checkIfLoggedIn(userid, sessionid):
     print("Logged in")
     with open("classes/" + classid + ".json") as f:
      data = json.load(f)
      peoplelist = data["students"]
      namelist = []
      try:
        for person in peoplelist:
          with open("users/" + person + ".json") as g:
            data2 = json.load(g)
            namelist.append(data2["name"])
            print(data2["name"])
      except:
        namelist.append("An Erorr Occured")
      print("preturn here")
      return flask.render_template("classpeople.html", classid = classid, classname = data["name"], students = namelist)
    else:
      print("Not signed in")
      return flask.redirect("/signin")
  except:
    print("Error")
    return flask.redirect("/signin")


    


@app.route("/class/<classid>/resources")
def resources(classid):
  try:
    cookies = flask.request.cookies
    sessionid = cookies.get("sessionID")
    userid = cookies.get("userID")
    if not classes.checkIfLoggedIn(userid, sessionid):
      print("Not logged in")
      return flask.redirect("/signin")
    with open("classes/" + classid + ".json") as f:
      data = json.load(f)
      teacher = data["teacher"]
      school = data["school"]
      name = data["name"]
      files = os.listdir("simulatedDirectories/" + school + "/" + classid)
      print(files)
      if teacher == userid:
        return flask.render_template("teacherresources.html", resources=files, classname = name, classid=classid, school = school)
      else:
        return flask.render_template("classresources.html", resources=files, classname = name, classid=classid, school = school)
  except:
    return flask.redirect("/classes")

@app.route("/signin", methods=['GET', 'POST'])  # this get s called when someone gets
def loginget():
  success = flask.make_response(flask.redirect("/myaccount"))
    #this one simply is when a user clicks on the 'My account'
  if flask.request.method == 'GET':
    try:
      cookies = flask.request.cookies
      session = cookies.get("sessionID")
      userid = cookies.get("userID")
      with open("users/" + userid + ".json", "r") as f:
        data = json.loads(f.read())
        print("open json")
        if classes.checkIfLoggedIn(userid, session):
          print("return")
          return flask.redirect("/myaccount")
        else:
          print(hashlib.sha3_512(session.replace(" ", "").encode()).hexdigest())
          print(data["sessionCookie"])
          print("session no match user")
          return flask.render_template("signin.html", alert=False, alertxt="")
    except:
      print("error try")
      return flask.render_template("signin.html", alert=False, alertxt="")
  elif flask.request.method == 'POST':
    data = flask.request.form
    user = data.get("user")
    pwd = data.get("pwd")
    try:
      e = open("users/" + user + ".json", "r+")
      datas = json.load(e)
      passwordhash = datas["hashedPwd"]
      e.truncate()
      f= open("users/" + user + ".json", "w+")
      f.write("{}")
      f.truncate()
      print("post try start")
      with open("users/" + user + ".json", "r+") as f:
        if hashlib.sha3_512(pwd.encode()).hexdigest() == passwordhash:
          print("right password")
          newsess = classes.genSessionID()
          success.set_cookie("sessionID", newsess)
          success.set_cookie("userID", user)
          print("session",newsess)
          datas["sessionCookie"] = hashlib.sha3_512(newsess.encode()).hexdigest()
          json.dump(datas,f)
          f.truncate()
          return success
        else:
          json.dump(datas, f)
          print("worng password")
          return flask.render_template("signin.html", alert=True, alertxt="Something went wrong")
    except:
      print("error post try")
      return flask.render_template("signin.html", alert=True, alertxt="Something went wrong")





@app.route("/changepwd", methods=["GET","POST"])
def changepwd():
  cookies = flask.request.cookies
  if flask.request.method == "GET":
    try:
      user = cookies.get("userID")
      session = cookies.get("sessionID")
      with open("users/" + user + ".json", "r+") as f:
        data = json.load(f)
        if hashlib.sha3_512(session.encode()).hexdigest() == data["sessionCookie"]:
          return flask.render_template("changepwd.html", alert=False, alertxt="")
        else:
          return flask.redirect("/signin")
    except:
      return flask.redirect("/signin")
  if flask.request.method == "POST":
    try:
      user = cookies.get("userID")
      session = cookies.get("sessionID")
      with open("users/" + user + ".json", "r+") as f:
        data = json.load(f)
        if hashlib.sha3_512(session.encode()).hexdigest() == data["sessionCookie"]:
          data = flask.request.form
          oldpwd = data.get("oldpwd")
          newpwd1 = data.get("newpwd1")
          newpwd2 = data.get("newpwd2")
          if classes.changePwd(user,hashlib.sha3_512(newpwd1.encode()).hexdigest(),hashlib.sha3_512(newpwd2.encode()).hexdigest(),hashlib.sha3_512(oldpwd.encode()).hexdigest(), flask):
            return flask.redirect("/myaccount")
          else:
            return flask.redirect("/changepwd")
        else:
          return flask.redirect("/signin")
    except:
      return flask.redirect("/signin")
    
    






@app.route("/classes")
def aclasses():
  try:
    cookies = flask.request.cookies
    session = cookies.get("sessionID")
    user = cookies.get("userID")
    with open("users/" + user + ".json", "r+") as f:
      data = json.load(f)
      if data["accountType"] == "teacher" or data["accountType"] == "admin":
        newokok = True
      else:
        newokok = False
      if hashlib.sha3_512(session.encode()).hexdigest() == data["sessionCookie"]:
        return flask.render_template("classes.html", classes=str(data["classes"]), newok = newokok)
      else:
        return flask.redirect("/signin")
  except:
    return flask.redirect("/signin")
  

@app.route("/newclass", methods=["GET","POST"])
def newclass():
  if flask.request.method == "POST":
    #try:
      cookies = flask.request.cookies
      form = flask.request.form
      user = cookies.get("userID")
      session = cookies.get("sessionID")
      with open("users/" + user + ".json", "r+") as  f:
        data = json.load(f)
        school = data["school"]
        if data["sessionCookie"] == hashlib.sha3_512(session.encode()).hexdigest():
          if data["accountType"] == "teacher" or data["accountType"] == "admin":
            if os.path.exists(os.path.join("simulatedDirectories", school)):
              if os.path.exists(os.path.join("simulatedDirectories", school, form.get("classid"))):
                print("path exists")
                return flask.redirect("/newclass")
              else:
                if os.path.isfile(os.path.join("classes", form.get("classid") + ".json")):
                  print("class exists")
                  return flask.redirect("/newclass")
                os.mkdir(os.path.join("simulatedDirectories", school, form.get("classid")))
                with open("classes/" + form.get("classid") + ".json", "w+") as e:
                  users = form.get("students")
                  student = users.split(" ")
                  student.append(user)
                  classDict = {
                    "teacher": user,
                    "name": form.get("classname"),
                    "school": school,
                    "students": ast.literal_eval(str(student).replace("'","\"")),
                    "stream": classes.stringifyJSON({"announcements":[],"description":[],"destinations":[]}),
                    "assignments": classes.stringifyJSON({"assignments":[]})
                  }
                  classDict2 = str(classDict).replace("'","\"")
                  e.write(classDict2.replace("\\\\\"","\\\""))
                  e.truncate()
                  res = ast.literal_eval(str(student).replace("'", "\""))
                for stu in res:
                  print(stu)
                  with open("users/" + stu + ".json", "r+") as h:
                    datau = json.load(h)
                    classlist = json.loads(str(datau["classes"]))
                    clases = classlist["classes"]
                    dests = classlist["destinations"]
                    print(str(clases))
                    print(str(dests))
                    clases.append(form.get("classname"))
                    dests.append("class/" + form.get("classid"))
                    classlist["classes"] = clases
                    classlist["destinations"] = dests
                    datau["classes"] = str(classlist).replace("'", "\"")
                    h.truncate()
                  with open("users/"+ stu + ".json", "w") as g:
                   json.dump(datau, g)
                   print(str(datau))
                return flask.redirect("/classes")
            else:
              print("file exists")
              return flask.redirect("/newclass")
          else:
            print("not teacher or admin")
            return flask.redirect("/myaccount")
        else:
          print("wrong session id")
          return flask.redirect("/myaccount")
        f.truncate()
    #except:
     # print("error")
      #return flask.redirect("/myaccount")
  else:
    print("GET request")
    return flask.render_template("newclass.html")
      
              




@app.route("/myaccount")
def account():
  try:
    cookies = flask.request.cookies
    userid = cookies.get("userID")
    if os.path.exists("users/" + userid + ".json") and userid != None:
      try:
        with open("users/" + userid + ".json", "r+") as f:
          data = json.load(f)
          sessionHashed = data["sessionCookie"]
          session = cookies.get("sessionID")
          school = data["school"]
          acctype = data["accountType"]
          if hashlib.sha3_512(session.encode()).hexdigest() == sessionHashed:
            bdate = data["bdate"]
            namefull = data["name"]
            return flask.render_template("myaccount.html", namefull = namefull, bdate = bdate, username =userid, school = school, acctype = acctype)
          else:
            return flask.redirect("/signin")
      except:
        return flask.redirect("/signin")
    else:
      return flask.redirect("/signin")
  except:
    return flask.redirect("/signin")






@app.route("/logout")
def logout():
  try:
    resp = flask.make_response(flask.redirect("/"))
    cookies = flask.request.cookies
    username = cookies.get("userID")
    session = cookies.get("sessionID")
    with open("users/" + username + ".json") as f:
      data = json.load(f)
      if hashlib.sha3_512(session.encode()).hexdigest() == data["sessionCookie"]:
        classes.logOutUser(username)
        resp.delete_cookie("userID")
        resp.delete_cookie("sessionID")
    return resp
  except:
    return flask.redirect("/myaccount")








@app.route("/signup", methods=['GET', 'POST'])
def signup():
  if flask.request.method == 'GET':
    with open("code/schools.json", "r+") as f:
      data = json.load(f)
      return flask.render_template("signup.html", schools=data["schools"])
  if flask.request.method == 'POST':
    resp = flask.make_response(flask.redirect("/myaccount"))
    data = flask.request.form  
    user = data.get("user")
    name = data.get("namefull")
    pwd = data.get("pwd")
    bdate = data.get("bdate")
    email = data.get("email")
    acctype = data.get("type")
    school = data.get("school")
    pw_hash = hashlib.sha3_512(pwd.encode()).hexdigest()
    email_hash = hashlib.sha3_512(email.encode()).hexdigest()
    sessiongen = classes.genSessionID()
    if classes.createUser(user,pw_hash,email_hash,bdate, name, sessiongen, acctype, school):
      respready = True
      with open("users/" +user+".json", "r+") as f:
        data = json.load(f)
        resp.set_cookie("sessionID", sessiongen)
        resp.set_cookie("userID", user)
        f.truncate()
        if respready:
          return resp
        else:
          return flask.redirect("/signup")
    else:
      return flask.redirect("/signup")

app.run(host='0.0.0.0', port=81)
