import base64,codecs,sys

def encodeString(str):
    base64string= base64.b64encode(str)
    return codecs.encode(base64string[::-1], 'rot13')
def decodeString(str):
    reversedbase64string= codecs.encode(str, 'rot13')
    base64string = reversedbase64string[::-1]
    return base64.b64decode(base64string)

cryptoResult=decodeString(sys.argv[1])
print (cryptoResult)