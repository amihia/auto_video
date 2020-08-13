#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import ttk
from PIL import Image, ImageFont, ImageDraw
from aip import AipSpeech
import os
import cv2
import eyed3
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips


# class type_system_info:
#    def __init__(self, name):
#        self.name = name
#
# system_info = type_system_info(os.name)

# 加载配置
def load_setting():
    global setting

    print('读取配置文件')
    try:
        fp = open("setting.json", 'r', encoding='utf-8')
        setting_json = fp.read()
        fp.close()
    except:
        print('读取配置文件失败')
    setting = json.loads(setting_json)


# 加载剧本
def load_log(path):
    print('读取剧本')
    try:
        fp = open(path, 'r', encoding='utf-8')
        text = fp.read()
        fp.close()

        # 分割文本
        try:
            text = text.split("\n\n")
            num = len(text)
            bg_list = []
            i = 0
            while i < num:
                text[i] = text[i].split("\n")
                if text[i][0] == 'bg':
                    num -= 1
                    bg_list.append(text[i][1])
                    text.pop(i)
                    text[i] = text[i].split("\n")
                else:
                    bg_list.append(bg_list[i - 1])
                i += 1
            return num, text, bg_list
        except:
            print("剧本格式错误")
    except:
        print('读取剧本失败')


# 保存配置
def save_setting():
    for i in tv.get_children():
        values = tv.item(i, 'values')
        try:
            setting['character'][values[0]]['sound']['spd'] = int(values[1])
            setting['character'][values[0]]['sound']['per'] = int(values[2])
            setting['character'][values[0]]['sound']['pid'] = int(values[3])
        except:
            setting['character'][values[0]] = {}
            setting['character'][values[0]]['sound'] = {}
            setting['character'][values[0]]['sound']['spd'] = int(values[1])
            setting['character'][values[0]]['sound']['per'] = int(values[2])
            setting['character'][values[0]]['sound']['pid'] = int(values[3])

    # 删除多余的行
    name_judge = {}
    for i in setting['character']:
        name_judge[i] = 1
        for j in tv.get_children():
            values = tv.item(j, 'values')
            if (values[0] == i):
                name_judge[i] = 0
                break
    for i in name_judge:
        if name_judge[i]: setting['character'].pop(i)

    setting['color']['R'] = r.get()
    setting['color']['G'] = g.get()
    setting['color']['B'] = b.get()
    setting['position'] = position.get()
    setting['_len'] = _len.get()
    setting['APP_ID'] = APP_ID.get()
    setting['API_KEY'] = API_KEY.get()
    setting['SECRET_KEY'] = SECRET_KEY.get()

    with open("setting.json", 'w') as f:
        f.write(json.dumps(setting, indent=4, separators=(',', ': ')))
    print("配置保存成功")


# 清理残留文件
def file_clear():
    print('清理上次残留文件')
    if (os.path.exists("frame")):
        for i in os.listdir("frame"):
            os.remove("frame/" + i)
    else:
        os.mkdir("frame")

    if (os.path.exists("sound")):
        for i in os.listdir("sound"):
            os.remove("sound/" + i)
    else:
        os.mkdir("sound")

    if (os.path.exists("video")):
        for i in os.listdir("video"):
            os.remove("video/" + i)
    else:
        os.mkdir("video")


# 颜色选择
def choose_color():
    ac = colorchooser.askcolor(color='red', title='选择字体颜色')
    r.set(int(ac[0][0]))
    g.set(int(ac[0][1]))
    b.set(int(ac[0][2]))


def select_file():
    global log_file
    log_file = filedialog.askopenfilenames(title="请选择剧本文件", filetypes=[("Text", "*.txt"), ("All Files", "*")])[0]


# 添加角色
def new_row():
    tv.insert('', len(tv.get_children()), values=("pc", 0, 5, 5, 1))
    tv.update()


# 删除角色
def delete_row():
    try:
        tv.delete(tv.selection()[0])
        tv.update()
    except:
        pass


# 编辑单元格
def set_cell_value(event):
    for item in tv.selection():
        item_text = tv.item(item, "values")

    column = tv.identify_column(event.x)  # 列
    row = tv.identify_row(event.y)  # 行

    try:
        cn = int(str(column).replace('#', ''))
        rn = int(str(row).replace('I', ''))
        edit = tk.Text(root, width=10, height=1)
        edit.place(x=20 + (cn - 1) * 100, y=165 + rn * 20)

        def save_edit(event):
            tv.set(item, column=column, value=edit.get(0.0, "end").split('\n')[0])
            edit.destroy()

        def quit_edit(event):
            edit.destroy()

        edit.bind('<Return>', save_edit)
        edit.bind('<Leave>', quit_edit)
    except:
        pass


