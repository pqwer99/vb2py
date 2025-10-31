# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
##from __future__ import unicode_literals

import io
import re
import sys

from ctypes import windll
from pprint import pprint
from collections import OrderedDict

from fltk import __version__ as fltkver

from fltk_pytmpl import fltk_widgets, hdr_stmt, app_stmt, kls_stmt

__all__ = ['PyFltkWin', 'T']

PY2 = sys.version_info[0]==2
if PY2:
    open = io.open

def __getdpi():
    GetDC = windll.user32.GetDC
    GetDeviceCaps = windll.gdi32.GetDeviceCaps
    ##Private Declare Function GetDC Lib "user32" (ByVal hWnd As Long) As Long
    ##Private Declare Function GetDeviceCaps Lib "gdi32" (ByVal hDC As Long, ByVal nIndex As Long) As Long
    LOGPIXELSX = 88        #  Logical pixels/inch in X

    return GetDeviceCaps(GetDC(None), LOGPIXELSX) / 96.0     # 96为设备绘制为100%大小时dpi

if fltkver >= "1.4":
    def T(twips):
        return int(twips / 15)
else:
    DPI = __getdpi()

    def T(twips, dpi=DPI):
        return int(twips / 15 * dpi)

def __getclienttop():
    GetSystemMetrics = windll.user32.GetSystemMetrics
    SM_CYFRAME = 33
    SM_CYCAPTION = 4
##    SM_CYBORDER = 6
    SM_CYMENU = 15
    FrameH = GetSystemMetrics(SM_CYFRAME)     # Total height, Top + Bottom
    CaptionH = GetSystemMetrics(SM_CYCAPTION)
##    BorderH = GetSystemMetrics(SM_CYBORDER)   # Border around Client area
    MenuH = GetSystemMetrics(SM_CYMENU)   # Border around Client area
    return int(CaptionH + MenuH) * 15

CLIENTTOPWITHMENU = __getclienttop()

def user_class(tag):
    pattern = r'(^\D\w*)\s*\(\s*(\w*)\s*\)'
    m = re.match(pattern, tag)
    return m.groups() if m else None

tabspack = ['sstab', 'sstabex']
grouppack=['frame', 'splitter']

