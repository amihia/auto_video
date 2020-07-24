import json
import tkinter as tk
import tkinter.colorchooser
from PIL import Image,ImageFont,ImageDraw
from aip import AipSpeech
import os
import sys
import cv2
import eyed3
from moviepy.editor import VideoFileClip,AudioFileClip,CompositeAudioClip,concatenate_videoclips

# 加载配置
def load_setting():

    global setting

    print('读取配置文件')
    setting_json=_read("setting.json")
    if (setting_json):
        setting=json.loads(setting_json)

# 保存配置
def save_setting():

    setting['color']['R']=r.get()
    setting['color']['G']=g.get()
    setting['color']['B']=b.get()
    setting['position']=position.get()
    setting['_len']=_len.get()
    setting['APP_ID']=APP_ID.get()
    setting['API_KEY']=API_KEY.get()
    setting['SECRET_KEY']=SECRET_KEY.get()

    with open("setting.json",'w') as f:
        f.write(json.dumps(setting,indent=4, separators=(',', ': ')))
    print("配置保存成功")

# 清理残留文件
def _clear():

    print('清理上次残留文件')
    if(os.path.exists("frame")):
        for i in os.listdir("frame"):
            os.remove("frame/"+i)
    else:
        os.mkdir("frame")

    if(os.path.exists("sound")):
        for i in os.listdir("sound"):
            os.remove("sound/"+i)
    else:
        os.mkdir("sound")

    if(os.path.exists("video")):
        for i in os.listdir("video"):
            os.remove("video/"+i)
    else:
        os.mkdir("video")

# 文件读取
def _read(path):

    try:
        f=open(path,"r",encoding="utf-8")
        x=f.read()
        f.close()
        return x
    except:
        print('读取'+path+'失败')
        return 0

# 颜色选择
def choose_color():

    a1 = tkinter.colorchooser.askcolor(color='red', title='选择字体颜色')
    r.set(int(a1[0][0]))
    g.set(int(a1[0][1]))
    b.set(int(a1[0][2]))

# 逐帧合成
def create_frame(num,player_name,text):
    
    # 立绘
    try:
        player= Image.open("img/"+player_name+".png")
    except:
        if(player_name=="kp"):
            player= Image.open("img/default/kp.png")
        else:
            player= Image.open("img/default/pc.png")

    # 背景
    try:
        bg= Image.open("img/bg.jpg")
    except:
        bg= Image.open("img/default/bg.jpg")
    # 语音合成
    client = AipSpeech(setting["APP_ID"], setting["API_KEY"], setting["SECRET_KEY"])
    try:
        result = client.synthesis(text,'zh', 1,setting['character'][player_name])
    except: 
        result = client.synthesis(text,'zh', 1)

    if not isinstance(result, dict):
        with open(r'sound/'+str(num)+'.mp3', 'wb') as f:
            f.write(result)
    else:
        _print("语音合成出错")
        sys.exit()

    # 对话框与背景大小调整  
    dhk= Image.open("img/default/dhk"+str(dhk_num.get())+".png")
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
    draw.text((int(bgx/30),int(bgy/60*setting["position"])),player_name,font=_font)

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
    color=tuple(setting['color'].values())
    for i in range(len(text)):
        draw.text((int(bgx/30),int(bgy/60*(setting["position"]+8+i*4))),text[i],color,font=_font)
    
    # 保存图片 
    hk.save("frame/"+str(num)+".jpg")

def create_video(lenlist):
    fourcc=cv2.VideoWriter_fourcc("D","I","V","X")
    img=cv2.imread("frame/0.jpg")
    imgInfo = img.shape
    size = (imgInfo[1],imgInfo[0])
    video=cv2.VideoWriter("video/video.avi",fourcc,1,size)
    for i in range(len(lenlist)):
        img=cv2.imread("frame/"+str(i)+".jpg")
        for j in range(lenlist[i]):
            video.write(img)
    video.release()

def audio_add(lenlist):

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

# 无GUI生成
def begin():

    _clear()

    save_setting()

    msg=_read("text.txt")
    if(msg=="error"):
        print("打开text.txt出错")
        return

    try:
        msg=msg.split("\n\n")
        num=len(msg)
        for i in range(len(msg)):
            msg[i]=msg[i].split("\n")
    except:
        print("text.txt格式错误")
        return

    # 逐帧合成
    print("开始合成，一共有"+str(len(msg))+"帧")
    for i in range(len(msg)):
        print("开始合成第"+str(i+1)+"帧")
        create_frame(i,msg[i][0],msg[i][1])
    #填充len_list
    lenlist=[]
    for i in range(num):
        voice_file = eyed3.load("sound/"+str(i)+".mp3")
        secs = voice_file.info.time_secs
        secs=int(secs)+1
        lenlist.append(secs)

    create_video(lenlist)
    print("视频合成完成，开始添加音轨")

    audio_add(lenlist)

    print("合成成功")
    
    l8=tk.Label(root,text="合成成功,视频zc0.avi——zc"+str(len(lenlist)-1)+".avi已保存到video文件夹中\n再次使用请重启程序",bg="white",height=8,width=67)
    l8.place(x=10,y=250)

if __name__== '__main__':

    gui_flag=1

    load_setting()

    if gui_flag:

        root=tk.Tk()

        r=tk.IntVar()
        r.set(setting['color']['R'])
        g=tk.IntVar()
        g.set(setting['color']['G'])
        b=tk.IntVar()
        b.set(setting['color']['B'])

        position=tk.IntVar()
        position.set(setting['position'])

        _len=tk.IntVar()
        _len.set(setting['_len'])

        dhk_num=tk.IntVar()
        dhk_num.set(setting['dhk_num'])

        APP_ID = tk.StringVar()
        APP_ID.set(setting['APP_ID'])
        API_KEY = tk.StringVar()
        API_KEY.set(setting['API_KEY'])
        SECRET_KEY = tk.StringVar()
        SECRET_KEY.set(setting['SECRET_KEY'])

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
    else:
        begin()
