# -*- coding: utf8 -*-

from __future__ import print_function

import sys

import io
from subprocess import Popen, PIPE, STARTUPINFO, STARTF_USESHOWWINDOW, SW_HIDE

from fltk import *

PY2 = sys.version_info[0]==2
PY3 = sys.version_info[0]==3

def fltkstr(txtstr):     # txtstr: unicode string
    """在pyfltk中能正确显示PY2、PY3及兼容pyinstaller打包的字符串
    """
    if PY2:
        try:
            txtstr = txtstr.encode('utf8')
        except UnicodeDecodeError:
            try:    ## 用pyinstaller打包时，如果print语句所在模块是gbk，会乱码
                txtstr = txtstr.decode('gbk').encode('utf8')
            except Exception as err:
                txtstr = txtstr #repr(err) #'字符编码错误！'
    #end if PY2
    return txtstr

class Print2Fltk(object):
    def __init__(self, ctrl):
        self.text_ctrl = ctrl

    def flush(self):    # PY3 必须有
        pass
##        Fl.flush()

    def write(self, output_stream):     # output_stream: unicode string
##        if PY2:   # 用pyinstaller打包时，如果print语句所在模块是gbk，会乱码
##            try:
##                output_stream = output_stream.encode('utf8')
##            except UnicodeDecodeError:
##                output_stream = output_stream

        output_stream = fltkstr(output_stream)
        buff = self.text_ctrl.buffer()
        buff.append(output_stream)
        self.text_ctrl.scroll(buff.length(), 1)


class StatusBar(Fl_Box):
    def __init__(self, x, y, w, h):
        Fl_Box.__init__(self, x, y, w, h, None)
##        self.box(FL_PLASTIC_THIN_UP_BOX)
        self.box(FL_THIN_DOWN_BOX)
        self.align(FL_ALIGN_LEFT + FL_ALIGN_INSIDE)

    def flush(self):    # PY3 必须有
        pass            # Fl_Box不需要

    def label(self, txtstr):
        txtstr = fltkstr(txtstr)
        Fl_Box.label(self, txtstr)

    def write(self, txtstr):
        # print(arg1, arg2, ...)重定向过来时会依次传入
        # arg1, sep=' ', arg2, ..., argn, end='\n'
        # 因此只有argn有效，并且要忽略end, 默认是'\n'
##        print(repr(txtstr))
        if txtstr != '\n':
            self.label(txtstr)


class Cmd4Fltk(object):
    def __init__(self):
        self._isrunning = False
        self._endline = None

    def run(self, cmdline, endline=None):
        self._endline = endline
        if PY2:
            st=STARTUPINFO
            st.dwFlags=STARTF_USESHOWWINDOW
            st.wShowWindow=SW_HIDE
        else:
            st = STARTUPINFO(dwFlags=STARTF_USESHOWWINDOW, wShowWindow=SW_HIDE)

        self._cmd_proc = Popen(cmdline, shell=True, startupinfo=st,
                               stdout=PIPE, stdin=PIPE, stderr=PIPE)
        Fl.add_idle(self._reprint, self._cmd_proc)

    def _reprint(self, cmd_proc):
        self._isrunning = True
        self._cmd_out = io.open(cmd_proc.stdout.fileno(), 'rb', closefd=False)
        # windows控制台默认编码是gbk
        buf = self._cmd_out.read1(io.DEFAULT_BUFFER_SIZE).decode('gbk')
        if not buf:
            self._close()
            return
        print(buf, end='') if PY2 else print(buf, end='', flush=True)

    def _close(self):
        self._isrunning = False
        self._cmd_out.close()
        if self._endline: print(self._endline)
        Fl.remove_idle(self._reprint, self._cmd_proc)

    def abort(self):
        if self._isrunning:
            self._close()
            print(u'\n< ^C 用户中断! >\n')


class FltkFont(object):
    def __init__(self, name='微软雅黑', size=16, style=0):
        """name: fontname, utf8
        style: normal = 0; bold = 1; italic = 2; bold italic 3
        """
        self._fontname = name
        self._fontsize = size
        # style: bold = 1; italic = 2; bold italic 3
        self._fontstyle = style if 0 <= style <= 3 else 0
        self._fontface = self._get_font_face(name)

    @property
    def font(self):
        return self._fontface

    @staticmethod
    def _get_font_face(name):
        flfont = FL_HELVETICA
        for i in range(Fl.set_fonts('-*')):
            fnt = Fl.get_font_name(i)
            if fnt[0]==name:
                flfont = i
                break
        return flfont

    @staticmethod
    def _modify(fl_ctl, face, size, style):
        if hasattr(fl_ctl, 'textfont'):
            fl_ctl.textfont(face + style)
            fl_ctl.textsize(size)
        if hasattr(fl_ctl, 'labelfont'):
            fl_ctl.labelfont(face + style)
            fl_ctl.labelsize(size)

    def set(self, *ctrls, **fontattrs):
        name = fontattrs.get('name', self._fontname)
        size = fontattrs.get('size', self._fontsize)
        style = fontattrs.get('style', self._fontstyle)
        style = style if 0 <= style <= 3 else 0
        face = self._get_font_face(name)

        for ctrl in ctrls:
            self._modify(ctrl, face, size, style)

##    def change(self, ctrl, **fontattrs):
##        name = fontattrs.get('name', self._fontname)
##        size = fontattrs.get('size', self._fontsize)
##        style = fontattrs.get('style', self._fontstyle)
##        style = style if 0 <= style <= 3 else 0
##        face = self._get_font_face(name)
##        self._modify(ctrl, face, size, style)