class VbFormParser(object):
    def __init__(self, filename):
        self.filename = filename
        self.rootwin = None
        self._MenuBarH = 300  # 菜单高度 GetSystemMetrics(SM_CYMENU:=15)*15/DPI

        self.widgets = dict()    # {widget1:{attr_name:attr_value, ...}, ...}; 每个窗体只允许254个控件名的固定限制
        self.groups = OrderedDict()     # {group1:[(tabindex, ctrl_name), ...], ...}; 最多25层嵌套控件
        self.__widgetstacks = []       # 容器栈：[窗体, 控件[容器], 控件...]

        self.parse_vbform()

    def parse_vbform(self):
        with open(self.filename, encoding="gbk") as f:
            self.__proc_frmfile(f)

    def __proc_frmfile(self, f):
        prop_name = ''
        for line in f:
            line = line.strip()
            if line.startswith('VERSION') or line.startswith('Object'): continue
            if line.startswith('Attribute'): break
            if line.startswith('BeginProperty'):    # 属性块，如 Font...
                prop_name = line.lower().split()[1]; continue
            if line.startswith('EndProperty'):
                prop_name = ''; continue

            if line.startswith('Begin'):    # Begin VB.Form Form1
                vb_ctrl = line.split()      # 控件类型、名称
                obj_name = vb_ctrl[2]       # 保留大小写，作为fltk窗口类名称
                vb_type, vb_name = vb_ctrl[1].lower(), vb_ctrl[2].lower()

                self.__widgetstacks.append(vb_name) # 入栈

                self.widgets[vb_name] = {'type': vb_type}

                if vb_type == 'vb.form':
                    self.rootwin = vb_name  # 根窗口
                    self.winclass = obj_name
                    self.groups.setdefault(vb_name, [])
                    self.widgets[vb_name].update({'__dx__': 0})
                    self.widgets[vb_name].update({'__dy__': 0})
                else:   # 窗口上的控件
                    group = self.__widgetstacks[-2]     # 容器, (-1 = 当前控件 = vb_name)
                    # 增加 控件拥用者属性
                    self.widgets[vb_name].update({'__owner__': group})
                    if vb_type.split(".")[1] in tabspack + grouppack + ['menu',]: #['sstab', 'sstabex', 'frame', 'splitter', 'menu']:   # 既是控件也是容器， Begin 嵌套 End
                        self.groups.setdefault(vb_name, [])
                        if vb_type.split(".")[1] in tabspack + grouppack: #['sstab', 'sstabex', 'frame', 'splitter']:
                            # 增加 容器偏移量属性
                            dx = self.widgets[group].get('__dx__', 0)
                            dy = self.widgets[group].get('__dy__', 0)
                            self.widgets[vb_name].update({'__dx__': dx})
                            self.widgets[vb_name].update({'__dy__': dy})
                        #end if
                    #end if
               #end if vb_type
            elif line.startswith('End'):
                # 出栈
                widget = self.__widgetstacks.pop()  # 当前部件 != vb_name
                if self.__widgetstacks:     # 将控件放入所属容器
                    group = self.__widgetstacks[-1]   #容器
                    # 有些控件如 vb.image 没有tabindex，默认 -1
                    self.groups[group].append((self.widgets[widget].get('tabindex', -1), widget))
                    self.groups[group].sort(key=lambda x:x[0])   # 为以后创建控件顺序准备
                else:
                    # 此时 widget是窗体名
                    tag = self.widgets[widget].get('tag', '')[1:-1]
                    try:    # 如果有合法的tag名称, 作为fltk窗口类名称
                        exec("{}=1".format(tag))
                        self.winclass = tag
                    except:
                        pass
                    #end try
                    break   # 最后一个End,窗体结束
                #end if
            else:   # 控件属性字典
                attr = line.split('=')
                attr_name, attr_value = attr[0].strip().lower(), attr[1].strip()

                if attr_name=='clienttop':  # 窗口内的偏移
                    clienttop = int(attr_value)
                    if clienttop >= CLIENTTOPWITHMENU:    # >=840 可能有菜单
                        self.widgets[vb_name]['__dy__'] = self._MenuBarH

                # 预处理属性值
                if attr_name in ['caption', 'simpletext', 'text', 'tag', 'tooltiptext']:
                    attr_value = attr_value.strip()
                else:
                    attr_value = attr_value.split("'")[0].strip()   # 忽略注释
                if prop_name: attr_name = prop_name + '_' + attr_name   # 属性块里的：加上前缀

                # Value: CheckBox(0,1,2), OptionButton(False,True), Slider
                if attr_name in ['tabindex', 'value']: attr_value = int(attr_value)
                if attr_name=='left':
                    attr_name = 'x'
                    attr_value = int(attr_value)
#--------------------------------------------------------------------
                    attr_value = 0 if attr_value==-15 else attr_value
#--------------------------------------------------------------------
                    # sstab中，非当前页面控件的left=实际值-75000
##                    attr_value = 75000 + attr_value if attr_value<-50000 else attr_value
                    if attr_value < -50000:
                        attr_value = 75000 + attr_value
                    # 设置偏移量dx
                    if vb_type.split(".")[1] in tabspack + grouppack:   #['sstab', 'sstabex', 'frame', 'splitter']:
                        self.widgets[vb_name]['__dx__'] += attr_value
                if attr_name=='top':
                    attr_name = 'y'
                    attr_value = int(attr_value)
#--------------------------------------------------------------------
                    attr_value = 0 if attr_value==-15 else attr_value
