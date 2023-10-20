# -*- coding: utf8 -*-

from __future__ import print_function

import sys
import os.path
from pprint import pprint
import json

from fltk import *

from fltk_ext import *
from dialogbox import FileDialog

from fltk_vbform import PyFltkWin, T

PY2 = sys.version_info[0] == 2

mainfont = FltkFont(name='微软雅黑', size=18, style=0)
fl_setfont = mainfont.set

class FormFltk(object):
    def __init__(self):
        self.formfltk = Fl_Window(T(9360), T(6612), "VB.Form -> pyfltk")
        self.formfltk.color(FL_LIGHT2)
        self._MenuBarH = 300  # MenuBar height
        self._ComboBoxH = 330   # ComboBox extent height

        self.text1 = Fl_Output(T(2400+0), T(225+0), T(6600), T(360), )
        self.text1.value("Text1")
        self.command1 = Fl_Button(T(315+0), T(210+0), T(1800), T(360), "选择文件")
        # bulid tabs widget
        self.tab_sstab1()

    def tab_sstab1(self):
        self.sstab1 = Fl_Tabs(T(45), T(795), T(9270), T(5775))
        TabsLabelH = 330   # Tabs Label height

        self.sstab1_page0 = Fl_Group(T(45), T(795+TabsLabelH), T(9270), T(5775-TabsLabelH), " Frm文件 ")
        if self.sstab1_page0:
            self.text2 = Fl_Text_Display(T(48+45), T(375+795), T(9180), T(4605), )
            self.text2_buffer = Fl_Text_Buffer()
            self.text2.buffer(self.text2_buffer)
            self.text2.show_cursor()
            self.command2 = Fl_Button(T(2190+45), T(5145+795), T(1800), T(360), "生成代码")
            self.option1 = Fl_Radio_Round_Button(T(4455+45), T(5175+795), T(1140), T(360), "全部源码")
            self.option1.value(-1)
            self.option2 = Fl_Radio_Round_Button(T(5820+45), T(5175+795), T(1140), T(360), "仅界面类")
            self.option2.value(0)
        self.sstab1_page0.end()

        self.sstab1_page1 = Fl_Group(T(45), T(795+TabsLabelH), T(9270), T(5775-TabsLabelH), " 过程数据 ")
        if self.sstab1_page1:
            self.text3 = Fl_Text_Display(T(48+45), T(375+795), T(9180), T(5385), )
            self.text3_buffer = Fl_Text_Buffer()
            self.text3.buffer(self.text3_buffer)
            self.text3.show_cursor()
        self.sstab1_page1.end()

        self.sstab1_page2 = Fl_Group(T(45), T(795+TabsLabelH), T(9270), T(5775-TabsLabelH), " 程序代码 ")
        if self.sstab1_page2:
            self.text4 = Fl_Text_Display(T(48+45), T(375+795), T(9180), T(4605), )
            self.text4_buffer = Fl_Text_Buffer()
            self.text4.buffer(self.text4_buffer)
            self.text4.show_cursor()
            self.command3 = Fl_Button(T(2190+45), T(5145+795), T(1800), T(360), "复制到剪贴板")
            self.command4 = Fl_Button(T(4815+45), T(5145+795), T(1800), T(360), "保存到文件")
        self.sstab1_page2.end()

        self.sstab1.end()

class FormFltkProc(FormFltk):
    def __init__(self):
        FormFltk.__init__(self)
        #
        self.text1.value('')# r'E:\My PY\Projects\VB6\Form_vb2py.frm')
        #
        self.resize()
        self.command1.callback(self.cb_selfile)
        self.command2.callback(self.cb_gencode)
        self.command3.callback(self.cb_copyto, self.text4)
        self.command4.callback(self.cb_saveto, self.text4)
        #
        fl_setfont(self.text2, self.text3, self.text4)
        #
        self.text4.show_cursor(self.text4.HEAVY_CURSOR)
        #
        self.formfltk.end()
        self.formfltk.show()

    def run(self):
        Fl.mt_run(self.formfltk)

    def resize(self):
        self.sstab1.resize(0, self.sstab1.y(),
                           self.formfltk.w(), self.formfltk.h() - self.sstab1.y())
        self.text2.resize(self.sstab1_page0.x(), self.sstab1_page0.y()+1,
                          self.sstab1_page0.w(), self.text2.h())
        self.text3.resize(self.sstab1_page1.x(), self.sstab1_page1.y()+1,
                          self.sstab1_page1.w(), self.sstab1_page1.h())
        self.text4.resize(self.sstab1_page2.x(), self.sstab1_page2.y()+1,
                          self.sstab1_page2.w(), self.text4.h())

        self.sstab1_page0.resizable(self.text2)
        self.sstab1_page1.resizable(self.text3)
        self.sstab1_page2.resizable(self.text4)
        self.sstab1.resizable(self.sstab1_page0)
        self.formfltk.resizable(self.sstab1)
##        self.formfltk.resizable(self.sstab1_page0)

    def cb_selfile(self, this):
        dlg = FileDialog(u"选择文件")
        dlg.filterstr = u'窗体文件 (*.frm)|*.frm'
        if dlg.showopen():
            vbfilename = fltkstr(dlg.filename)
            self.text1.value(vbfilename)
            self.text2_buffer.text('')
            self.text3_buffer.text('')
            self.text4_buffer.text('')
        else:
            return

##        if not os.path.isfile(vbfilename): return
        with open(vbfilename) as f:
            for line in f:
                if line.startswith('VERSION') or line.startswith('Object'): continue
                if line.startswith('Attribute'): break
                self.text2_buffer.append(fltkstr(line))

    def cb_gencode(self, this):
        self.text3_buffer.text('')
        self.text4_buffer.text('')

        vbfilename = self.text1.value()
        if not vbfilename: return
        pycode = PyFltkWin(vbfilename)

        pprint(pycode.widgets, stream=Print2Fltk(self.text3))
##        print(json.dumps(pycode.widgets, indent=4, ensure_ascii=False), file=Print2Fltk(self.text3))

        if self.option1.value():
            self.text4_buffer.append(pycode.hdr_stmt)

        win_stmt = '\n'.join(pycode.win_stmts)
        self.text4_buffer.append(fltkstr(win_stmt))
        if pycode.kls_stmts:
            kls_stmt = '\n'.join(pycode.kls_stmts)
            self.text4_buffer.append(fltkstr(kls_stmt))
        if pycode.tbl_stmts:
            tbl_stmt = '\n'.join(pycode.tbl_stmts)
            self.text4_buffer.append(fltkstr(tbl_stmt))

        if self.option1.value():
            self.text4_buffer.append(pycode.app_stmt)

    def cb_copyto(self, this, textctrl):
        Fl.copy(textctrl.buffer().text(), textctrl.buffer().length(), 1)    # clipboard (destination is 1)

    def cb_saveto(self, this, textctrl):
        vbfilename = self.text1.value()
        txt = textctrl.buffer().text()
        if not txt: return
        pyfilename = os.path.splitext(vbfilename)[0] + '.py'

        dlg = FileDialog(u"保存文件")
        dlg.filterstr = 'Python Files (*.py;*.pyw)|*.py;*.pyw'
        dlg.filename = pyfilename
        if dlg.showsave():
            pyfilename = fltkstr(dlg.filename)
            with open(pyfilename, 'w') as f:
                f.write(txt)


if __name__ == '__main__':
    app = FormFltkProc()
    app.run()

