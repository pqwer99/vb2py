# -*- coding: utf8 -*-

import os.path
import sys
import io

from fltk import *

from fltk_ext import fltktext, getfltktext, FltkFont

from ctypes_vbapi import getvbdeclare, makectypes
from ctypes_struct import buildstruct

from dialogbox import FileDialog

from fltk_vbform import T

PY2 = sys.version_info[0] == 2
if PY2:
    open = io.open

PY3 = sys.version_info[0] == 3

fltkfont = FltkFont(name='微软雅黑', size=18, style=0)
##fltkfont = FltkFont(name='宋体', size=16, style=0)

##def __getdpi():
##    from ctypes import windll
##    GetDC = windll.user32.GetDC
##    GetDeviceCaps = windll.gdi32.GetDeviceCaps
##    LOGPIXELSX = 88        #  Logical pixels/inch in X
##    return GetDeviceCaps(GetDC(None), LOGPIXELSX) / 96.0     # 96为设备绘制为100%大小时dpi
##DPI = __getdpi()
##
##def T(twips, dpi=DPI):
##    return int(twips / 15 * dpi)

class FormCtypes(object):
    def __init__(self):
        self.formctypes = Fl_Double_Window(T(12555), T(7815), "api -> ctypes")
        #
        self._MenuBarH = 300  # MenuBar height
        self._ComboBoxH = 330   # ComboBox extent height

        # bulid tabs widget
        self.createtabs_sstab1()

    def createtabs_sstab1(self):
        self.sstab1 = Fl_Tabs(T(30), T(30), T(12480), T(7740))
        TabsLabelH = 330   # Tabs Label height

        self.sstab1_page0 = Fl_Group(T(30), T(30+TabsLabelH), T(12480), T(7740-TabsLabelH), " VB源码 或 C结构体 ")
        if self.sstab1_page0:
            self.command1 = Fl_Button(T(480), T(570), T(1600), T(330), "打开VB文件")
            self.command2 = Fl_Button(T(2700), T(570), T(1600), T(330), "转换VB源玛")
            self.text1 = Fl_Text_Editor(T(90), T(1065), T(12375), T(6660), None)
            self.text1_buffer = Fl_Text_Buffer()
            self.text1.buffer(self.text1_buffer)
            self.command3 = Fl_Button(T(4860), T(570), T(1600), T(330), "转换C结构体")

            self.popmenu1 = Fl_Menu_Button(self.text1.x(), self.text1.y(), self.text1.w(), self.text1.h(), '源码')
            self.popmenu1.type(Fl_Menu_Button.POPUP3)
        self.sstab1_page0.end()

        self.sstab1_page1 = Fl_Group(T(30), T(30+TabsLabelH), T(12480), T(7740-TabsLabelH), " Python代码 ")
        if self.sstab1_page1:
            self.text2 = Fl_Text_Editor(T(90), T(390), T(12375), T(7335), None)
            self.text2_buffer = Fl_Text_Buffer()
            self.text2.buffer(self.text2_buffer)

            self.popmenu2 = Fl_Menu_Button(self.text2.x(), self.text2.y(), self.text2.w(), self.text2.h(), 'Python代码')
            self.popmenu2.type(Fl_Menu_Button.POPUP3)
        self.sstab1_page1.end()

        self.sstab1.end()

class FormCtypesProc(FormCtypes):
    def __init__(self):
        FormCtypes.__init__(self)
        self.formctypes.color(FL_LIGHT2)   # 当前窗体颜色
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(0xf0, 0xf0, 0xf0))     # 更改部件默认背景色
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(*Fl.get_color(FL_LIGHT2)))
        self.resize()
        #
        # 修改、设置控件属性
        #
