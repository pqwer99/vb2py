# -*- coding: utf-8 -*-

# fltk 可视部件
fltk_widgets = {
'fl_box': 'Fl_Box',
'fl_button': 'Fl_Button',
    'fl_light_button': 'Fl_Light_Button',
        'fl_check_button': 'Fl_Check_Button',
        'fl_radio_light_button': 'Fl_Radio_Light_Button',
        'fl_round_button': 'Fl_Round_Button',
            'fl_radio_round_button': 'Fl_Radio_Round_Button',
    'fl_radio_button': 'Fl_Radio_Button',
    'fl_repeat_button': 'Fl_Repeat_Button',
    'fl_return_button': 'Fl_Return_Button',
    'fl_toggle_button': 'Fl_Toggle_Button',
'fl_chart': 'Fl_Chart',
'fl_clock_output': 'Fl_Clock_Output',
    'fl_clock': 'Fl_Clock',
        'fl_round_clock': 'Fl_Round_Clock',
'fl_group': 'Fl_Group',
    #Fl_Browser_
        'fl_browser': 'Fl_Browser',
            'fl_file_browser': 'Fl_File_Browser',
            'fl_hold_browser': 'Fl_Hold_Browser',
            'fl_multi_browser': 'Fl_Multi_Browser',
            'fl_select_browser': 'Fl_Select_Browser',
        'fl_check_browser': 'Fl_Check_Browser',
    'fl_color_chooser': 'Fl_Color_Chooser',
    'fl_help_view': 'Fl_Help_View',
    'fl_input_choice': 'Fl_Input_Choice',
    'fl_pack': 'Fl_Pack',
    'fl_scroll': 'Fl_Scroll',
    'fl_spinner': 'Fl_Spinner',
    #'fl_table': 'Fl_Table',
        #'fl_table_row': 'Fl_Table_Row',
    'fl_tabs': 'Fl_Tabs',
    'fl_text_display': 'Fl_Text_Display',
        'fl_text_editor': 'Fl_Text_Editor',
    'fl_tile': 'Fl_Tile',
#Fl_Input_
    'fl_input': 'Fl_Input',
        'fl_file_input': 'Fl_File_Input',
        'fl_float_input': 'Fl_Float_Input',
        'fl_int_input': 'Fl_Int_Input',
        'fl_multiline_input': 'Fl_Multiline_Input',
        'fl_output': 'Fl_Output',
            'fl_multiline_output': 'Fl_Multiline_Output',
        'fl_secret_input': 'Fl_Secret_Input',
#Fl_Menu_
    'fl_choice': 'Fl_Choice',
    'fl_menu_bar': 'Fl_Menu_Bar',
    'fl_menu_button': 'Fl_Menu_Button',
'fl_positioner': 'Fl_Positioner',
'fl_progress': 'Fl_Progress',
'fl_valuator': 'Fl_Valuator',
    'fl_adjuster': 'Fl_Adjuster',
    'fl_counter': 'Fl_Counter',
        'fl_simple_counter': 'Fl_Simple_Counter',
    'fl_dial': 'Fl_Dial',
        'fl_fill_dial': 'Fl_Fill_Dial',
        'fl_line_dial': 'Fl_Line_Dial',
    'fl_roller': 'Fl_Roller',
        'fl_slider': 'Fl_Slider',
        'fl_fill_slider': 'Fl_Fill_Slider',
        'fl_hor_fill_slider': 'Fl_Hor_Fill_Slider',
        'fl_hor_nice_slider': 'Fl_Hor_Nice_Slider',
        'fl_hor_slider': 'Fl_Hor_Slider',
        'fl_nice_slider': 'Fl_Nice_Slider',
        'fl_scrollbar': 'Fl_Scrollbar',
        'fl_value_slider': 'Fl_Value_Slider',
            'fl_hor_value_slider': 'Fl_Hor_Value_Slider',
    'fl_value_input': 'Fl_Value_Input',
    'fl_value_output': 'Fl_Value_Output',
'fl_tree': 'Fl_Tree'
}


hdr_stmt = """# -*- coding: utf8 -*-

from ctypes import windll

from fltk import *

from fltk_ext import Print2Fltk, Cmd4Fltk, FltkFont
from fltk_grid import FltkGrid

def __getdpi():
    GetDC = windll.user32.GetDC
    GetDeviceCaps = windll.gdi32.GetDeviceCaps
    LOGPIXELSX = 88        #  Logical pixels/inch in X
    return GetDeviceCaps(GetDC(None), LOGPIXELSX) / 96.0     # 96为设备绘制为100%大小时dpi
DPI = __getdpi()

def T(twips, dpi=DPI):
    return int(twips / 15 * dpi)

"""

app_stmt = """
class {1}Proc({1}):
    def __init__(self):
        {1}.__init__(self)
        self.{0}.color(FL_LIGHT2)   # 设置当前窗体颜色
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(0xf0, 0xf0, 0xf0))     # 更改部件默认背景色
        # Fl.set_color(FL_BACKGROUND_COLOR, fl_rgb_color(*Fl.get_color(FL_LIGHT2)))
        self.resize()
        #
        # 修改、设置控件属性
        #

    def resize(self):
        # 调整窗口、控件位置及大小
        pass

    def start(self, mt=False):
        self.{0}.callback(self.on_close)
        self.{0}.end()
        self.{0}.show()
        if mt:
            #Fl.mt_run(self.{0})
            import time
            while Fl.check(): time.sleep(0.1)  #Fl.wait(0.05)
        else:
            Fl.run()
        #end if

    def on_close(self, this):
        # Fl.event()=FL_CLOSE，窗口关闭时执行以下代码

        # this.hide()
        Fl.fltk_exit()

if __name__ == '__main__':
    app = {1}Proc()
    app.start()
"""

kls_stmt = """
class {0}({1}):
    def __init__(self, x, y, w, h, l):
        super({0}, self).__init__(x, y, w, h, l)
"""
