import time
count = 0
print(count)
a = 0
for i in range(1,32):
    start = time.time()
    count +=1
    process = round(count/32,2)*100
    print(process)
    if count == 31:
        print(100)
    else:
        print(process)
    time.sleep(1)
    end = time.time()

    s = end-start

    a += s

    print(s)
    print(type(s))
    print(int(a))
    print(type(a))