# 逐帧合成
def create_frame(num, player_name, text, bg):
    # 立绘
    try:
        try:
            character = Image.open("image/" + player_name + ".png")
            player_name = player_name.split("(")[0]
            player_name = player_name.split("（")[0]
        except:
            player_name = player_name.split("(")[0]
            player_name = player_name.split("（")[0]
            character = Image.open("image/" + player_name + ".png")
    except:
        if (player_name == "kp"):
            player = Image.open("img/default/kp.png")
        else:
            player = Image.open("img/default/pc.png")

    # 背景
    try:
        bg = Image.open("img/" + bg + ".jpg")
    except:
        bg = Image.open("img/default/bg.jpg")
    # 语音合成
    client = AipSpeech(setting["APP_ID"], setting["API_KEY"], setting["SECRET_KEY"])
    try:
        result = client.synthesis(text, 'zh', 1, setting['character'][player_name]['sound'])
    except:
        result = client.synthesis(text, 'zh', 1)

    if not isinstance(result, dict):
        with open('sound/' + str(num) + '.mp3', 'wb') as f:
            f.write(result)
    else:
        print("语音合成出错")

    # 对话框与背景大小调整  
    dialog_frame = Image.open("img/default/dhk" + str(dhk_num.get()) + ".png")
    bgx, bgy = bg.size
    dialog_frame_x, dialog_frame_y = dialog_frame.size
    dialog_frame = dialog_frame.resize((bgx, int(0.75 * bgy)), Image.BILINEAR)  # 固定对话框Y坐标起始于画面3/4处
    dialog_frame_x, dialog_frame_y = dialog_frame.size
    _font = ImageFont.truetype('simhei.ttf', int(bgy / 20))

    main_canvas = bg
    playerx, playery = player.size
    player = player.resize((int((bgy / 6 * 5) / playery * playerx), int(bgy / 6 * 5)), Image.BILINEAR)
    playerx, playery = player.size
    try:
        main_canvas.paste(player, (int(bgx / 30), int(bgy - playery - (bgy / 6))), mask=player.split()[3])
    except:
        main_canvas.paste(player, (int(bgx / 30), int(bgy - playery - (bgy / 6))))
    main_canvas.paste(dialog_frame, (0, bgy - dialog_frame_y), mask=dialog_frame.split()[3])
    draw = ImageDraw.Draw(main_canvas)
    draw.text((int(bgx / 30), int(bgy / 60 * setting["position"])), player_name, font=_font)

    textlen = setting['_len']
    if (len(text) >= textlen):
        formatted_text = []
        line_num = int(len(text) / textlen) + 1
        for i in range(line_num):
            if ((i + 1) * textlen > len(text) - 1):
                formatted_text.append(text[i * textlen:])
            else:
                formatted_text.append(text[i * textlen:(i + 1) * textlen])
        text = formatted_text
    else:
        text = [text]
    color = tuple(setting['color'].values())
    for i in range(len(text)):
        draw.text((int(bgx / 30), int(bgy / 60 * (setting["position"] + 8 + i * 4))), text[i], color, font=_font)

    # 保存图片 
    main_canvas.save("frame/" + str(num) + ".jpg")


def create_video(lenlist):
    fourcc = cv2.VideoWriter_fourcc("D", "I", "V", "X")
    img = cv2.imread("frame/0.jpg")
    imgInfo = img.shape
    size = (imgInfo[1], imgInfo[0])
    video = cv2.VideoWriter("video/video.avi", fourcc, 1, size)
    for i in range(len(lenlist)):
        img = cv2.imread("frame/" + str(i) + ".jpg")
        for j in range(lenlist[i]):
            video.write(img)
    video.release()


def audio_add(lenlist):
    video = VideoFileClip('video/video.avi')
    result = []
    for i in range(len(lenlist)):
        if (i != 0):
            video_ = video.subclip(sum(lenlist[0:i]), sum(lenlist[0:i]) + lenlist[i])
            print([sum(lenlist[0:i]), sum(lenlist[0:i]) + lenlist[i]])
        else:
            video_ = video.subclip(0, lenlist[i])
        audio = AudioFileClip("sound/" + str(i) + ".mp3")
        video_ = video_.set_audio(audio)
        subvideo = video_
        subvideo.write_videofile("video/zc" + str(i) + ".avi", codec="png")
        # result.append(subvideo)
    # print(len(result))
    # result=concatenate_videoclips(result)
    # result.write_videofile("video/result.avi",codec="png")


# 无GUI生成
def begin():
    file_clear()

    if gui_flag: save_setting()

    log = load_log(log_file)
    num = log[0]
    msg = log[1]
    bg_list = log[2]

    # 逐帧合成
    print("开始合成，一共有" + str(len(msg)) + "帧")
    for i in range(num):
        print("开始合成第" + str(i + 1) + "帧")
        create_frame(i, msg[i][0], msg[i][1], bg_list[i])
    # 填充len_list
    lenlist = []
    for i in range(num):
        voice_file = eyed3.load("sound/" + str(i) + ".mp3")
        secs = voice_file.info.time_secs
        secs = int(secs) + 1
        lenlist.append(secs)

    create_video(lenlist)
    print("视频合成完成，开始添加音轨")

    audio_add(lenlist)

    print("合成成功")