#--------------------------------------------------------------------
                    # 设置偏移量dy
                    if vb_type.split(".")[1] in tabspack + grouppack:   #['sstab', 'sstabex', 'frame', 'splitter']:
                        self.widgets[vb_name]['__dy__'] += attr_value
                if attr_name in ['width', 'clientwidth']: attr_name = 'w'
                if attr_name in ['height', 'clientheight']: attr_name = 'h'
                if attr_name in ['w', 'h', 'tabheight']: attr_value = int(attr_value)

                self.widgets[vb_name].update({attr_name:attr_value})
            #end if
        #end for -----> line

def indent(i):
    return ' ' * i * 4
I = indent

class PyFltkWin(VbFormParser):
    def __init__(self, filename):
        super(PyFltkWin, self).__init__(filename)
##        pprint(self.widgets)
##        pprint(dict(self.groups))
        self.tabpages = OrderedDict()
        self.win_stmts = list()
        self.tbl_stmts = list()
        self.kls_stmts = list()

        self.user_class = set()

        self.build_winclass()

        self.hdr_stmt = hdr_stmt
        self.app_stmt = app_stmt.format(self.rootwin, self.winclass)

    def build_winclass(self):
        # 首先构造窗体类
        win = self.rootwin
        win_attrs = self.widgets.get(win)
        w, h = win_attrs.get('w', 0), win_attrs.get('h', 0)
        dx, dy = win_attrs.get('__dx__', 0), win_attrs.get('__dy__', 0)
        label = win_attrs.get('caption', '""')

        ctrls = self.groups.pop(win)

        # 菜单默认高度 = 300
        # vb.combobox(默认276|300)的高度不能调整，在fltk中显示太小，= 330
        stmt = 'class {1}(object):\n'  \
               '    def __init__(self):\n' \
               '        self.{0} = Fl_Double_Window(T({2}), T({3}), {4})\n' \
               '        #\n' \
               '        self._MenuBarH = 300  # MenuBar height\n' \
               '        self._ComboBoxH = 330   # ComboBox extent height\n'
        self.win_stmts.append(stmt.format(self.rootwin, self.winclass, w, h+dy, label))

        # 构造直属 Fl_Windows 的部件
        self.build_widgets(ctrls, dx, dy)
        self.win_stmts.append('')

        # 如果窗体包含有 Group 和 Tabs
        for group in self.groups:
            group_attrs = self.widgets.get(group)
            x, y = group_attrs.get('x', 0), group_attrs.get('y', 0)
            w, h = group_attrs.get('w', 0), group_attrs.get('h', 0)
            dx, dy = group_attrs.get('__dx__', 0), group_attrs.get('__dy__', 0)

            if group_attrs['type'].split(".")[1] in ["frame", "splitter"]: #== 'vb.frame':
                borderstyle = bool(int(group_attrs.get('borderstyle', 1)))
                borderstyle = 'FL_ENGRAVED_FRAME' if borderstyle else 'FL_NO_BOX'
                label = group_attrs.get('caption', '""')

                frame = group
                stmt = '    def creategroup_{0}(self):\n'  \
                       '        self.{0} = Fl_Group(T({1}), T({2}), T({3}), T({4}), {5})\n' \
                       '        self.{0}.box({6})\n' \
                       '        self.{0}.align(FL_ALIGN_TOP_LEFT + FL_ALIGN_INSIDE)\n' \
                       '        self.{0}.labeltype(FL_NORMAL_LABEL)\n'
                self.win_stmts.append(stmt.format(frame, dx, dy, w, h, label, borderstyle))

                ctrls = self.groups[frame]
                # 构造 Fl_Group 内的部件
                self.build_widgets(ctrls, dx, dy)

                self.win_stmts.append('')
                self.win_stmts.append(I(2) + 'self.{}.end()'.format(frame))
                self.win_stmts.append('')
            #end if -----> vb.frame

