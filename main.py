import tkinter as tk
from PIL import Image,ImageFont,ImageDraw
from aip import AipSpeech
import os
import sys
import cv2
import eyed3
from moviepy.editor import VideoFileClip,AudioFileClip,CompositeAudioClip,concatenate_videoclips

num=0
work_num=0

msg=""
sound=""
font_bg=0
lenlist=[]

def _read(index):
    try:
        f=open(index,"r",encoding="utf-8")
        x=f.read()
        f.close()
        return x
    except:
        return "error"

def create_frame(player_name,text):
    global lenlist
    global num,font_bg,client
    global msg,sound,font_bg
    try:
        player= Image.open("img/players/"+player_name+".png")
    except:
        if(player_name=="kp"):
            player= Image.open("zc/kp.png")
        else:
            player= Image.open("zc/pc.png")

    try:
        bg= Image.open("img/bg.jpg")
    except:
        bg= Image.open("zc/bg.jpg")

    soundjdg=0
    for i in range(len(sound)):
        if(sound[i][0]==player_name):
            spd=sound[i][1]
            per=sound[i][2]
            pit=sound[i][3]
            soundjdg=1
            break
    if(soundjdg==0):
        spd=6
        per=1
        pit=7

    result  = client.synthesis(text, 'zh', 1, {'vol': 5,'spd':spd,'per':per,'pit':pit})
    if not isinstance(result, dict):
        with open(r'sound/'+str(num)+'.mp3', 'wb') as f:
            f.write(result)
    else:
        _print("语音合成出错")
        sys.exit()
        
    dhk= Image.open("zc/dhk"+str(dhk_num.get())+".png")
    bgx,bgy=bg.size
    dhkx,dhky=dhk.size
    dhk=dhk.resize((bgx,int(bgx/dhkx*dhky/5*4)),Image.BILINEAR)
    dhkx,dhky=dhk.size
    _font=ImageFont.truetype('simhei.ttf',int(bgy/20))

    hk=bg
    playerx,playery=player.size
    player=player.resize((int((bgy/6*5)/playery*playerx),int(bgy/6*5)),Image.BILINEAR)
    playerx,playery=player.size
    try:
        hk.paste(player,(int(bgx/30),int(bgy-playery-(bgy/6))),mask=player.split()[3])
    except:
        hk.paste(player,(int(bgx/30),int(bgy-playery-(bgy/6))))
    hk.paste(dhk,(0,bgy-dhky),mask=dhk.split()[3])
    draw=ImageDraw.Draw(hk)
    color=[r.get(),g.get(),b.get()]
    draw.text((int(bgx/30),int(bgy/60*font_bg)),player_name,(color[0],color[1],color[2]),font=_font)

    textlen=_len.get()
    if(len(text)>=textlen):
        text0=[]
        numn=int(len(text)/textlen)+1
        for i in range(numn):
            if((i+1)*textlen>len(text)-1):
                text0.append(text[i*textlen:])
            else:
                text0.append(text[i*textlen:(i+1)*textlen])
        text=text0
    else:
        text=[text]

    for i in range(len(text)):
        draw.text((int(bgx/30),int(bgy/60*(font_bg+8+i*4))),text[i],(color[0],color[1],color[2]),font=_font)
    hk.save("frame/"+str(num)+".jpg")

    num+=1
def create_video(lenlist):
    fourcc=cv2.VideoWriter_fourcc("D","I","V","X")
    img=cv2.imread("frame/0.jpg")
    imgInfo = img.shape
    size = (imgInfo[1],imgInfo[0])
    video=cv2.VideoWriter("video/video.avi",fourcc,1,size)
    for i in range(num):
        img=cv2.imread("frame/"+str(i)+".jpg")
        for j in range(lenlist[i]):
            video.write(img)
    video.release()

def audio_add():
    global lenlist
    video = VideoFileClip('video/video.avi')
    result=[]
    for i in range(len(lenlist)):
        if(i!=0):
            video_=video.subclip(sum(lenlist[0:i]),sum(lenlist[0:i])+lenlist[i])
            print([sum(lenlist[0:i]),sum(lenlist[0:i])+lenlist[i]])
        else:
            video_=video.subclip(0,lenlist[i])
        audio=AudioFileClip("sound/"+str(i)+".mp3")
        video_=video_.set_audio(audio)
        subvideo=video_
        subvideo.write_videofile("video/zc"+str(i)+".avi",codec="png")
        #result.append(subvideo)
    #print(len(result))
    #result=concatenate_videoclips(result)
    #result.write_videofile("video/result.avi",codec="png")
