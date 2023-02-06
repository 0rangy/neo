import random
import json
import os
import hashlib
import time
    

#token
def genSessionID():
    allStuff = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.&#$1234567890"
    toReturn = ''.join(random.choice(allStuff) for i in range(69))
    return toReturn.replace(" ", "")


def createUser(user, pwdHash, emailHash, bdate, uname, sessiongenerated, acctype, school):
    user1 = user.replace("\\","")
    user2 = user1.replace("\"","")
    uname1 = uname.replace("\\","")
    uname2 = uname1.replace("\"","")
    if len(user) >= 25:
      return False
    print("createuser 1")
    if not os.path.exists("users/" + user + ".json"):
        sessionid = sessiongenerated
        f = open("users/" + user2 + ".json", "w+")
        print("creatUser 2")
        userDict2 = {
          "name": uname2,
          "hashedEmail": str(emailHash),
          "hashedPwd": str(pwdHash),
          "sessionCookie": hashlib.sha3_512(sessionid.encode()).hexdigest().replace(" ", ""),
          "bdate": str(bdate),
          "accountType": acctype,
          "school": school,
          "classes": stringifyJSON({"classes":[],"destinations":[]})
        }
        userDict3 = str(userDict2).replace("'","\"")
        f.write(userDict3.replace("\\\\\"","\\\""))
        f.truncate()
        return True
    else:
        print("user exists already")
        return False


def stringifyJSON(string):
  string2 = str(string).replace("'","\"")
  string3 = string2.replace("\"","\\\"")
  return string3

def newAssignment(classid, assignment, description, duedate, attachment):
  print("new Assignment")
  with open("classes/" + classid + ".json", "r") as f:
    data = json.load(f)
    assigndata = json.loads(data["assignments"])
    titles = assigndata["assignments"]
    titles.append(assignment)
    assigndata["assignments"] = titles
    assigndata[assignment] = {
      "description": str(description),
      "duedate": str(duedate),
      "attachment": attachment,
      "href": "/class/" + classid + "/assignment/" + assignment
    }
    data["assignments"] = str(assigndata).replace("'","\"")
  with open("classes/" + classid + ".json" , "w") as g:
    json.dump(data, g)
    g.truncate()


def changeSessionID(user):
  newses = genSessionID()
  g = open("users/" + user + ".json", "r+")
  data = json.load(g)
  print("First sesionchange data:\n\n" + str(data))
  data["sessionCookie"] = hashlib.sha3_512(newses.encode()).hexdigest().replace(" ", "")
  g.truncate()
  with open("users/" + user + ".json", "w+") as f:
    json.dump(data, f)
    print("Final changesesion data:\n\n" + str(data))
    print(data)
    f.trucate()
  return newses


def logOutUser(user):
    x = open("users/" + user + ".json", "r+")
    xread = x.read()
    x.truncate()
    with open("users/" + user + ".json", "w+") as f:
        data = json.loads(xread)
        data["sessionCookie"] = None
        json.dump(data, f)
        f.truncate()
    

def checkIfLoggedIn(user, session):
    with open("users/" + user + ".json", "r+") as f:
        data = json.load(f)
        if data["sessionCookie"] == hashlib.sha3_512(session.encode()).hexdigest():
            return True
        else:
            return False
        f.truncate()


def changePwd(user, newPwd1Hash, newPwd2Hash, oldPwdHash, flaskses):
    g = open("users/"+ user + ".json","r+")
    data = json.load(g)
    oldPwdHashInternal = data["hashedPwd"]
    print("First changepwd data: \n\n" + str(data))
    if oldPwdHash == oldPwdHashInternal:
      if newPwd1Hash == newPwd2Hash:
        data["hashedPwd"] = newPwd1Hash
        print("old pwd hash: " + oldPwdHash + "\nNew ped hash:" + newPwd1Hash)
        with open("users/" + user + ".json", "w+") as f:    
          json.dump(data, f)
          print("Final changepwd Data: \n\n" + str(data))
          f.truncate()
          time.sleep(2)
          changeSessionID(user)
          return True
      else:
        return False
        print("new pwd no match")
    else:
      return False
      print("old pwd wrong")
        
    g.truncate()
    