##            if group_attrs['type'] == 'tabdlg.sstab':
            if group_attrs['type'].split(".")[1] in tabspack:   #["sstab", "sstabex"]:
                tabheight = int(group_attrs.get('tabheight', 300*1.76) / 1.76) # frm/ide=1.76

                sstab = group
                # 定义 Fl_Tabs
                stmt = '    def createtabs_{0}(self):\n'  \
                       '        self.{0} = Fl_Tabs(T({1}), T({2}), T({3}), T({4}))\n' \
                       '        TabHeight = {5}   # Tabs Label Height\n'
                self.win_stmts.append(stmt.format(sstab, dx, dy, w, h, tabheight))

                # 解析Tab内的控件，对其分页处理
                tabpages, pagenames = self.parse_sstab(sstab)
##                print(tabpages)
                for tabpage in tabpages:
                    tabctrls = tabpages[tabpage]
                    label = pagenames[tabpage]
##                    print(tabctrls)
                    # 分页
                    stmt = '        self.{0} = Fl_Group(T({1}), T({2}+TabHeight), T({3}), T({4}-TabHeight), {5})\n'  \
                           '        if self.{0}:'
                    self.win_stmts.append(stmt.format(tabpage, dx, dy, w, h, label))

                    # 构造 Fl_Tabs 内的部件
                    self.build_widgets(tabctrls, dx, dy, i=3)

                    self.win_stmts.append(I(2) + 'self.{}.end()\n'.format(tabpage))
                #end for -----> tabpage
                self.win_stmts.append(I(2) + 'self.{}.end()'.format(sstab))
                self.win_stmts.append('')
            #end if -----> tabdlg.sstab
        #end for -----> groups

    def parse_sstab(self, sstab):
        """tabdlg.sstab中所有控件按页归类
        """
        _pagectrl_max = _tabpage_max = len(self.groups[sstab])    # 最多99个页面，254个控件
        tab_attrs = self.widgets.get(sstab)
        tabpages = OrderedDict()
        pagenames = dict()

        for i in range(_tabpage_max):
            tabcaption = 'tabcaption({})'.format(i)
            if tabcaption in tab_attrs:
                tabpage = '{}_page{}'.format(sstab, i)     # 自定义页名，VB中没有此项
##                print(tabpage, tab_attrs[tabcaption])
                tabpages.setdefault(tabpage, [])            # 第i页控件List
                pagenames[tabpage] = tab_attrs[tabcaption]  # 第i页标题
                for j in range(_pagectrl_max):   # 遍历第i页控件
                    tabcontrol = 'tab({}).control({})'.format(i, j)
                    if tabcontrol in tab_attrs:
##                        print('-----',tab_attrs[tabcontrol])
                        ctrl_name = tab_attrs[tabcontrol][1:-1].lower()  # 去除两头的引号
                        tabpages[tabpage].append((self.widgets[ctrl_name].get('tabindex', -1), ctrl_name))
                        tabpages[tabpage].sort(key=lambda x:x[0])   # 为以后创建控件顺序准备
                    #end if
                #end for -----> page
            #end if
        #end for -----> tabs
        return tabpages, pagenames

    def build_widgets(self, ctrls, dx=0, dy=0, i=2):  # i=缩进量
        """VB控件转换成fltk widgets，一般格式是：ctrlname = Fl_Xxxx(x, y, w, h, label)
           例如: self.command1 = Fl_Button(x, y, w, h, 'Command1')
        """
        for _, ctrl in ctrls:
            ctrl_attrs = self.widgets.get(ctrl)
            vb_type = ctrl_attrs.get('type')

            tag = ctrl_attrs.get('tag', '""')[1:-1]
            tag_lower = ctrl_attrs.get('tag', '""')[1:-1].lower()