def begin():
    global lenlist,work_num
    global msg,sound,font_bg
    msg=_read("text/text.txt")

    if(msg=="error"):
        print("打开text.txt出错")
        return
    sound=_read("text/sound.txt")
    if(sound=="error"):
        print("打开sound.txt出错")
        return
    
    font_bg=position.get()

    try:
        msg=msg.split("\n\n")
        for i in range(len(msg)):
            msg[i]=msg[i].split("\n")
    except:
        print("text.txt格式错误")
        return
    try:
        sound=sound.split("\n")
        for i in range(len(sound)):
            sound[i]=sound[i].split(" ")
        for i in range(len(sound)):
            for j in range(1,len(sound[i])):
                sound[i][j]=int(sound[i][j])
    except:
        print("sound.txt格式错误")
        return

    for i in os.listdir("frame"):
        os.remove("frame/"+i)

    for i in os.listdir("sound"):
        os.remove("sound/"+i)

    for i in os.listdir("video"):
        os.remove("video/"+i)

    print("开始合成，一共有"+str(len(msg))+"帧")
    for i in range(len(msg)):
        print("开始合成第"+str(i+1)+"帧")
        create_frame(msg[i][0],msg[i][1])
    lenlist=[]
    for i in range(num):
        voice_file = eyed3.load("sound/"+str(i)+".mp3")
        secs = voice_file.info.time_secs
        secs=int(secs)+1
        lenlist.append(secs)
    print(lenlist)
    create_video(lenlist)
    print("视频合成完成，开始添加音轨")
    audio_add()
    print("合成成功")
    
    l8=tk.Label(root,text="合成成功,视频zc0.avi——zc"+str(len(lenlist)-1)+".avi已保存到video文件夹中\n再次使用请重启程序",bg="white",height=8,width=67)
    l8.place(x=10,y=250)


root=tk.Tk()

r=tk.IntVar()
r.set(255)
g=tk.IntVar()
g.set(255)
b=tk.IntVar()
b.set(255)
position=tk.IntVar()
position.set(33)
_len=tk.IntVar()
_len.set(23)
dhk_num=tk.IntVar()
dhk_num.set(1)

APP_ID = tk.StringVar()
API_KEY = tk.StringVar()
SECRET_KEY = tk.StringVar()



client = AipSpeech(APP_ID.get(), API_KEY.get(), SECRET_KEY.get())

l1=tk.Label(root,text="参数设置")
l1.place(x=10,y=10)

l2=tk.Label(root,text="文字颜色")
l2.place(x=10,y=50)
l21=tk.Label(root,text="R",width=2)
l21.place(x=10,y=90)
l22=tk.Label(root,text="G",width=2)
l22.place(x=60,y=90)
l23=tk.Label(root,text="B",width=2)
l23.place(x=120,y=90)
e21=tk.Entry(root,width=4,textvariable=r)
e22=tk.Entry(root,width=4,textvariable=g)
e23=tk.Entry(root,width=4,textvariable=b)
e21.place(x=30,y=90)
e22.place(x=80,y=90)
e23.place(x=140,y=90)

l3=tk.Label(root,text="文字上下坐标")
l3.place(x=200,y=50)
e3=tk.Entry(root,width=10,textvariable=position)
e3.place(x=200,y=90)

l4=tk.Label(root,text="每行文字数")
l4.place(x=300,y=50)
e4=tk.Entry(root,width=10,textvariable=_len)
e4.place(x=300,y=90)

l5=tk.Label(root,text="对话框模板（1-3）")
l5.place(x=400,y=50)
e5=tk.Entry(root,width=10,textvariable=dhk_num)
e5.place(x=400,y=90)

#语音合成参数
l6=tk.Label(root,text="APP_ID")
l6.place(x=10,y=130)
e6=tk.Entry(root,width=55,textvariable=APP_ID)
e6.place(x=90,y=130)

l7=tk.Label(root,text="API_KEY")
l7.place(x=10,y=170)
e7=tk.Entry(root,width=55,textvariable=API_KEY)
e7.place(x=90,y=170)

l7=tk.Label(root,text="SECRET_KEY")
l7.place(x=10,y=210)
e7=tk.Entry(root,width=55,textvariable=SECRET_KEY)
e7.place(x=90,y=210)

#信息框
l8=tk.Label(root,text="",bg="white",height=8,width=67)
l8.place(x=10,y=250)

b1=tk.Button(root,text="开始合成",command=begin)
b1.place(x=420,y=400)

root.geometry('520x440')
root.title("跑团自动视频生成")
root.mainloop()