if __name__ == '__main__':

    gui_flag = 1

    log_file = "text.txt"

    load_setting()

    if gui_flag:

        root = tk.Tk()

        r = tk.IntVar()
        r.set(setting['color']['R'])
        g = tk.IntVar()
        g.set(setting['color']['G'])
        b = tk.IntVar()
        b.set(setting['color']['B'])

        position = tk.IntVar()
        position.set(setting['position'])

        _len = tk.IntVar()
        _len.set(setting['_len'])

        dhk_num = tk.IntVar()
        dhk_num.set(setting['dhk_num'])

        APP_ID = tk.StringVar()
        APP_ID.set(setting['APP_ID'])
        API_KEY = tk.StringVar()
        API_KEY.set(setting['API_KEY'])
        SECRET_KEY = tk.StringVar()
        SECRET_KEY.set(setting['SECRET_KEY'])

        l1 = tk.Label(root, text="参数设置")
        l1.place(x=10, y=10)

        l2 = tk.Label(root, text="文字颜色")
        l2.place(x=10, y=50)
        l21 = tk.Label(root, text="R", width=2)
        l21.place(x=10, y=90)
        l22 = tk.Label(root, text="G", width=2)
        l22.place(x=60, y=90)
        l23 = tk.Label(root, text="B", width=2)
        l23.place(x=120, y=90)
        e21 = tk.Entry(root, width=4, textvariable=r)
        e22 = tk.Entry(root, width=4, textvariable=g)
        e23 = tk.Entry(root, width=4, textvariable=b)
        e21.place(x=30, y=90)
        e22.place(x=80, y=90)
        e23.place(x=140, y=90)

        l3 = tk.Label(root, text="文字上下坐标")
        l3.place(x=200, y=50)
        e3 = tk.Entry(root, width=10, textvariable=position)
        e3.place(x=200, y=90)

        l4 = tk.Label(root, text="每行文字数")
        l4.place(x=300, y=50)
        e4 = tk.Entry(root, width=10, textvariable=_len)
        e4.place(x=300, y=90)

        l5 = tk.Label(root, text="对话框模板（1-3）")
        l5.place(x=400, y=50)
        e5 = tk.Entry(root, width=10, textvariable=dhk_num)
        e5.place(x=400, y=90)

        # 语音合成参数
        l6 = tk.Label(root, text="APP_ID")
        l6.place(x=10, y=130)
        e6 = tk.Entry(root, width=55, textvariable=APP_ID)
        e6.place(x=90, y=130)

        l7 = tk.Label(root, text="API_KEY")
        l7.place(x=10, y=170)
        e7 = tk.Entry(root, width=55, textvariable=API_KEY)
        e7.place(x=90, y=170)

        l7 = tk.Label(root, text="SECRET_KEY")
        l7.place(x=10, y=210)
        e7 = tk.Entry(root, width=55, textvariable=SECRET_KEY)
        e7.place(x=90, y=210)

        b1 = tk.Button(root, text="开始合成", command=begin)
        b1.place(x=420, y=400)

        b2 = tk.Button(root, text="选择颜色", command=choose_color)
        b2.place(x=90, y=45)

        # 表格
        columns = ("角色名", "语速", "发音人", "音调")
        tv = ttk.Treeview(root, height=6, show="headings", columns=columns)

        for i in columns:
            tv.heading(i, text=i)  # 显示表头
            tv.column(i, width=100, anchor='center')  # 表示列,不显示

        tv.place(x=10, y=250)
        sb = ttk.Scrollbar(root, command=tv.yview)
        sb.pack(side="right", fill="y")
        tv.configure(yscrollcommand=sb.set)

        # 写入数据
        ans = 1
        for i in setting['character']:
            tv.insert('', ans,
                      values=(i, setting['character'][i]['sound']['spd'], setting['character'][i]['sound']['per'],
                              setting['character'][i]['sound']['pid']))
            ans += 1

        # 双击左键进入编辑
        tv.bind('<Double-1>', set_cell_value)

        b3 = ttk.Button(root, text='添加角色', width=15, command=new_row)
        b3.place(x=20, y=403)

        b4 = ttk.Button(root, text='删除角色', width=15, command=delete_row)
        b4.place(x=150, y=403)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="文件", menu=filemenu)
        filemenu.add_command(label="导入文件", command=select_file)

        root.config(menu=menubar)
        root.geometry('530x440')
        root.title("跑团自动视频生成")
        root.resizable(width=False, height=False)
        root.mainloop()
    else:
        begin()