##            appearance = bool(int(ctrl_attrs.get('appearance', 0)))     # 0:Flat, 1:3D
##            borderstyle = bool(int(ctrl_attrs.get('borderstyle', 0)))   # 0:None, 1:Fixed Single

            # =====控件基本属性
            x, y = ctrl_attrs.get('x', 0), ctrl_attrs.get('y', 0),
            w, h = ctrl_attrs.get('w', 0), ctrl_attrs.get('h', 0)
            label = ctrl_attrs.get('caption', None)
            tooltiptext = ctrl_attrs.get('tooltiptext', '')

            widget_stmt = 'self.{} = {}(T({}), T({}), T({}), T({}), {})'.format(ctrl, '{}', x+dx, y+dy, w, h, label)
            # now: widget_stmt = 'self.ctrl = {}(T(x+dx), T(y+dy), T(w), T(h), label)'

            # =====构造控件
            if vb_type.split(".")[1] in tabspack:   #["sstab", "sstabex"]:
                self.win_stmts.append(I(i) + '# bulid tabs widget')
                self.win_stmts.append(I(i) + 'self.createtabs_{}()'.format(ctrl))

            elif vb_type.split(".")[1] in grouppack:    #['frame', 'spliter']
                self.win_stmts.append(I(i) + '# bulid group widget')
                self.win_stmts.append(I(i) + 'self.creategroup_{}()'.format(ctrl))

            elif vb_type ==  'vb.menu':
                self.win_stmts.append(I(i) + 'self.{} = Fl_Menu_Bar(0, 0, self.{}.w(), T(self._MenuBarH))'.format(ctrl, self.rootwin))
                self.win_stmts.append(I(i) + 'self.{}.box(FL_FLAT_BOX)'.format(ctrl))
                self.win_stmts.append('')

            elif vb_type == 'vb.picturebox':
                stmt = widget_stmt.format('Fl_Box')
                if tag_lower in fltk_widgets:    # 主要是替代VB没有的控件
                    stmt = widget_stmt.format(fltk_widgets[tag_lower])
                else:
                    v = user_class(tag)
                    if v:    # 有自定义类
                        kls, kls_inh = v
                        stmt = 'self.{} = {}(x=T({}), y=T({}), w=T({}), h=T({}), l={})'.format(ctrl, kls, x+dx, y+dy, w, h, label)
                        if kls not in self.user_class:
                            self.user_class.add(kls)
                            self.kls_stmts.append(kls_stmt.format(kls, kls_inh))
                        #end if -----> kls
                    #end if -----> v
                #end if -----> tag_lower
                self.win_stmts.append(I(i) + stmt)

            elif vb_type == 'vb.label':
                alignment = int(ctrl_attrs.get('alignment', 0))     # 0:left, 1:right, 2:center
                align = ('FL_ALIGN_LEFT', 'FL_ALIGN_RIGHT', 'FL_ALIGN_CENTER')[alignment]
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Box'))
                self.win_stmts.append(I(i) + 'self.{}.align({} + FL_ALIGN_INSIDE)'.format(ctrl, align))
                borderstyle = bool(int(ctrl_attrs.get('borderstyle', 0)))   # 0:None, 1:Fixed Single
                if borderstyle:
                    self.win_stmts.append(I(i) + 'self.{}.box(FL_BORDER_BOX)'.format(ctrl) + ' # fltk:323')

            elif vb_type == 'vb.textbox':
                txt = ctrl_attrs.get('text', '""')
                is_textstyle = False  # Fl_X_Input/Output有value, Fl_Text_Editor无

                # tag的优先
                if tag_lower in ['fl_text_editor', 'fl_text_display']:
                    is_textstyle = True
                    self.win_stmts.append(I(i) + widget_stmt.format(fltk_widgets[tag_lower]))
                    self.win_stmts.append(I(i) + 'self.{}_buffer = Fl_Text_Buffer()'.format(ctrl))
                    self.win_stmts.append(I(i) + 'self.{0}.buffer(self.{0}_buffer)'.format(ctrl))
                    if tag_lower=='fl_text_display':
                        self.win_stmts.append(I(i) + 'self.{0}.show_cursor()'.format(ctrl))
                elif tag_lower == 'fl_file_input':
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_File_Input'))
                elif tag_lower in ['fl_float_input', 'fl_int_input']:
                    self.win_stmts.append(I(i) + widget_stmt.format(fltk_widgets[tag_lower]))
                    try:    # 字符型数字
                        float(txt[1:-1])
                    except:
                        txt = '"0"'
                elif tag_lower in ['fl_spinner', 'fl_value_input']:
                    self.win_stmts.append(I(i) + widget_stmt.format(fltk_widgets[tag_lower]))
                    try:
                        txt = float(txt[1:-1])
                    except:
                        txt = 0
                elif tag_lower=='fl_secret_input' or bool(ctrl_attrs.get('passwordchar', '')):
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Secret_Input'))
                else:
                    multiline = bool(int(ctrl_attrs.get('multiline', 0)))   # True/False
                    locked = bool(int(ctrl_attrs.get('locked', 0)))     # True/False
                    if multiline and locked:
                        self.win_stmts.append(I(i) + widget_stmt.format('Fl_Multiline_Output'))
                        txt = '""' #txt.split(':')[0]     #  ="Form8.frx":000C
                    elif multiline and (not locked):
                        self.win_stmts.append(I(i) + widget_stmt.format('Fl_Multiline_Input'))
                        txt = '""' #txt.split(':')[0]
                    elif (not multiline) and locked:
                        self.win_stmts.append(I(i) + widget_stmt.format('Fl_Output'))
                    else:
                        self.win_stmts.append(I(i) + widget_stmt.format('Fl_Input'))
                #end if -----> tag_lower
                if not is_textstyle: self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, txt))

            elif vb_type == 'vb.commandbutton':
                if not tag_lower and bool(int(ctrl_attrs.get('default', 0))):
                    tag_lower = 'fl_return_button'    # default: True/False

                if tag_lower in ['fl_light_button', 'fl_return_button', 'fl_toggle_button', 'fl_menu_button']:
                    self.win_stmts.append(I(i) + widget_stmt.format(fltk_widgets[tag_lower]))
                    if tag_lower == 'fl_light_button':
                        self.win_stmts.append(I(i) + 'self.{}.align(FL_ALIGN_CENTER) # fltk:750'.format(ctrl))
                    #end if -----> fl_light_button
                else:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Button'))
                #end if

            elif vb_type == 'vb.checkbox':
                val = int(ctrl_attrs.get('value', 0))   # 0:unchecked 1:checked 2:grayed
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Check_Button'))
                self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, val))

            elif vb_type == 'vb.optionbutton':
                val = int(ctrl_attrs.get('value', 0))   # True/False
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Radio_Round_Button'))
                self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, val))

            elif vb_type == 'vb.combobox':
                if ctrl_attrs.get('style', '0') == '0':     # dropdown combo 可编辑
