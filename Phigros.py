from threading import Thread
from ctypes import windll
from os import chdir, environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str()
from os.path import exists, abspath, dirname
import webbrowser
import typing
import json
import sys
import time
import math

sys.excepthook = lambda *args: [print("^C"), windll.kernel32.ExitProcess(0)] if KeyboardInterrupt in args[0].mro() else sys.__excepthook__(*args)

from PIL import Image, ImageFilter
from pygame import mixer
import webcvapis

import Const
import Tool_Functions
import PhigrosGameObject
import rpe_easing

selfdir = dirname(sys.argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

if not exists("./PhigrosAssets"):
    while True:
        print("PhigrosAssets not found, please download it from https://github.com/qaqFei/PhigrosPlayer_PhigrosAssets")
        time.sleep(0.1)

mixer.init()
chaptersDx = 0.0
inMainUI = False
lastMainUI_ChaptersClickX = 0.0
lastLastMainUI_ChaptersClickX = 0.0
mainUI_ChaptersMouseDown = False
changeChapterMouseDownX = float("nan")
lastChangeChapterTime = float("-inf")
setting = PhigrosGameObject.Setting()

def Load_Chapters():
    global Chapters, ChaptersMaxDx
    jsonData = json.loads(open("./PhigrosAssets/chapters.json", "r", encoding="utf-8").read())
    Chapters = PhigrosGameObject.Chapters(
        [
            PhigrosGameObject.Chapter(
                name = chapter["name"],
                cn_name = chapter["cn-name"],
                o_name = chapter["o-name"],
                image = chapter["image"],
                songs = [
                    PhigrosGameObject.Song(
                        name = song["name"],
                        composer = song["composer"],
                        image = song["image"],
                        preview = song["preview"],
                        difficlty = [
                            PhigrosGameObject.SongDifficlty(
                                name = diff["name"],
                                level = diff["level"],
                                chart = diff["chart"]
                            )
                            for diff in song["difficlty"]
                        ]
                    )
                    for song in chapter["songs"]
                ]
            )
            for chapter in jsonData["chapters"]
        ]
    )
    
    ChaptersMaxDx = w * (len(Chapters.items) - 1) * (295 / 1920) + w * 0.5 - w * 0.875

def Load_Resource():
    global ButtonWidth, ButtonHeight
    global MainUIIconWidth, MainUIIconHeight
    global SettingUIOtherIconWidth, SettingUIOtherIconHeight
    global MessageButtonSize
    global JoinQQGuildBannerWidth, JoinQQGuildBannerHeight
    global JoinQQGuildPromoWidth, JoinQQGuildPromoHeight
    global SettingUIOtherDownIconWidth
    global SettingUIOtherDownIconHeight_Twitter, SettingUIOtherDownIconHeight_QQ, SettingUIOtherDownIconHeight_Bilibili
    
    Resource = {
        "logoipt": Image.open("./Resources/logoipt.png"),
        "warning": Image.open("./Resources/Start.png"),
        "phigros": Image.open("./Resources/phigros.png"),
        "AllSongBlur": Image.open("./Resources/AllSongBlur.png"),
        "facula": Image.open("./Resources/facula.png"),
        "collectibles": Image.open("./Resources/collectibles.png"),
        "setting": Image.open("./Resources/setting.png"),
        "ButtonLeftBlack": Image.open("./Resources/Button_Left_Black.png"),
        "ButtonRightBlack": None,
        "message": Image.open("./Resources/message.png"),
        "JoinQQGuildBanner": Image.open("./Resources/JoinQQGuildBanner.png"),
        "UISound_1": mixer.Sound("./Resources/UISound_1.wav"),
        "UISound_2": mixer.Sound("./Resources/UISound_2.wav"),
        "UISound_3": mixer.Sound("./Resources/UISound_3.wav"),
        "JoinQQGuildPromo": Image.open("./Resources/JoinQQGuildPromo.png"),
        "Arrow_Left": Image.open("./Resources/Arrow_Left.png"),
        "Arrow_Right_Black": Image.open("./Resources/Arrow_Right_Black.png"),
        "twitter": Image.open("./Resources/twitter.png"),
        "qq": Image.open("./Resources/qq.png"),
        "bilibili": Image.open("./Resources/bilibili.png"),
    }
    
    Resource["ButtonRightBlack"] = Resource["ButtonLeftBlack"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    
    imageBlackMaskHeight = 12
    imageBlackMask = Image.new("RGBA", (1, imageBlackMaskHeight), (0, 0, 0, 0))
    imageBlackMask.putpixel((0, 0), (0, 0, 0, 64))
    imageBlackMask.putpixel((0, 1), (0, 0, 0, 32))
    imageBlackMask.putpixel((0, 2), (0, 0, 0, 16))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 3), (0, 0, 0, 16))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 2), (0, 0, 0, 32))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 1), (0, 0, 0, 64))
    
    root.reg_img(imageBlackMask.resize((1, 500)), "imageBlackMask")
    root.reg_img(Resource["logoipt"], "logoipt")
    root.reg_img(Resource["warning"], "warning")
    root.reg_img(Resource["phigros"], "phigros")
    root.reg_img(Resource["AllSongBlur"], "AllSongBlur")
    root.reg_img(Resource["facula"], "facula")
    root.reg_img(Resource["collectibles"], "collectibles")
    root.reg_img(Resource["setting"], "setting")
    root.reg_img(Resource["ButtonLeftBlack"], "ButtonLeftBlack")
    root.reg_img(Resource["ButtonRightBlack"], "ButtonRightBlack")
    root.reg_img(Resource["message"], "message")
    root.reg_img(Resource["JoinQQGuildBanner"], "JoinQQGuildBanner")
    root.reg_img(Resource["JoinQQGuildPromo"], "JoinQQGuildPromo")
    root.reg_img(Resource["Arrow_Left"], "Arrow_Left")
    root.reg_img(Resource["Arrow_Right_Black"], "Arrow_Right_Black")
    root.reg_img(Resource["twitter"], "twitter")
    root.reg_img(Resource["qq"], "qq")
    root.reg_img(Resource["bilibili"], "bilibili")
        
    ButtonWidth = w * 0.10875
    ButtonHeight = ButtonWidth / Resource["ButtonLeftBlack"].width * Resource["ButtonLeftBlack"].height # bleft and bright size is the same.
    MainUIIconWidth = w * 0.0265
    MainUIIconHeight = MainUIIconWidth / Resource["collectibles"].width * Resource["collectibles"].height # or arr or oth w/h same ratio
    SettingUIOtherIconWidth = w * 0.01325
    SettingUIOtherIconHeight = SettingUIOtherIconWidth / Resource["Arrow_Right_Black"].width * Resource["Arrow_Right_Black"].height
    MessageButtonSize = w * 0.025
    JoinQQGuildBannerWidth = w * 0.2
    JoinQQGuildBannerHeight = JoinQQGuildBannerWidth / Resource["JoinQQGuildBanner"].width * Resource["JoinQQGuildBanner"].height
    JoinQQGuildPromoWidth = w * 0.61
    JoinQQGuildPromoHeight = JoinQQGuildPromoWidth / Resource["JoinQQGuildPromo"].width * Resource["JoinQQGuildPromo"].height
    SettingUIOtherDownIconWidth = w * 0.01725
    SettingUIOtherDownIconHeight_Twitter = SettingUIOtherDownIconWidth / Resource["twitter"].width * Resource["twitter"].height
    SettingUIOtherDownIconHeight_QQ = SettingUIOtherDownIconWidth / Resource["qq"].width * Resource["qq"].height
    SettingUIOtherDownIconHeight_Bilibili = SettingUIOtherDownIconWidth / Resource["bilibili"].width * Resource["bilibili"].height
    
    for chapter in Chapters.items:
        im = Image.open(f"./PhigrosAssets/{chapter.image}")
        chapter.im = im
        root.reg_img(im, f"chapter_{chapter.chapterId}_raw")
        root.reg_img(im.filter(ImageFilter.GaussianBlur(radius = (im.width + im.height) / 100)), f"chapter_{chapter.chapterId}_blur")
    
    with open("./Resources/font.ttf", "rb") as f:
        root.reg_res(f.read(),"PhigrosFont")
    root.load_allimg()
    for im in root._is_loadimg.keys(): # ...  create image draw cache
        root.create_image(im, 0, 0, 50, 50, wait_execute=True)
    root.clear_canvas(wait_execute = True)
    root.run_js_wait_code()
    root.run_js_code(f"loadFont('PhigrosFont',\"{root.get_resource_path("PhigrosFont")}\");")
    while not root.run_js_code("font_loaded;"):
        time.sleep(0.1)
    
    # i donot want to update webcvapis module ...
    root._regims.clear()
    root.shutdown_fileserver()
    Thread(target=root._file_server.serve_forever, args=(0.1, ), daemon=True).start()
    
    root.run_js_code(f"createChapterBlackGrd({h * (140 / 1080)}, {h * (1.0 - 140 / 1080)});")
    
    return Resource

