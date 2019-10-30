#File handling utilities

def readBlacklist():
    noreply = []
    out = open("noreply.txt",mode = 'r',encoding = 'utf-8')
    line = out.readline()
    while line:
        noreply.append(int(line))
        line = out.readline()
    out.close()
    return noreply

def updateBlacklist(x):
    out = open("noreply.txt",mode = 'w',encoding = 'utf-8')
    for y in x:
        out.write(str(y)+"\n")
    out.close()

def readToken():
    read = open("TOKEN.txt",mode = 'r',encoding = 'utf-8')
    token = read.readline()
    read.close()
    return token

def shift(arr, index, direction = 1):
    _list = arr[:] #arr must be sliced otherwise python will set them equal by reference rather than value
    if direction == 0: 
        print("direction cannot be zero: shift()")
        return
    if direction > 0:
        for i in range(len(_list) - 2, index - 1, -1):
            _list[i + 1] = _list[i][:]
    elif direction < 0:
        for i in range(index, len(_list) - 2):
            _list[i] = _list[i+1][:]
    return _list