##                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Input_Choice'))
                    self.win_stmts.append(I(i) + 'self.{} = Fl_Input_Choice(T({}), T({}), T({}), T(self._ComboBoxH))'.format(ctrl, x+dx, y+dy, w))
                    self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, ctrl_attrs.get('text', '')))
                else:   # dropdown list 不能编辑
##                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Choice'))
                    self.win_stmts.append(I(i) + 'self.{} = Fl_Choice(T({}), T({}), T({}), T(self._ComboBoxH))'.format(ctrl, x+dx, y+dy, w))

            elif vb_type == 'vb.listbox':
                if ctrl_attrs.get('style', '0') == '0':     # 0:standard, 1:checkbox
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Browser'))
                    list_type = 'FL_MULTI_BROWSER' if bool(int(ctrl_attrs.get('multiselect', 0))) else 'FL_HOLD_BROWSER'
                    self.win_stmts.append(I(i) + 'self.{}.type({}) # fltk:1629'.format(ctrl, list_type))
                else:   # checkbox
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Check_Browser'))

            elif vb_type == 'vb.timer':
                self.win_stmts.append(I(i) + 'pass # self.{} = Fl_Timer()'.format(ctrl))
                self.win_stmts.append(I(i) + '# You should directly call Fl.add_timeout() instead.\n')

            elif vb_type == 'vb.filelistbox':
                pattern = ctrl_attrs.get('pattern', '"*.*"')
                list_type = 'FL_MULTI_BROWSER' if bool(int(ctrl_attrs.get('multiselect', 0))) else 'FL_HOLD_BROWSER'
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_File_Browser'))
                self.win_stmts.append(I(i) + 'self.{}.filter({})'.format(ctrl, pattern))
                self.win_stmts.append(I(i) + 'self.{}.type({})'.format(ctrl, list_type))
                self.win_stmts.append(I(i) + 'self.{}.load(".", FL_ALPHASORT) # fltk:2323'.format(ctrl))

            elif vb_type == 'vb.image':
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Box'))
                self.win_stmts.append(I(i) + '# self.{}_bits = [""] # xpm file contents'.format(ctrl))
                self.win_stmts.append(I(i) + '# self.{0}.image(Fl_Pixmap(self.{0}_bits))'.format(ctrl))

