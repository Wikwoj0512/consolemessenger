from fbchat import Client
from fbchat.models import *
import sys,_thread, threading, time
from multiprocessing import Process
import subprocess as sp, os, subprocess,msvcrt
last=0
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
threadslast=[]
threadsupdate=[]
end=False
height=0
def exitcode():
    global end
    end=True
    client.logout()
messageslast={}
threadusers={}
writing=[]
current=0
def collect():
    global writing, end
    writing = []
    while not end:
        text = msvcrt.getwch()
        if text == "\b":
            writing = writing[:-1]
        elif text=="\r":
            send()
        else:
            writing.append(text)
def send():
    global last, writing, current, threadusers,messages,height, threadsupdate
    text="".join(writing)
    writing=[]
    if text=="^end": exitcode()
    if text=="^exit":current,writing,height=0,[],0
    if text=="^up" and current!=0: height+=1
    if text == "^dn" and current != 0 and height>0:
        height -= 1
        if height==0:
            if current.name in threadsupdate: threadsupdate.remove(current.name)

    if text[0]=='^':
        if len(text[1:])==16:
            try:
                messages=[]
                current=client.fetchThreadInfo(text[1:])[text[1:]]
                if current.name in threadsupdate: threadsupdate.remove(current.name)
                if current.type==ThreadType.USER:
                    threadusers[current.uid]=current.name
                else:
                    for user in client.fetchAllUsersFromThreads([current]):
                        threadusers[user.uid]=user.name
                threadusers[client.uid] = "You"
                messages = client.fetchThreadMessages(thread_id=current.uid,  limit=25*(height+1))[height*25:]
                # messages.reverse()
                height=0
                print("dolaczono")
            except:
                print("nie znaleziono wątku")
        elif len(text[1:])<3:
            try:
                messages=[]
                current=client.fetchThreadList(limit=20)[int(text[1:])]
                if current.name in threadsupdate: threadsupdate.remove(current.name)
                if current.type==ThreadType.USER:
                    threadusers[current.uid]=current.name
                else:
                    for user in client.fetchAllUsersFromThreads([current]):
                        threadusers[user.uid]=user.name
                threadusers[client.uid]="You"
                messages = client.fetchThreadMessages(thread_id=current.uid, limit=25*(height+1))[height*25:]
                height=0
                print("dolaczono")

            except:
                print("nie udało sie dolaczyc")
        return
    else:
        if not current==0:
            thread=current
            try:
                client.sendMessage(text, thread.uid, thread.type)
                last=(thread.uid,thread.name)
                print(f"You sent message to {thread.name}: {text}")
            except:
                pass

def onmessage(message_object, author_id, thread_id, thread_type):
    global last,marker, threadsupdate, messages, threadslast, messageslast, height
    threadslast = client.fetchThreadList(limit=20)
    thread=client.fetchThreadInfo(thread_id)[thread_id]
    if messageslast:
        messageslast[thread.uid] = message_object.text
    if current.name in threadsupdate and height<1: threadsupdate.remove(current.name)
    if( thread.name not in threadsupdate and thread_id!=current.uid) or height>0:
        threadsupdate.append(thread.name)
    if current!=0:
        if current.uid==thread_id:
            if messages:
                message = client.fetchThreadMessages(thread_id=thread_id, limit=25 * (height + 1))[height * 25] if height >0 else message_object
                messages.insert(0,message)
                messages=messages[:-1]
            else:
                messages = client.fetchThreadMessages(thread_id=thread_id, limit=25*(height+1))[height*25:]


class CustomClient(Client):
    def onMessage(self, message_object, author_id, thread_id, thread_type, **kwargs):
        onmessage(message_object, author_id, thread_id, thread_type)


def printer():
    global writing, current, client, threadsupdate,end, messages,threadusers,threadslast, messageslast, height
    while not end:
        try:
            print(" ".join( threadsupdate))
            if current == 0:
                height=0
                messages=False
                threadsupdate=[]
                if not threadslast:
                    threadslast = client.fetchThreadList(limit=20)
                if not messageslast:
                    for thread in threadslast:
                        messageslast[thread.uid]=client.fetchThreadMessages(thread_id=thread.uid, limit=1)[0].text
                i=0
                for thread in threadslast:
                    # print(thread)
                    # print(messageslast[thread]):
                    print(f"({thread.type} {thread.uid}, {i}) {thread.name}  last message: {messageslast[thread.uid]}")
                    i+=1
            else:
                thread=current
                print(" "*20+thread.name, height)
                if not messages:
                    messages = client.fetchThreadMessages(thread_id=thread.uid,limit=25*(height+1))[height*25:]
                for index, message in list(enumerate(messages))[::-1]:
                    if message.replied_to: print(f"\n[{index+(height*25)}] (reply to: {message.replied_to.text}): {threadusers[message.author]}: {message.text}")
                    else: print(f"\n[{index+(height*25)}] {threadusers[message.author]}: {message.text}")
            print("write: ","".join(writing))
            if current!=0:
                i=0
                for thread in threadslast[:10]:
                    print(f"({thread.type} {thread.uid}, {i}) {thread.name}  last message: {messageslast[thread.uid]}")
                    i += 1
            time.sleep(0.05)
            os.system("cls")
        except Exception as e:
            print(e)


username = input("nazwa użytkownika: ")
passwd = input('hasło')
client = CustomClient(username, passwd)
t = threading.Thread(target=client.listen)
t.start()
t2 = threading.Thread(target=collect)
t2.start()
t3 = threading.Thread(target=printer)
t3.start()