def bindEvents():
    root.jsapi.set_attr("click", eventManager.click)
    root.run_js_code("_click = (e) => pywebview.api.call_attr('click', e.x, e.y);")
    root.run_js_code("document.addEventListener('mousedown', _click);")
    
    root.jsapi.set_attr("mousemove", eventManager.move)
    root.run_js_code("_mousemove = (e) => pywebview.api.call_attr('mousemove', e.x, e.y);")
    root.run_js_code("document.addEventListener('mousemove', _mousemove);")
    
    root.jsapi.set_attr("mouseup", eventManager.release)
    root.run_js_code("_mouseup = (e) => pywebview.api.call_attr('mouseup', e.x, e.y);")
    root.run_js_code("document.addEventListener('mouseup', _mouseup);")
    
    eventManager.regClickEventFs(mainUI_mouseClick, False)
    eventManager.regReleaseEvent(PhigrosGameObject.ReleaseEvent(mainUI_mouseRelease))
    eventManager.regMoveEvent(PhigrosGameObject.MoveEvent(mainUI_mouseMove))
    eventManager.regClickEventFs(changeChapterMouseDown, False)
    eventManager.regReleaseEvent(PhigrosGameObject.ReleaseEvent(changeChapterMouseUp))

def drawBackground():
    f, t = Chapters.aFrom, Chapters.aTo
    if f == -1: f = t # 最开始的, 没有之前的选择
    imfc, imtc = Chapters.items[f], Chapters.items[t]
    p = getChapterP(imtc)
    
    root.run_js_code(
        f"ctx.drawAlphaImage(\
            {root.get_img_jsvarname(f"chapter_{imfc.chapterId}_blur")},\
            0, 0, {w}, {h}, {1.0 - p}\
        );",
        add_code_array = True
    )   
    root.run_js_code(
        f"ctx.drawAlphaImage(\
            {root.get_img_jsvarname(f"chapter_{imtc.chapterId}_blur")},\
            0, 0, {w}, {h}, {p}\
        );",
        add_code_array = True
    )

def drawFaculas():
    for facula in faManager.faculas:
        if facula["startTime"] <= time.time() <= facula["endTime"]:
            state = faManager.getFaculaState(facula)
            sizePx = facula["size"] * (w + h) / 40
            root.run_js_code(
                f"ctx.drawAlphaImage(\
                    {root.get_img_jsvarname("facula")},\
                    {facula["x"] * w - sizePx / 2}, {state["y"] * h - sizePx / 2},\
                    {sizePx}, {sizePx},\
                    {state["alpha"] * 0.4}\
                );",
                add_code_array = True
            )

def getChapterP(chapter: PhigrosGameObject.Chapter):
    chapterIndex = Chapters.items.index(chapter)
    ef = rpe_easing.ease_funcs[0]
    atime = 1.0
    
    if chapterIndex == Chapters.aFrom:
        p = 1.0 - (time.time() - Chapters.aSTime) / atime
        ef = rpe_easing.ease_funcs[16]
    elif chapterIndex == Chapters.aTo:
        p = (time.time() - Chapters.aSTime) / atime
        ef = rpe_easing.ease_funcs[15]
    else:
        p = 0.0
    
    return ef(Tool_Functions.fixOutofRangeP(p))

def getChapterWidth(p: float):
    return w * (0.221875 + (0.5640625 - 0.221875) * p)

def getChapterToNextWidth(p: float):
    return w * (295 / 1920) + (w * 0.5 - w * (295 / 1920)) * p

def getChapterRect(dx: float, chapterWidth: float):
    return (
        dx, h * (140 / 1080),
        dx + chapterWidth, h * (1.0 - 140 / 1080)
    )

