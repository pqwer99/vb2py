# -*- coding: utf8 -*-

from __future__ import print_function

import sys
import platform
import io
from subprocess import Popen, PIPE, STARTUPINFO, STARTF_USESHOWWINDOW, SW_HIDE

from fltk import *

PY2 = sys.version_info[0]==2
PY3 = sys.version_info[0]==3

X86 = platform.architecture()[0]=='32bit'
X64 = platform.architecture()[0]=='64bit'

def fltkstr(txtstr):
    """在pyfltk中能正确显示PY2、PY3及兼容pyinstaller打包的字符串
    用pyinstaller打包时，如果print语句所在模块是gbk，会乱码
    """
    return fltktext(txtstr)

def fltktext(txtstr):
    """[in]:txtstr is gbk or utf8 or u'string'; [Return]: utf8
    PY2中字符串要么是文件的编码(gbk,utf8)、要么是u'string',而pyfltk只使用utf8
    """
    if PY2:
        if isinstance(txtstr, unicode):
            txtstr = txtstr.encode('utf8')      # u'txtstr'
        else:
            try:
                txtstr.decode('utf8')     # txtstr is 'utf8'
            except UnicodeDecodeError as err:
                #PY2中，重定向Print中的值也是gbk编码
                txtstr = txtstr.decode('gbk').encode('utf8')    # txtstr is 'gbk'
    #end if PY2
    return txtstr

def setfltktext(txtstr):
    """在pyfltk中能正确显示PY2、PY3及兼容pyinstaller打包的字符串
    用pyinstaller打包时，如果print语句所在模块是gbk，会乱码
    """
    return fltktext(txtstr)

def getfltktext(txtstr):
    """[in]:txtstr is utf8; [Return]: unicode
    在PY2中,解码pyfltk控件中的label,text等相关属性值(utf8)
    """
    if PY2:
        try:
            txtstr = txtstr.decode('utf8')
        except:
            txtstr = txtstr #repr(err) #'字符编码错误！'
    #end if PY2
    return txtstr

class Print2Fltk(object):
    def __init__(self, ctrl):
        self.text_ctrl = ctrl

    def flush(self):    # PY3 必须有
        pass
##        Fl.flush()

    def write(self, output_stream):
        text = fltktext(output_stream)     #转换成pyfltk的字符串
        if isinstance(self.text_ctrl, (Fl_Text_Editor, Fl_Text_Display)):
            buff = self.text_ctrl.buffer()
            buff.append(text)
            self.text_ctrl.scroll(buff.length(), 1)
        elif isinstance(self.text_ctrl, Fl_Box):
            # print(arg1, arg2, ...)重定向过来时会依次传入
            # arg1, sep=' ', arg2, ..., argn, end='\n'
            # 因此只有argn有效，并且要忽略end, 默认是'\n'
    ##        print(repr(txtstr))
            if text != '\n': self.text_ctrl.label(text)


class Cmd4Fltk(object):
    def __init__(self):
        self._isrunning = False
        self._endline = None

    def run(self, cmdline, endmsg=None):
        self._end_msg = endmsg
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
            self._close(self._end_msg)
            return
        print(buf, end='') if PY2 else print(buf, end='', flush=True)

    def _close(self, closemsg):
        self._isrunning = False
        self._cmd_out.close()
        if closemsg: print(closemsg)
        Fl.remove_idle(self._reprint, self._cmd_proc)

    def abort(self, abortmsg=u'\n< ^C 用户中断! >\n'):
        if self._isrunning:
            self._close(abortmsg)


class FltkFont(object):
    def __init__(self, name='微软雅黑', size=16, style=0):
        """name: fontname, utf8
        style: normal = 0; bold = 1; italic = 2; bold italic 3
        """
        self._fontname = name
        self._fontsize = size
        self._fontstyle = style if 0 <= style <= 3 else 0

    @property
    def font(self):
        return self._get_font_face(self._fontname)

    @staticmethod
    def _get_font_face(fontname):
        flfont = FL_HELVETICA
        if isinstance(fontname, str):
            fcount = Fl.set_fonts('-*')
            # 安装某些字体后，32位python，set_fonts('-*')会退出
            # 已确认 霞鹜等宽文楷
