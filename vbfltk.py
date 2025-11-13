# -*- coding: utf8 -*-

from __future__ import print_function

import io
import sys
import os.path
from pprint import pprint
import json

from fltk import *

from fltk_ext import fltktext, getfltktext, FltkFont, Print2Fltk
from dialogbox import FileDialog

from fltk_vbform import PyFltkWin, T

PY2 = sys.version_info[0] == 2
if PY2:
    open = io.open

class FormFltk(object):
    def __init__(self):
        self.formfltk = Fl_Double_Window(T(12555), T(7815), "VB.Form -> pyfltk")
        #
        self._MenuBarH = 300  # MenuBar height
        self._ComboBoxH = 330   # ComboBox extent height

        self.text1 = Fl_Output(T(2400), T(210), T(9735), T(360), None)
        self.text1.value("Text1")
        self.command1 = Fl_Button(T(315), T(210), T(1800), T(360), "选择文件")
        # bulid tabs widget
        self.createtabs_sstab1()

    def createtabs_sstab1(self):
        self.sstab1 = Fl_Tabs(T(45), T(795), T(12465), T(6975))
        TabHeight = 330   # Tabs Label height

        self.sstab1_page0 = Fl_Group(T(45), T(795+TabHeight), T(12465), T(6975-TabHeight), " 📄 Frm文件 ")
        if self.sstab1_page0:
            self.text2 = Fl_Text_Display(T(93), T(1170), T(12375), T(5835), None)
            self.text2_buffer = Fl_Text_Buffer()
            self.text2.buffer(self.text2_buffer)
            self.text2.show_cursor()
            self.command2 = Fl_Button(T(3705), T(7200), T(1800), T(360), "生成代码")
            self.option1 = Fl_Radio_Round_Button(T(5970), T(7230), T(1140), T(360), "全部源码")
            self.option1.value(-1)
            self.option2 = Fl_Radio_Round_Button(T(7335), T(7230), T(1140), T(360), "仅界面类")
            self.option2.value(0)
        self.sstab1_page0.end()

        self.sstab1_page1 = Fl_Group(T(45), T(795+TabHeight), T(12465), T(6975-TabHeight), " 📊 过程数据 ")
        if self.sstab1_page1:
            self.text3 = Fl_Text_Display(T(93), T(1170), T(12375), T(6555), None)
            self.text3_buffer = Fl_Text_Buffer()
            self.text3.buffer(self.text3_buffer)
            self.text3.show_cursor()
        self.sstab1_page1.end()

        self.sstab1_page2 = Fl_Group(T(45), T(795+TabHeight), T(12465), T(6975-TabHeight), " 📝 程序代码 ")
        if self.sstab1_page2:
            self.text4 = Fl_Text_Display(T(93), T(1170), T(12375), T(5820), None)
            self.text4_buffer = Fl_Text_Buffer()
            self.text4.buffer(self.text4_buffer)
            self.text4.show_cursor()
            self.command3 = Fl_Button(T(3900), T(7185), T(1800), T(360), "复制到剪贴板")
            self.command4 = Fl_Button(T(6525), T(7185), T(1800), T(360), "保存到文件")
        self.sstab1_page2.end()

        self.sstab1.end()


class FormFltkProc(FormFltk):
    def __init__(self):
        FormFltk.__init__(self)
        # 设置窗体背景色
        self.formfltk.color(FL_LIGHT2)
        # 更改部件默认背景色
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(0xf0, 0xf0, 0xf0))
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(*Fl.get_color(FL_LIGHT2)))
        #
        # 修改、设置控件属性
        #
        self.text1.value('')# r'E:\My PY\Projects\VB6\Form_vb2py.frm')
        self.text4.show_cursor(self.text4.HEAVY_CURSOR)

        self.command1.callback(self.cb_selfile)
        self.command2.callback(self.cb_gencode)
        self.command3.callback(self.cb_copyto, self.text4)
        self.command4.callback(self.cb_saveto, self.text4)