def drawChapterItem(item: PhigrosGameObject.Chapter, dx: float):
    p = getChapterP(item)
    if dx > w: return getChapterToNextWidth(p)
    chapterWidth = getChapterWidth(p)
    if dx + chapterWidth < 0: return getChapterToNextWidth(p)
    chapterImWidth = h * (1.0 - 140 / 1080 * 2) / item.im.height * item.im.width
    dPower = Tool_Functions.getDPower(chapterWidth, h * (1.0 - 140 / 1080 * 2), 75)
    
    chapterRect = getChapterRect(dx, chapterWidth)
    
    root.run_js_code(
        f"ctx.drawDiagonalRectangleClipImage(\
            {", ".join(map(str, chapterRect))},\
            {root.get_img_jsvarname(f"chapter_{item.chapterId}_raw")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, {p}\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.drawDiagonalRectangleClipImage(\
            {", ".join(map(str, chapterRect))},\
            {root.get_img_jsvarname(f"chapter_{item.chapterId}_blur")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, {1.0 - p}\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.drawDiagonalRectangleClipImage(\
            {", ".join(map(str, chapterRect))},\
            {root.get_img_jsvarname("imageBlackMask")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, 1.0\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.drawRotateText2(\
            '{processStringToLiteral(item.name)}',\
            {chapterRect[2] - dPower * chapterWidth - (w + h) / 150}, {chapterRect[3] - (w + h) / 150},\
            -75, 'rgba(255, 255, 255, {0.95 * (1.0 - Tool_Functions.PhigrosChapterNameAlphaValueTransfrom(p))})', '{(w + h) / 50}px PhigrosFont',\
            'left', 'bottom'\
        );",
        add_code_array = True
    )
    
    root.create_text(
        chapterRect[2] - (w + h) / 50,
        chapterRect[1] + (w + h) / 90,
        item.cn_name,
        font = f"{(w + h) / 75}px PhigrosFont",
        textAlign = "right",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {p ** 2})", # ease again
        wait_execute = True
    )
    
    root.create_text(
        chapterRect[0] + dPower * chapterWidth + (w + h) / 125,
        chapterRect[1] + (w + h) / 90,
        item.o_name,
        font = f"{(w + h) / 115}px PhigrosFont",
        textAlign = "left",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {p ** 2})", # ease again
        wait_execute = True
    )
    
    playButtonRect = (
        chapterRect[2] - dPower * chapterWidth + PlayButtonDPower * PlayButtonWidth - PlayButtonWidth, chapterRect[3] - PlayButtonHeight,
        chapterRect[2] - dPower * chapterWidth + PlayButtonDPower * PlayButtonWidth, chapterRect[3]
    )
    
    playButtonTriangle = (
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.17, playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * (4 / 11),
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.17, playButtonRect[3] - (playButtonRect[3] - playButtonRect[1]) * (4 / 11),
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.25, playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * 0.5
    )
    
    playButtonAlpha = Tool_Functions.PhigrosChapterPlayButtonAlphaValueTransfrom(p)
    
    if playButtonAlpha != 0.0:
        root.run_js_code(
            f"ctx.drawDiagonalRectangleNoFix(\
                {", ".join(map(str, playButtonRect))},\
                {PlayButtonDPower}, 'rgba(255, 255, 255, {playButtonAlpha})'\
            );",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.drawTriangleFrame(\
                {", ".join(map(str, playButtonTriangle))},\
                'rgba(0, 0, 0, {playButtonAlpha})',\
                {(w + h) / 800}\
            );",
            add_code_array = True
        )
        
        root.create_text(
            playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.35,
            playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * 0.5,
            "P L A Y",
            font = f"{(w + h) / 65}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = f"rgba(49, 49, 49, {playButtonAlpha})",
            wait_execute = True
        )
    
    dataAlpha = Tool_Functions.PhigrosChapterDataAlphaValueTransfrom(p)
    
    if dataAlpha != 0.0:
        root.create_text(
            chapterRect[0] + chapterWidth * 0.075,
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "All",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * 0.075,
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            f"{len(item.songs)}",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Clear",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 2),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Full Combo",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 2),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 3),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Phi",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        root.create_text(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 3),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
    
    return getChapterToNextWidth(p)

def drawChapters():
    chapterX = w * 0.034375 + chaptersDx
    for chapter in Chapters.items:
        chapterX += drawChapterItem(chapter, chapterX)

def drawButton(buttonName: typing.Literal["ButtonLeftBlack", "ButtonRightBlack"], iconName: str, buttonPos: tuple[float, float]):
    root.run_js_code(
        f"ctx.drawImage(\
           {root.get_img_jsvarname(buttonName)},\
           {buttonPos[0]}, {buttonPos[1]}, {ButtonWidth}, {ButtonHeight}\
        );",
        add_code_array = True
    )
    
    centerPoint = (0.35, 0.395) if buttonName == "ButtonLeftBlack" else (0.65, 0.605)
    
    root.run_js_code(
        f"ctx.drawImage(\
           {root.get_img_jsvarname(iconName)},\
           {buttonPos[0] + ButtonWidth * centerPoint[0] - MainUIIconWidth / 2},\
           {buttonPos[1] + ButtonHeight * centerPoint[1] - MainUIIconHeight / 2},\
           {MainUIIconWidth}, {MainUIIconHeight}\
        );",
        add_code_array = True
    )

def drawDialog(
    p: float,
    dialogImageName: str, diagonalPower: float,
    dialogImageSize: tuple[float, float],
    noText: str, yesText: str
):
            
    root.run_js_code(
        f"dialog_canvas_ctx.clear();",
        add_code_array = True
    )
            
    p = 1.0 - (1.0 - p) ** 3
    tempWidth = dialogImageSize[0] * (0.65 + p * 0.35)
    tempHeight = dialogImageSize[1] * (0.65 + p * 0.35)
    diagonalRectanglePowerPx = diagonalPower * tempWidth
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawAlphaImage(\
            {root.get_img_jsvarname(dialogImageName)},\
            {w / 2 - tempWidth / 2}, {h * 0.39 - tempHeight / 2},\
            {tempWidth}, {tempHeight}, {p}\
        );",
        add_code_array = True
    )
    
    diagonalRectangle = (
        w / 2 - tempWidth / 2 - diagonalRectanglePowerPx * 0.2,
        h * 0.39 + tempHeight / 2,
        w / 2 + tempWidth / 2 - diagonalRectanglePowerPx,
        h * 0.39 + tempHeight / 2 + tempHeight * 0.2
    )
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawDiagonalRectangle(\
            {", ".join(map(str, diagonalRectangle))},\
            {diagonalPower * 0.2}, 'rgba(0, 0, 0, {0.85 * p})'\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawDiagonalRectangleText(\
            {", ".join(map(str, diagonalRectangle))},\
            {diagonalPower * 0.2},\
            '{processStringToLiteral(noText)}',\
            '{processStringToLiteral(yesText)}',\
            'rgba(255, 255, 255, {p})',\
            '{(w + h) / 100 * (0.65 + p * 0.35)}px PhigrosFont'\
        );",
        add_code_array = True
    )
    
    return (
        diagonalRectangle[0] + diagonalRectanglePowerPx * 0.2, diagonalRectangle[1],
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[3]
    ), (
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[1],
        diagonalRectangle[2] - diagonalRectanglePowerPx * 0.2, diagonalRectangle[3]
    )

