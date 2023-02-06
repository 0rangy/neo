#Work in progress

#from jwt import PyJWT
import jwt
import time


def createToken(user, secretKey):

  payloadData = {
    'sub': user,
    'name': user,
    'iss': 'toddle.ddns.net',
    'iat': time.time(),
    'exp': 1  #(time.time() + 1209600)
  }

  token = jwt.encode(payload=payloadData, key=secretKey)

  return token


def parseToken(tokn, secret):
  tokan = tokn

  headerData = jwt.get_unverified_header(tokn)

  try:
    tokenData = jwt.decode(tokn, algorithms=[
      headerData['alg'],
    ])

    if (int(tokenData['exp']) <= time.time()):
      return 'exp'  #f'it was expired, timesigned: {tokenData["iat"]}, expiretime: {tokenData["exp"]}, currenttime: {time.time()}'

    else:
      return tokenData['sub']

  except jwt.exceptions.ExpiredSignatureError:  #jwt.InvalidTokenError:
    return 'ok it actually expires'


#print(parseToken(createToken('testUser'), 'my_super_secret'))

#{'id': tokenData['sub'], 'validity': True}

print(parseToken(createToken('testUser', 'my_super_secret'), 'my_super_secret'))