##            elif vb_type in ['vb.hscroll', 'vb.vscroll']:
##            elif vb_type in ['mscomctllib.slider', 'comctllib.slider']:
            elif vb_type.split(".")[1] in ['slider', 'hscroll', 'vscroll']:
##                selectrange = bool(int(ctrl_attrs.get('selectrange', 0)))     # True/False
                range_min = int(ctrl_attrs.get('min', 0))
                range_max = int(ctrl_attrs.get('max', 100))
                step = int(ctrl_attrs.get('smallchange', 1))
                lstep = int(ctrl_attrs.get('largechange', 2))
                value = int(ctrl_attrs.get('value', 0))
                orientation = int(ctrl_attrs.get('orientation', 0))
                if orientation==0 or vb_type.split(".")[1]=='hscroll':  # 水平
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Hor_Value_Slider'))
                else:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Value_Slider'))
                #end if
                self.win_stmts.append(I(i) + 'self.{}.range({}, {})'.format(ctrl, range_min, range_max))
                self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, value))
                self.win_stmts.append(I(i) + 'self.{}.step({})'.format(ctrl, step))

##            elif vb_type in ['mscomctllib.statusbar', 'comctllib.statusbar']:
            elif vb_type.split(".")[1] in ['statusbar', 'ucstatusbar']:
                simpletext = ctrl_attrs.get('simpletext', '')
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Box'))
                self.win_stmts.append(I(i) + 'self.{}.box(FL_THIN_DOWN_BOX)'.format(ctrl))
                self.win_stmts.append(I(i) + 'self.{}.align(FL_ALIGN_LEFT + FL_ALIGN_INSIDE)'.format(ctrl))
                if simpletext:
                    self.win_stmts.append(I(i) + 'self.{}.label({})'.format(ctrl, simpletext))

##            elif vb_type in ['mscomctllib.progressbar', 'comctllib.progressbar']:
            elif vb_type.split(".")[1] in ['progressbar', 'ucprogressbar']:
                minimum = int(ctrl_attrs.get('min', 0))
                maximum = int(ctrl_attrs.get('max', 100))
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Progress'))
                self.win_stmts.append(I(i) + 'self.{}.minimum({})'.format(ctrl, minimum))
                self.win_stmts.append(I(i) + 'self.{}.maximum({})'.format(ctrl, maximum))
                appearance = bool(int(ctrl_attrs.get('appearance', 0)))     # 0:Flat, 1:3D
                if not appearance:
                    self.win_stmts.append(I(i) + 'self.{}.box(FL_FLAT_BOX)'.format(ctrl) + ' # fltk:323')