def showStartAnimation():
    global faManager
    
    start_animation_clicked = False
    def start_animation_click_cb(*args): nonlocal start_animation_clicked; start_animation_clicked = True
    
    a1_t = 5.0
    a1_st = time.time()
    mixer.music.load("./Resources/NewSplashSceneBGM.mp3")
    played_NewSplashSceneBGM = False
    while True:
        p = (time.time() - a1_st) / a1_t
        if p > 1.0: break
                
        if p > 0.4 and not played_NewSplashSceneBGM:
            played_NewSplashSceneBGM = True
            mixer.music.play(-1)
            Thread(target=soundEffect_From0To1, daemon=True).start()
        
        if p > 0.4:
            eventManager.regClickEventFs(start_animation_click_cb, True)
            if start_animation_clicked:
                break
            
        root.clear_canvas(wait_execute = True)
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("logoipt")},\
                0, 0, {w}, {h}, {Tool_Functions.easeAlpha(p)}\
            );",
            add_code_array = True
        )
        
        root.run_js_wait_code()
    
    a2_t = 5.0
    a2_st = time.time()
    while True:
        p = (time.time() - a2_st) / a2_t
        if p > 1.0: break
        if start_animation_clicked: break
        
        root.clear_canvas(wait_execute = True)
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("warning")},\
                0, 0, {w}, {h}, {Tool_Functions.easeAlpha(p)}\
            );",
            add_code_array = True
        )
        
        root.run_js_wait_code()
    
    for e in eventManager.clickEvents:
        if e.callback is start_animation_click_cb:
            eventManager.clickEvents.remove(e)
            break
    
    faManager = PhigrosGameObject.FaculaAnimationManager()
    Thread(target=faManager.main, daemon=True).start()
    a3_st = time.time()
    a3_clicked = False
    a3_clicked_time = float("nan")
    a3_sound_fadeout = False
    def a3_click_cb(*args):
        nonlocal a3_clicked_time, a3_clicked
        a3_clicked_time = time.time()
        a3_clicked = True
    eventManager.regClickEventFs(a3_click_cb, True)
    phigros_logo_width = 0.25
    phigros_logo_rect = (
        w / 2 - w * phigros_logo_width / 2,
        h * (100 / 230) - h * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height / 2,
        w * phigros_logo_width, w * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height
    )
    if not abs(mixer.music.get_pos() / 1000 - 8.0) <= 0.05:
        mixer.music.set_pos(8.0)
    while True:
        atime = time.time() - a3_st
        
        if a3_clicked and time.time() - a3_clicked_time > 1.0:
            root.create_rectangle( # no wait
                0, 0, w, h, fillStyle = "#000000"
            )
            break
        
        root.clear_canvas(wait_execute = True)
        
        drawBackground()
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = f"rgba(0, 0, 0, {(math.sin(atime / 1.5) + 1.0) / 5 + 0.15})",
            wait_execute = True
        )
        
        for i in range(50):
            root.create_line(
                0, h * (i / 50), w, h * (i / 50),
                strokeStyle = "rgba(162, 206, 223, 0.03)",
                lineWidth = 0.25, wait_execute = True
            )
    
        drawFaculas()
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("phigros")},\
                {", ".join(map(str, phigros_logo_rect))}\
            );",
            add_code_array = True
        )
        
        textBlurTime = atime % 5.5
        if textBlurTime > 3.0:
            textBlur = math.sin(math.pi * (textBlurTime - 3.0) / 2.5) * 10
        else:
            textBlur = 0.0
        
        root.run_js_code(
            f"ctx.shadowColor = '#FFFFFF'; ctx.shadowBlur = {textBlur};",
            add_code_array = True
        )
        
        root.create_text(
            w / 2,
            h * (155 / 230),
            text = "点  击  屏  幕  开  始",
            font = f"{(w + h) / 125}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            wait_execute = True
        )
        
        root.run_js_code(
            "ctx.shaderColor = 'rgba(0, 0, 0, 0)'; ctx.shadowBlur = 0;",
            add_code_array = True
        )
        
        root.create_text(
            w / 2,
            h * 0.98,
            text = f"Version: {Const.PHIGROS_VERSION}",
            font = f"{(w + h) / 250}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = "#888888",
            wait_execute = True
        )
        
        if atime <= 2.0:
            blurP = 1.0 - (1.0 - atime / 2.0) ** 3
            root.run_js_code(f"mask.style.backdropFilter = 'blur({(w + h) / 60 * (1 - blurP)}px)';", add_code_array = True)
        else:
            root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
        
        if a3_clicked and time.time() - a3_clicked_time <= 1.0:
            if not a3_sound_fadeout:
                a3_sound_fadeout = True
                mixer.music.fadeout(500)
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {1.0 - (1.0 - (time.time() - a3_clicked_time)) ** 2})",
                wait_execute = True
            )
        
        root.run_js_wait_code()
    
    root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
    mixer.music.load("./Resources/ChapterSelect.mp3")
    mainRender()

def soundEffect_From0To1():
    v = 0.0
    for _ in range(100):
        v += 0.01
        if mixer.music.get_pos() / 1000 <= 3.0:
            mixer.music.set_volume(v)
            time.sleep(0.02)
        else:
            mixer.music.set_volume(1.0)
            return None

def processStringToLiteral(string: str):
    return string.replace("\\","\\\\").replace("'","\\'").replace("\"","\\\"").replace("`","\\`").replace("\n", "\\n")

def mainUI_mouseMove(x, y):
    global lastMainUI_ChaptersClickX, lastLastMainUI_ChaptersClickX, chaptersDx
    if inMainUI and mainUI_ChaptersMouseDown:
        chaptersDx += x - lastMainUI_ChaptersClickX
        lastLastMainUI_ChaptersClickX = lastMainUI_ChaptersClickX
        lastMainUI_ChaptersClickX = x

def mainUI_mouseClick(x, y):
    global lastMainUI_ChaptersClickX, lastLastMainUI_ChaptersClickX, mainUI_ChaptersMouseDown
    
    if not inMainUI:
        return None
    
    for e in eventManager.clickEvents:
        if e.tag == "mainUI" and Tool_Functions.InRect(x, y, e.rect):
            return None
    
    lastMainUI_ChaptersClickX = x
    lastLastMainUI_ChaptersClickX = x
    mainUI_ChaptersMouseDown = True

def mainUI_mouseRelease(x, y):
    global mainUI_ChaptersMouseDown
    downed = mainUI_ChaptersMouseDown # 按下过
    mainUI_ChaptersMouseDown = False
    
    if downed and inMainUI:
        Thread(target=chapterUI_easeSroll, daemon=True).start()    

def chapterUI_easeSroll():
    global chaptersDx
    dx = (lastMainUI_ChaptersClickX - lastLastMainUI_ChaptersClickX)
    
    while abs(dx) > w * 0.001:
        dx *= 0.9
        chaptersDx += dx
        if - chaptersDx <= - w / 10 or - chaptersDx >= ChaptersMaxDx - w / 10: # 往右 = 负, 左 = 正, 反的, 所以`-cheaptersDx`
            Thread(target=cheapterUI_easeBack, daemon=True).start()
            return None
        time.sleep(1 / 120)
    Thread(target=cheapterUI_easeBack, daemon=True).start()