##        self.mnu_edit =  (
##            ("Undo",        0, self.undo_cb, self.text_log_buff, FL_MENU_DIVIDER ),
##            ("Cu&t",        FL_CTRL + ord('x'), self.cut_cb, self.text1 ),
##            ("&Copy",       FL_CTRL + ord('c'), self.copy_cb, self.text1),
##            ("&Paste",      FL_CTRL + ord('v'), self.paste_cb, self.text1 ),
##            ("&Delete",     0,                  self.delete_cb, self.text1 ),
##            (None,) )
        self.mnu_edit =  (
            ("撤消", FL_CTRL + ord('z'), 0, 0, FL_MENU_DIVIDER ),
            ("剪切", FL_CTRL + ord('x') ),
            ("复制", FL_CTRL + ord('c')),
            ("粘贴", FL_CTRL + ord('v'), 0, 0, FL_MENU_DIVIDER),
            ("删除", 0, 0),
            (None,) )
        self.popmenu1.copy(self.mnu_edit)
        self.popmenu2.copy(self.mnu_edit)
        self.popmenu1.callback(self.menu_callback, self.text1)
        self.popmenu2.callback(self.menu_callback, self.text2)
        #
        self.command1.callback(self.cb_selfile)
        self.command2.callback(self.cb_vbapi)
        self.command3.callback(self.cb_struct)

        fltkfont.set(self.text1, self.text2, self.popmenu1, self.popmenu2)
##        self.sstab1.selection_color(7)

    def resize(self):
        # 调整窗口、控件位置及大小
        _w, _h = int(self.formctypes.w()*0.618), int(self.formctypes.h()*0.618)
        self.formctypes.size_range(_w, _h)
        self.formctypes.resizable(self.sstab1)
        self.sstab1.resizable(self.sstab1_page0)
        self.sstab1_page0.resizable(self.text1)
        self.sstab1_page1.resizable(self.text2)
        self.sstab1.resize(0, self.sstab1.y(),
                           self.formctypes.w(), self.formctypes.h() - self.sstab1.y())
##        self.text1.resize(self.sstab1_page0.x(), self.text1.y()+1,
##                          self.sstab1_page0.w(), self.text1.h()+1)
##        self.text2.resize(self.sstab1_page1.x(), self.sstab1_page1.y()+1,
##                          self.sstab1_page1.w(), self.sstab1_page1.h()-1)

    def menu_callback(self, this, editor):
##        print(this, editor)
##        print this.mvalue()     # Fl_menu_Item
##        print this.mvalue().label()
##        print(this.text())
        menu_index = this.value()
##        print menu_index
        if menu_index==0:     # undo
            editor.buffer().undo()
        elif menu_index==1:   # cut
            editor.kf_cut(0, editor)
        elif menu_index==2:  # copy
##            Fl_Text_Editor_kf_copy(0, editor)
            editor.kf_copy(0, editor)
        elif menu_index==3:  # paste
##            Fl_paste(editor)   # Fl_Text_Buffer用
            editor.kf_paste(0, editor)
        elif menu_index==4:  # delete
            editor.kf_delete(0, editor)
##            editor.remove_selection()   # Fl_Text_Buffer用

    def cb_selfile(self, this):
        dlg = FileDialog()
        filterstr = u'VB 文件 (*.frm;*.bas;*.cls;*.ctl)|*.frm;*.bas;*.cls;*.ctl|All Files (*.*)|*.*'
        vbfile = dlg.showopen(u"选择文件", Filter=filterstr)
        if vbfile:
            vbfilename = vbfile[0]
        else:
            return
        #end if

        if not os.path.isfile(vbfilename): return
        vbfile = getvbdeclare(vbfilename)
        self.text1_buffer.text('')
        self.text1_buffer.append(fltktext(vbfile.getvalue()))

    def cb_vbapi(self, this):
        vbsrc = getfltktext(self.text1_buffer.text())
        pyfile = makectypes(vbsrc)
        self.text2.scroll(self.text2_buffer.length(), 1)

        self.text2_buffer.append(fltktext(pyfile.getvalue()))

        self.text2.activate()

    def cb_struct(self, this):
        txt = getfltktext(self.text1_buffer.text())
        stfile = buildstruct(txt)
        self.text2.scroll(self.text2_buffer.length(), 1)

        self.text2_buffer.append(fltktext(stfile.getvalue()))

        self.text2.activate()

    def start(self, mt=False):
        self.formctypes.callback(self.on_close)
        self.formctypes.end()
        self.formctypes.show()
        if mt:
            #Fl.mt_run(self.formctypes)
            import time
            while Fl.check(): time.sleep(0.1)  #Fl.wait(0.05)
        else:
            Fl.run()
        #end if

    def on_close(self, this):
        # Fl.event()=FL_CLOSE，窗口关闭时执行以下代码

        # this.hide()
##        print(this.label())
        Fl.fltk_exit()

if __name__ == '__main__':
    app = FormCtypesProc()
    app.start()