##            elif vb_type in ['mscomctllib.treeview', 'comctllib.treeview']:
            elif vb_type.split(".")[1] == 'treeview':
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Tree'))

            elif vb_type.split(".")[1] in ['spinbox', 'spinner']:
                minimum = int(ctrl_attrs.get('min', 0))
                maximum = int(ctrl_attrs.get('max', 100))
                value = int(ctrl_attrs.get('value', 0))
                step = int(ctrl_attrs.get('increment', 1))
                if step > 2:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Counter'))
                    self.win_stmts.append(I(i) + 'self.{}.range({}, {})'.format(ctrl, minimum, maximum))
                    self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, value))
                    self.win_stmts.append(I(i) + 'self.{}.lstep({})'.format(ctrl, step))
                    self.win_stmts.append(I(i) + 'self.{}.step({})'.format(ctrl, 1))
                else:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Spinner'))
                    self.win_stmts.append(I(i) + 'self.{}.minimum({})'.format(ctrl, minimum))
                    self.win_stmts.append(I(i) + 'self.{}.maximum({})'.format(ctrl, maximum))
                    self.win_stmts.append(I(i) + 'self.{}.value({})'.format(ctrl, value))
                    self.win_stmts.append(I(i) + 'self.{}.step({})'.format(ctrl, step))
                #end if

            # vb_type = vb.textbox, tag_lower in ['fl_text_editor', 'fl_text_display']
            # 也可用上面方式
            elif vb_type.split(".")[1] == 'richtextbox':
                locked = bool(int(ctrl_attrs.get('locked', 0)))     # True/False
                if locked:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Text_Display'))
                else:
                    self.win_stmts.append(I(i) + widget_stmt.format('Fl_Text_Editor'))
                self.win_stmts.append(I(i) + 'self.{}_buffer = Fl_Text_Buffer()'.format(ctrl))
                self.win_stmts.append(I(i) + 'self.{0}.buffer(self.{0}_buffer)'.format(ctrl))

            elif 'flexgrid' in vb_type.split(".")[1] or 'listview' in vb_type.split(".")[1]:
                self.win_stmts.append(I(i) + widget_stmt.format('FltkGrid'))

##                rows = int(ctrl_attrs.get('rows', 2))
##                cols = int(ctrl_attrs.get('cols', 2))
##                fixedrows = int(ctrl_attrs.get('fixedrows', 1))
##                fixedcols = int(ctrl_attrs.get('fixedcols', 1))
##                cls_name = 'Table{}'.format(ctrl.title())
##                cls_table = '{}(T({}), T({}), T({}), T({}), {})'.format(cls_name, x+dx, y+dy, w, h, label)
##                self.win_stmts.append(I(i) + '# bulid table widget')
##                self.win_stmts.append(I(i) + 'self.{} = {}'.format(ctrl, cls_table))
##                self.win_stmts.append(I(i) + 'if self.{}:'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.selection_color(FL_YELLOW)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.col_header_height(24)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.row_header(True)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.col_header(True)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.row_resize(True)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.col_resize(True)'.format(ctrl))
##                self.win_stmts.append(I(i+1) + 'self.{}.rows({})'.format(ctrl, rows))
##                self.win_stmts.append(I(i+1) + 'self.{}.cols({})'.format(ctrl, cols))

##                self.tbl_stmts.append(tbl_stmt.format(cls_name))

            else:
                self.win_stmts.append(I(i) + widget_stmt.format('Fl_Box'))
                self.win_stmts.append(I(i) + 'self.{}.align(FL_ALIGN_CENTER + FL_ALIGN_INSIDE)'.format(ctrl))
                self.win_stmts.append(I(i) + 'self.{0}.box(FL_BORDER_BOX)'.format(ctrl))
                self.win_stmts.append(I(i) + 'self.{0}.label("{0}")'.format(ctrl))
                self.win_stmts.append(I(i) + 'pass # {} = {}'.format(ctrl, vb_type))
            #end if -----> vb_type

##            self.win_stmts.append(I(i) + 'self.{}.color(self._NewColor)'.format(ctrl))

            if tooltiptext:
                self.win_stmts.append(I(i) + 'self.{}.tooltip({})'.format(ctrl, tooltiptext))

##            self.win_stmts.append("")
##            print(ctrl, x+dx, y+dy, w, h, label)
        #end for -----> ctrls


if __name__ == '__main__':
    pycode = PyFltkWin(r'test_form\Form2.frm')

    print(pycode.hdr_stmt)
    print('\n'.join(pycode.win_stmts))
    if pycode.kls_stmts:
        print('\n'.join(pycode.kls_stmts))
    print(pycode.app_stmt)