def cheapterUI_easeBack():
    global chaptersDx
    
    cdx = - chaptersDx
    
    if 0 <= cdx <= ChaptersMaxDx:
        return None

    if cdx < 0:
        dx = - cdx
    else:
        dx = ChaptersMaxDx - cdx
    dx *= -1 # 前面cdx = 负的, 所以变回来
    if chaptersDx + dx > 0: # 超出左界
        dx = - chaptersDx
    
    lastv = 0.0
    av = 0.0
    ast = time.time()
    while True:
        p = (time.time() - ast) / 0.75
        if p > 1.0:
            chaptersDx += dx - av
            break
        
        v = 1.0 - (1.0 - p) ** 4
        dxv = (v - lastv) * dx
        av += dxv
        chaptersDx += dxv
        lastv = v
        
        time.sleep(1 / 120)
        
def changeChapterMouseDown(x, y):
    global changeChapterMouseDownX
    
    if y < h * (140 / 1080) or y > h * (1.0 - 140 / 1080):
        return None
    elif not inMainUI:
        return None
    
    changeChapterMouseDownX = x

def changeChapterMouseUp(x, y):
    global lastChangeChapterTime
    
    if y < h * (140 / 1080) or y > h * (1.0 - 140 / 1080):
        return None
    elif abs(x - changeChapterMouseDownX) > w * 0.005:
        return None
    elif not inMainUI:
        return None
    elif time.time() - lastChangeChapterTime < 0.85: # 1.0s 动画时间, 由于是ease out, 所以可以提前一点
        return None
    
    chapterX = w * 0.034375 + chaptersDx
    for index, i in enumerate(Chapters.items):
        p = getChapterP(i)
        width = getChapterWidth(p)
        dPower = Tool_Functions.getDPower(width, h * (1.0 - 140 / 1080 * 2), 75)
        if Tool_Functions.inDiagonalRectangle(*getChapterRect(chapterX, width), dPower, x, y):
            if Chapters.aTo != index:
                Chapters.aFrom, Chapters.aTo, Chapters.aSTime = Chapters.aTo, index, time.time()
                lastChangeChapterTime = time.time()
                Resource["UISound_3"].play()
            break
        chapterX += getChapterToNextWidth(p)