##        self.sstab1.selection_color(7)

        # 设置控件字体
        mainfont = FltkFont(name='微软雅黑', size=18, style=0)
        mainfont(self.text2, self.text3, self.text4)

    def resize(self):
        # 调整窗口、控件位置及大小
        _w, _h = int(self.formfltk.w()*0.618), int(self.formfltk.h()*0.618)
        self.formfltk.size_range(_w, _h)
        self.formfltk.resizable(self.sstab1)
        self.sstab1.resizable(self.sstab1_page0)
        self.sstab1_page0.resizable(self.text2)
        self.sstab1_page1.resizable(self.text3)
        self.sstab1_page2.resizable(self.text4)

        self.sstab1.resize(0, self.sstab1.y(),
                           self.formfltk.w(), self.formfltk.h() - self.sstab1.y())
        self.text2.resize(self.sstab1_page0.x(), self.sstab1_page0.y()+1,
                          self.sstab1_page0.w(), self.text2.h())
        self.text3.resize(self.sstab1_page1.x(), self.sstab1_page1.y()+1,
                          self.sstab1_page1.w(), self.sstab1_page1.h())
        self.text4.resize(self.sstab1_page2.x(), self.sstab1_page2.y()+1,
                          self.sstab1_page2.w(), self.text4.h())

    def cb_selfile(self, this):
        dlg = FileDialog()
        vbfile = dlg.showopen(u"选择文件", Filter=u'窗体文件 (*.frm)|*.frm')
        if vbfile:
            vbfilename = vbfile[0]
            self.text1.value(fltktext(vbfilename))
            self.text2_buffer.text('')
            self.text3_buffer.text('')
            self.text4_buffer.text('')
        else:
            return
        #end if

##        if not os.path.isfile(vbfilename): return
        with open(vbfilename, encoding="gbk") as f:
            for line in f:
                if line.startswith('VERSION') or line.startswith('Object'): continue
                if line.startswith('Attribute'): break
                self.text2_buffer.append(fltktext(line))
            #end for
        #end with

        self.sstab1_page0.show()

    def cb_gencode(self, this):
        self.text3_buffer.text('')
        self.text4_buffer.text('')

        vbfilename = getfltktext(self.text1.value())
        if not vbfilename: return
        pycode = PyFltkWin(vbfilename)

        if PY2:
            print(json.dumps(pycode.widgets, indent=4, ensure_ascii=False), file=Print2Fltk(self.text3))
        else:
            pprint(pycode.widgets, stream=Print2Fltk(self.text3))

        if self.option1.value():
            self.text4_buffer.append(pycode.hdr_stmt)

        win_stmt = '\n'.join(pycode.win_stmts)
        self.text4_buffer.append(fltktext(win_stmt))
        if pycode.kls_stmts:
            kls_stmt = '\n'.join(pycode.kls_stmts)
            self.text4_buffer.append(fltktext(kls_stmt))
##        if pycode.tbl_stmts:
##            tbl_stmt = '\n'.join(pycode.tbl_stmts)
##            self.text4_buffer.append(fltktext(tbl_stmt))

        if self.option1.value():
            self.text4_buffer.append(pycode.app_stmt)

    def cb_copyto(self, this, textctrl):
        Fl.copy(textctrl.buffer().text(), textctrl.buffer().length(), 1)    # clipboard (destination is 1)

    def cb_saveto(self, this, textctrl):
        txt = textctrl.buffer().text()
        if not txt: return
        txt = getfltktext(txt)

        vbfilename = getfltktext(self.text1.value())
        pyfilename = os.path.splitext(vbfilename)[0] + '.py'

        dlg = FileDialog()
        pyfilename = dlg.showsave("保存文件", Filter='Python Files (*.py;*.pyw)|*.py;*.pyw')
        if pyfilename:
            with open(pyfilename, 'w', encoding="utf8") as f:
                f.write(txt)

    def start(self, mt=False):
        self.resize()
        self.formfltk.callback(self.on_close)
        self.formfltk.end()
        self.formfltk.show()
        if mt:
            #Fl.mt_run(self.formfltk)
            import time
            while Fl.check(): time.sleep(0.1)  #Fl.wait(0.05)
        else:
            Fl.run()
        #end if

    def on_close(self, this):   # Fl.event()=FL_CLOSE，窗口关闭时执行以下代码
        # this.hide()
        # sys.exit(0)
        Fl.fltk_exit()


if __name__ == '__main__':
    app = FormFltkProc()
    app.start()