##            fcount = Fl.set_fonts() if X86 else Fl.set_fonts('-*')
            for i in range(fcount):
                fnt = Fl.get_font_name(i)
                if fnt[0]==fontname:
                    flfont = i
                    break
                #end if
            #end for
        elif isinstance(fontname, int):
            flfont = fontname
        #end if
        return flfont

    @staticmethod
    def _modify(fl_ctl, face, size, style):
        if hasattr(fl_ctl, 'textfont'):
            fl_ctl.textfont(face + style)
            fl_ctl.textsize(size)
        if hasattr(fl_ctl, 'labelfont'):
            fl_ctl.labelfont(face + style)
            fl_ctl.labelsize(size)

    def __call__(self, *ctrls, **fontattrs):
        name = fontattrs.get('name', self._fontname)
        size = fontattrs.get('size', self._fontsize)
        style = fontattrs.get('style', self._fontstyle)
        style = style if 0 <= style <= 3 else 0
        face = self._get_font_face(name)

        for ctrl in ctrls:
            self._modify(ctrl, face, size, style)


if __name__ == '__main__':

    class AppMainForm(object):
        def __init__(self):
            self.mainform = Fl_Window(400,200,487,376)
    ##        self.mainform = Fl_Window(387,376)
            self.mainform.label('标题')
            self.mainform.color(FL_LIGHT2)

            tooltip_font = FL_FREE_FONT
            Fl.set_font(tooltip_font, "STCAIYUN")
            Fl_Tooltip.font(tooltip_font)
            Fl_Tooltip.size(16)
            Fl_Tooltip.textcolor(FL_GREEN)

            self.button_1 = Fl_Button(20, 20, 100, 30, '测试')
            self.button_1.tooltip("Tooltip String")
            self.button_2 = Fl_Button(140, 20, 100, 30, 'Button2')
            self.button_3 = Fl_Button(260, 20, 100, 30, fltktext(u'字体列表'))

            self.stat_1 = Fl_Box(0, self.mainform.h()-30, self.mainform.w(), 30) #, 'rthfdghdfhgfghdfgdfgdfg')
            self.stat_1.box(FL_THIN_DOWN_BOX)
            self.stat_1.align(FL_ALIGN_LEFT + FL_ALIGN_INSIDE)
            self.stat_1.label('状态栏！！！')

            self.text_log = Fl_Text_Display(0, 80, self.mainform.w(), self.mainform.h()-80-self.stat_1.h())
            self.text_log.textsize(16)
            self.log_buff = Fl_Text_Buffer()
            self.text_log.buffer(self.log_buff)

            mainfont = FltkFont(name='微软雅黑', size=18, style=0)
##            mainfont = FltkFont(name=320, size=18, style=0)
            mainfont(self.button_1, self.button_2, self.text_log, self.stat_1)

            bntfont = FltkFont(name='@微软雅黑')
            self.button_3.labelfont(bntfont.font)
            self.button_3.labelsize(24)

            self.r_obj = Print2Fltk(self.text_log)
            sys.stdout = self.r_obj
            sys.stderr = self.r_obj


    class ExamApp(AppMainForm):
        def __init__(self):
            super(ExamApp, self).__init__()
            self.button_1.callback(self.button_callback)
            self.button_2.callback(self.button_callback)
            self.button_3.callback(self.button_callback)

        def button_callback(self, this):
            if this is self.button_1:
                print('中文')
                print(u"u' 中文")
                print(u'打印状态栏', file=Print2Fltk(self.stat_1))
    ##            self.stat_1.label('utf8 中文')
            elif this is self.button_2:
                print(self.button_2.label())
                self.stat_1.label(self.button_2.label())
            elif this is self.button_3:
                for i in range(Fl.set_fonts('-*')):
                    fnt = Fl.get_font_name(i)
                    fontname = fnt[0].decode('utf8') if PY2 else fnt[0]
                    print(i, fontname, fnt[1])
                    print(self.button_3.label(), file=Print2Fltk(self.stat_1))
                #end for
            #end if

        def start(self, mt=False):
            self.mainform.end()
            self.mainform.show()
            if mt:
                while Fl.check(): Fl.wait(0.05)
            else:
                Fl.run()
            #end if

    app = ExamApp()
    app.start()