def mainRender():
    global inMainUI
    inMainUI = True
    
    faManager.faculas.clear()
    mainRenderSt = time.time()
    mixer.music.play(-1)
    
    messageRect = (w * 0.015, h * 0.985 - MessageButtonSize, MessageButtonSize, MessageButtonSize)
    JoinQQGuildBannerRect = (0.0, h - JoinQQGuildBannerHeight, JoinQQGuildBannerWidth, JoinQQGuildBannerHeight)
    events = []
    
    clickedMessage = False
    clickMessageTime = float("nan")
    canClickMessage = True
    messageBackTime = 7.0
    messageBacking = False
    messageBackSt = float("nan")
    def clickMessage(*args):
        nonlocal clickedMessage, clickMessageTime, canClickJoinQQGuildBanner
        if canClickMessage:
            clickMessageTime = time.time()
            clickedMessage = True
            canClickJoinQQGuildBanner = True
            Resource["UISound_1"].play()
    events.append(PhigrosGameObject.ClickEvent(
        rect = (messageRect[0], messageRect[1], messageRect[0] + messageRect[2], messageRect[1] + messageRect[3]),
        callback = clickMessage,
        once = False,
        tag = "mainUI"
    ))
    eventManager.regClickEvent(events[-1])
    
    clickedJoinQQGuildBanner = False
    clickedJoinQQGuildBannerTime = float("nan")
    canClickJoinQQGuildBanner = False
    def clickJoinQQGuildBanner(*args):
        global inMainUI
        nonlocal clickedJoinQQGuildBanner, clickedJoinQQGuildBannerTime, messageBackTime
        
        if canClickJoinQQGuildBanner and (time.time() - clickMessageTime) > 0.1:
            clickedJoinQQGuildBannerTime = time.time()
            clickedJoinQQGuildBanner = True
            messageBackTime = float("inf")
            inMainUI = False
            Resource["UISound_2"].play()
    events.append(PhigrosGameObject.ClickEvent(
        rect = (JoinQQGuildBannerRect[0], JoinQQGuildBannerRect[1], JoinQQGuildBannerRect[0] + JoinQQGuildBannerRect[2], JoinQQGuildBannerRect[1] + JoinQQGuildBannerRect[3]),
        callback = clickJoinQQGuildBanner,
        once = False
    ))
    eventManager.regClickEvent(events[-1])
    
    JoinQQGuildPromoNoEvent = None
    JoinQQGuildPromoYesEvent = None
    JoinQQGuildBacking = False
    JoinQQGuildBackingSt = float("nan")
    
    def JoinQQGuildPromoNoCallback(*args):
        global inMainUI
        nonlocal JoinQQGuildBacking, JoinQQGuildBackingSt, clickedJoinQQGuildBanner
        nonlocal JoinQQGuildPromoNoEvent, JoinQQGuildPromoYesEvent
        
        JoinQQGuildBacking = True
        JoinQQGuildBackingSt = time.time()
        clickedJoinQQGuildBanner = False
        
        eventManager.unregEvent(JoinQQGuildPromoNoEvent)
        eventManager.unregEvent(JoinQQGuildPromoYesEvent)
        events.remove(JoinQQGuildPromoNoEvent)
        events.remove(JoinQQGuildPromoYesEvent)
        
        JoinQQGuildPromoNoEvent = None
        JoinQQGuildPromoYesEvent = None
        inMainUI = True
    
    def JoinQQGuildPromoYesCallback(*args):
        webbrowser.open_new("https://qun.qq.com/qqweb/qunpro/share?inviteCode=21JzOLUd6J0")
        JoinQQGuildPromoNoCallback(*args)
    
    SettingClicked = False
    SettingClickedTime = float("nan")
    
    def SettingCallback(*args):
        nonlocal SettingClicked, SettingClickedTime
        if not SettingClicked:
            for e in events:
                eventManager.unregEvent(e)
            
            SettingClicked = True
            SettingClickedTime = time.time()
            mixer.music.fadeout(500)
            Resource["UISound_2"].play()
    
    events.append(PhigrosGameObject.ClickEvent(
        rect = (w - ButtonWidth, h - ButtonHeight, w, h),
        callback = SettingCallback,
        once = False,
        tag = "mainUI"
    ))
    eventManager.regClickEvent(events[-1])
    
    while True:
        root.clear_canvas(wait_execute = True)
        
        drawBackground()
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = "rgba(0, 0, 0, 0.7)",
            wait_execute = True
        )
        
        drawFaculas()
        
        drawButton("ButtonLeftBlack", "collectibles", (0, 0))
        drawButton("ButtonRightBlack", "setting", (w - ButtonWidth, h - ButtonHeight))
        drawChapters()
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("message")},\
                {", ".join(map(str, messageRect))}, 0.7\
            );",
            add_code_array = True
        )
        
        if clickedMessage and time.time() - clickMessageTime >= messageBackTime:
            clickedMessage = False
            messageBacking = True
            messageBackSt = time.time()
            canClickJoinQQGuildBanner = False
            
            if messageBackTime == 0.0:
                messageBackTime = 2.0 # back JoinQQGuild
            elif messageBackTime == 2.0:
                messageBackTime = 7.0
        
        if clickedMessage and time.time() - clickMessageTime <= 1.5:
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0] - JoinQQGuildBannerWidth + (1.0 - (1.0 - ((time.time() - clickMessageTime) / 1.5)) ** 6) * JoinQQGuildBannerWidth}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        elif not clickedMessage and messageBacking:
            if time.time() - messageBackSt > 1.5:
                messageBacking = False
                messageBackSt = time.time() - 1.5 # 防止回弹
                canClickMessage = True
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0] - (1.0 - (1.0 - ((time.time() - messageBackSt) / 1.5)) ** 6) * JoinQQGuildBannerWidth}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        elif clickedMessage:
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0]}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        
        if clickedMessage and canClickMessage:
            canClickMessage = False
        
        if clickedJoinQQGuildBanner:
            canClickJoinQQGuildBanner = False
            p = (time.time() - clickedJoinQQGuildBannerTime) / 0.35
            p = p if p <= 1.0 else 1.0
            ep = 1.0 - (1.0 - p) ** 2
            
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {ep * 0.5})",
                wait_execute = True                
            )
            
            root.run_js_code(
                f"mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';",
                add_code_array = True
            )
            
            noRect, yesRect = drawDialog(
                p, "JoinQQGuildPromo",
                Const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
            
            if JoinQQGuildPromoNoEvent is None and JoinQQGuildPromoYesEvent is None:
                JoinQQGuildPromoNoEvent = PhigrosGameObject.ClickEvent( # once is false, remove event in callback
                    noRect, JoinQQGuildPromoNoCallback, False
                )
                JoinQQGuildPromoYesEvent = PhigrosGameObject.ClickEvent(
                    yesRect, JoinQQGuildPromoYesCallback, False
                )
                events.append(JoinQQGuildPromoNoEvent)
                events.append(JoinQQGuildPromoYesEvent)
                eventManager.regClickEvent(JoinQQGuildPromoNoEvent)
                eventManager.regClickEvent(JoinQQGuildPromoYesEvent)
            else:
                JoinQQGuildPromoNoEvent.rect = noRect
                JoinQQGuildPromoYesEvent.rect = yesRect
        elif JoinQQGuildBacking and time.time() - JoinQQGuildBackingSt < 0.35:
            p = 1.0 - (time.time() - JoinQQGuildBackingSt) / 0.35
            ep = 1.0 - (1.0 - p) ** 2
            
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {ep * 0.5})",
                wait_execute = True                
            )
            
            root.run_js_code(
                f"mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';",
                add_code_array = True
            )
            
            drawDialog(
                p, "JoinQQGuildPromo",
                Const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
        elif JoinQQGuildBacking:
            root.run_js_code(
                "mask.style.backdropFilter = 'blur(0px)';",
                add_code_array = True
            )
            
            root.run_js_code(
                "dialog_canvas_ctx.clear();",
                add_code_array = True
            )
            
            JoinQQGuildBacking = False
            JoinQQGuildBackingSt = float("nan")
            messageBackTime = 0.0
        
        if time.time() - mainRenderSt < 2.0:
            p = (time.time() - mainRenderSt) / 2.0
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {(1.0 - p) ** 2})",
                wait_execute = True
            )
        
        if SettingClicked and time.time() - SettingClickedTime < 0.75:
            p = (time.time() - SettingClickedTime) / 0.75
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})",
                wait_execute = True
            )
        elif SettingClicked:
            inMainUI = False
            root.clear_canvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=settingRender, daemon=True).start()
            break
        
        root.run_js_wait_code()

def settingRender():
    settingRenderSt = time.time()
    settingState = PhigrosGameObject.SettingState()
    
    clickedBackButton = False
    clickedBackButtonTime = float("nan")
    
    def clickBackButtonCallback(*args):
        nonlocal clickedBackButton, clickedBackButtonTime
        if not clickedBackButton:
            eventManager.unregEvent(clickBackButtonEvent)
            eventManager.unregEvent(settingMainClickEvent)
            
            clickedBackButton = True
            clickedBackButtonTime = time.time()
            Resource["UISound_2"].play()
    
    clickBackButtonEvent = PhigrosGameObject.ClickEvent(
        rect = (0, 0, ButtonWidth, ButtonHeight),
        callback = clickBackButtonCallback,
        once = False
    )
    eventManager.regClickEvent(clickBackButtonEvent)
    
    lastChangeSettingStateTime = float("-inf")
    
    def _setSettingState(t: int):
        nonlocal lastChangeSettingStateTime
        
        if time.time() - lastChangeSettingStateTime < 0.6:
            return None
        elif t == settingState.aTo:
            return None
        lastChangeSettingStateTime = time.time()
        settingState.changeState(t)
    
    def settingMainClickCallback(x, y):
        if Tool_Functions.InRect(x, y, (
            346 / 1920 * w, 35 / 1080 * h,
            458 / 1920 * w, 97 / 1080 * h
        )):
            _setSettingState(Const.PHIGROS_SETTING_STATE.PLAY)
        elif Tool_Functions.InRect(x, y, (
            540 / 1920 * w, 35 / 1080 * h,
            723 / 1920 * w, 97 / 1080 * h
        )):
            _setSettingState(Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        elif Tool_Functions.InRect(x, y, (
            807 / 1920 * w, 35 / 1080 * h,
            915 / 1920 * w, 97 / 1080 * h
        )):
            _setSettingState(Const.PHIGROS_SETTING_STATE.OTHER)
    
    settingMainClickEvent = PhigrosGameObject.ClickEvent(
        rect = (0, 0, w, h),
        callback = settingMainClickCallback,
        once = False
    )
    eventManager.regClickEvent(settingMainClickEvent)
    
    settingDx = [0.0, 0.0, 0.0]
    
    def getShadowDiagonalXByY(y: float):
        return w * Tool_Functions.getDPower(w, h, 75) * ((h - y) / h)
    
    def drawOtherSettingButton(x0: float, y0: float, x1: float, y1: float, dpower: float):
        root.run_js_code(
            f"ctx.drawDiagonalRectangleNoFix(\
                {x0}, {y0},\
                {x1}, {y1},\
                {dpower}, '#FFFFFF'\
            );",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("Arrow_Right_Black")},\
                {x0 + (x1 - x0) / 2 - SettingUIOtherIconWidth / 2},\
                {y0 + (y1 - y0) / 2 - SettingUIOtherIconHeight / 2},\
                {SettingUIOtherIconWidth}, {SettingUIOtherIconHeight}\
            );",
            add_code_array = True
        )
    
    otherSettingButtonRects = [
        (
            w * 0.3921875, h * (611 / 1080),
            w * (0.3921875 + 0.046875), h * ((611 + 50) / 1080)
        ),
        (
            w * 0.3765625, h * (711 / 1080),
            w * (0.3765625 + 0.046875), h * ((711 + 50) / 1080)
        ),
        (
            w * 0.7890625, h * (611 / 1080),
            w * (0.7890625 + 0.046875), h * ((611 + 50) / 1080)
        ),
        (
            w * 0.7734375, h * (711 / 1080),
            w * (0.7734375 + 0.046875), h * ((711 + 50) / 1080)
        )
    ]
    
    def drawPlaySetting(dx: float, alpha: float):
        if alpha == 0.0: return None
    
    def drawAccountAndCountSetting(dx: float, alpha: float):
        if alpha == 0.0: return None
        
        root.run_js_code(
            f"ctx.save(); ctx.translate({- dx}, 0); ctx.globalAlpha = {alpha};",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.restore();",
            add_code_array = True
        )

    def drawOtherSetting(dx: float, alpha: float):
        if alpha == 0.0: return None
        
        root.run_js_code(
            f"ctx.save(); ctx.translate({- dx}, 0); ctx.globalAlpha = {alpha};",
            add_code_array = True
        )

        phiIconWidth = w * 0.215625
        phiIconHeight = phiIconWidth / Resource["phigros"].width * Resource["phigros"].height
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("phigros")},\
                {w * 0.3890625 - phiIconWidth / 2}, {h * ((0.275 + 371 / 1080) / 2) - phiIconHeight / 2},\
                {phiIconWidth}, {phiIconHeight}\
            );",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.drawLineEx(\
                {w * 0.5296875}, {h * 0.275},\
                {w * 0.5296875}, {h * (371 / 1080)},\
                {(w + h) / 2000}, 'rgb(138, 138, 138, 0.95)'\
            );",
            add_code_array = True
        )
        
        root.create_text(
            w * 0.5703125, h * (308 / 1080),
            f"Version: {Const.PHIGROS_VERSION}",
            font = f"{(w + h) /125}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgb(138, 138, 138, 0.95)",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.5703125, h * (361 / 1080),
            f"Device: {Const.DEVICE}",
            font = f"{(w + h) /125}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgb(138, 138, 138, 0.95)",
            wait_execute = True
        )
        
        settingOtherButtonDPower = Tool_Functions.getDPower(90, 50, 75)
        
        root.create_text(
            w * (0.0515625 + 0.0265625) + getShadowDiagonalXByY(h * 0.575),
            h * 0.575,
            "音频问题疑难解答",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawOtherSettingButton(
            *otherSettingButtonRects[0],
            settingOtherButtonDPower
        )
        
        root.create_text(
            w * (0.0515625 + 0.0265625) + getShadowDiagonalXByY(h * 0.675),
            h * 0.675,
            "观看教学",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawOtherSettingButton(
            *otherSettingButtonRects[1],
            settingOtherButtonDPower
        )
        
        root.create_text(
            w * (0.0515625 + 0.0265625 + 0.4015625) + getShadowDiagonalXByY(h * 0.575),
            h * 0.575,
            "开源许可证",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawOtherSettingButton(
            *otherSettingButtonRects[2],
            settingOtherButtonDPower
        )
        
        root.create_text(
            w * (0.0515625 + 0.0265625 + 0.4015625) + getShadowDiagonalXByY(h * 0.675),
            h * 0.675,
            "隐私政策",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawOtherSettingButton(
            *otherSettingButtonRects[3],
            settingOtherButtonDPower
        )
        
        root.create_text(
            w * 0.5453125,
            h * (1031 / 1080),
            Const.OTHERSERTTING_RIGHTDOWN_TEXT,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("twitter")},\
                {w * 0.0734375 - SettingUIOtherIconWidth / 2}, {h * (1031 / 1080) - SettingUIOtherDownIconHeight_Twitter / 2},\
                {SettingUIOtherDownIconWidth}, {SettingUIOtherDownIconHeight_Twitter}\
            );",
            add_code_array = True
        )
        
        root.create_text(
            w * 0.0875, h * (1031 / 1080),
            Const.OTHER_SETTING_LB_STRINGS.TWITTER,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("bilibili")},\
                {w * 0.203125 - SettingUIOtherIconWidth / 2}, {h * (1031 / 1080) - SettingUIOtherDownIconHeight_Bilibili / 2},\
                {SettingUIOtherDownIconWidth}, {SettingUIOtherDownIconHeight_Bilibili}\
            );",
            add_code_array = True
        )
        
        root.create_text(
            w * 0.2171875, h * (1031 / 1080),
            Const.OTHER_SETTING_LB_STRINGS.BILIBILI,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("qq")},\
                {w * 0.3328125 - SettingUIOtherIconWidth / 2 * 0.85}, {h * (1031 / 1080) - SettingUIOtherDownIconHeight_QQ / 2 * 0.85},\
                {SettingUIOtherDownIconWidth * 0.85}, {SettingUIOtherDownIconHeight_QQ * 0.85}\
            );",
            add_code_array = True
        )
        
        root.create_text(
            w * 0.346875, h * (1031 / 1080),
            Const.OTHER_SETTING_LB_STRINGS.QQ,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.restore();",
            add_code_array = True
        )
    
    PlaySettingWidgets = {
        "OffsetLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "谱面延时",
            right_text = "0ms",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "OffsetSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 0.0,
            number_points = (
                (0.0, -400.0),
                (0.4, 0.0),
                (1.0, 600.0)
            ),
            lr_button = True
        ),
        "OffsetTip": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "",
            right_text = "*请调节至第三拍的声音与按键音恰好重合的状态",
            font = "10px PhigrosFont",
            color = "rgba(255, 255, 255, 0.6)"
        ),
        "NoteScaleLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "按键缩放",
            right_text = "",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "NoteScaleSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 1.0,
            number_points = ((0.0, 1.0), (1.0, 1.29)),
            lr_button = False
        ),
        "BackgroundDimLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "背景亮度",
            right_text = "",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "BackgroundDimSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 0.6,
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False
        ),
        "ClickSoundCheckbox": PhigrosGameObject.PhiCheckbox(
            padding_top = 0.0,
            padding_bottom = 0.0,
            text = "打开打击音效",
            font = "10px PhigrosFont",
            checked = True
        ),
        "MusicVolumeLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "音乐音量",
            right_text = "",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "MusicVolumeSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 1.0,
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False
        ),
        "UISoundVolumeLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "界面音效音量",
            right_text = "",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "UISoundVolumeSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 1.0,
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False
        ),
        "ClickSoundVolumeLabel": PhigrosGameObject.PhiLabel(
            padding_top = 0.0,
            padding_bottom = 0.0,
            left_text = "打击音效音量",
            right_text = "",
            font = "10px PhigrosFont",
            color = "#FFFFFF"
        ),
        "ClickSoundVolumeSlider": PhigrosGameObject.PhiSlider(
            padding_top = 0.0,
            padding_bottom = 0.0,
            value = 1.0,
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False
        ),
        "MorebetsAuxiliaryCheckbox": PhigrosGameObject.PhiCheckbox(
            padding_top = 0.0,
            padding_bottom = 0.0,
            text = "开启多押辅助",
            font = "10px PhigrosFont",
            checked = True
        ),
        "FCAPIndicatorCheckbox": PhigrosGameObject.PhiCheckbox(
            padding_top = 0.0,
            padding_bottom = 0.0,
            text = "开启FC/AP指示器",
            font = "10px PhigrosFont",
            checked = True
        ),
        "LowQualityCheckbox": PhigrosGameObject.PhiCheckbox(
            padding_top = 0.0,
            padding_bottom = 0.0,
            text = "低分辨率模式",
            font = "10px PhigrosFont",
            checked = False
        )
    }
    
    print(PlaySettingWidgets)
    
    while True:
        root.clear_canvas(wait_execute = True)
        
        drawBackground()
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = "rgba(0, 0, 0, 0.5)",
            wait_execute = True
        )
        
        drawButton("ButtonLeftBlack", "Arrow_Left", (0, 0))
        
        ShadowXRect = settingState.getShadowRect()
        ShadowRect = (
            ShadowXRect[0] * w, 0.0,
            ShadowXRect[1] * w, h
        )
        ShadowDPower = Tool_Functions.getDPower(ShadowRect[2] - ShadowRect[0], h, 75)
        
        root.run_js_code(
            f"ctx.drawDiagonalRectangleNoFix(\
                {", ".join(map(str, ShadowRect))},\
                {ShadowDPower}, 'rgba(0, 0, 0, 0.2)'\
            );",
            add_code_array = True
        )
        
        BarWidth = settingState.getBarWidth() * w
        BarHeight = h * (2 / 27)
        BarDPower = Tool_Functions.getDPower(BarWidth, BarHeight, 75)
        BarRect = (
            w * 0.153125, h * 0.025,
            w * 0.153125 + BarWidth, h * 0.025 + BarHeight
        )
        
        root.run_js_code(
            f"ctx.drawDiagonalRectangleNoFix(\
                {", ".join(map(str, BarRect))},\
                {BarDPower}, 'rgba(0, 0, 0, 0.45)'\
            );",
            add_code_array = True
        )
        
        LabelWidth = settingState.getLabelWidth() * w
        LabelHeight = h * (113 / 1080)
        LabelDPower = Tool_Functions.getDPower(LabelWidth, LabelHeight, 75)
        LabelX = settingState.getLabelX() * w
        LabelRect = (
            LabelX, h * 1 / 108,
            LabelX + LabelWidth, h * 1 / 108 + LabelHeight
        )
        
        root.run_js_code(
            f"ctx.drawDiagonalRectangleNoFix(\
                {", ".join(map(str, LabelRect))},\
                {LabelDPower}, 'rgba(255, 255, 255, 1.0)'\
            );",
            add_code_array = True
        )
        
        PlayTextColor = settingState.getTextColor(Const.PHIGROS_SETTING_STATE.PLAY)
        AccountAndCountTextColor = settingState.getTextColor(Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        OtherTextColor = settingState.getTextColor(Const.PHIGROS_SETTING_STATE.OTHER)
        PlayTextFontScale = settingState.getTextScale(Const.PHIGROS_SETTING_STATE.PLAY)
        AccountAndCountTextFontScale = settingState.getTextScale(Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        OtherTextFontScale = settingState.getTextScale(Const.PHIGROS_SETTING_STATE.OTHER)
        settingTextY = h * 0.025 + BarHeight / 2
        
        root.create_text(
            w * 0.209375, settingTextY,
            "游玩",
            font = f"{(w + h) / 100 * PlayTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgb{PlayTextColor}",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.3296875, settingTextY,
            "账号与统计",
            font = f"{(w + h) / 100 * AccountAndCountTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgb{AccountAndCountTextColor}",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.4484375, settingTextY,
            "其他",
            font = f"{(w + h) / 100 * OtherTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgb{OtherTextColor}",
            wait_execute = True
        )
        
        settingState.render(drawPlaySetting, drawAccountAndCountSetting, drawOtherSetting, ShadowXRect[0], w, settingDx)
                
        if time.time() - settingRenderSt < 1.25:
            p = (time.time() - settingRenderSt) / 1.25
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {(1.0 - p) ** 2})",
                wait_execute = True
            )
        
        if clickedBackButton and time.time() - clickedBackButtonTime < 0.75:
            p = (time.time() - clickedBackButtonTime) / 0.75
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})",
                wait_execute = True
            )
        elif clickedBackButton:
            root.clear_canvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=mainRender, daemon=True).start()
            break
        
        root.run_js_wait_code()

root = webcvapis.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "Phigros",
    debug = "--debug" in sys.argv,
    resizable = False
)
webdpr = root.run_js_code("window.devicePixelRatio;")
root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")

# w, h = root.winfo_screenwidth(), root.winfo_screenheight()
# root.resize(w, h)
# root._web.toggle_fullscreen()

w, h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564), int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
root.resize(w, h)
w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
dw_legacy *= webdpr; dh_legacy *= webdpr
dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
del w_legacy, h_legacy
root.resize(w + dw_legacy, h + dh_legacy)
root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))

# Constant
PlayButtonWidth = w * 0.1453125
PlayButtonHeight = h * (5 / 54)
PlayButtonDPower = Tool_Functions.getDPower(PlayButtonWidth, PlayButtonHeight, 75)

if "--window-host" in sys.argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))

Load_Chapters()
Resource = Load_Resource()
eventManager = PhigrosGameObject.EventManager()
bindEvents()
Thread(target=showStartAnimation, daemon=True).start()
    
root.loop_to_close()
windll.kernel32.ExitProcess(0)