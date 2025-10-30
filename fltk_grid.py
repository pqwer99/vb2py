# -*- coding: utf8 -*-

from fltk import *

class FltkGrid(Fl_Table_Row):
    def __init__(self, x, y, w, h, l=None):
        Fl_Table_Row.__init__(self, x, y, w, h, l)
        self.selection_color(FL_YELLOW)
        self.col_header(1)
        self.col_resize(1)
        self.col_header_height(24)
        self.row_header(1)
        self.row_resize(1)
##        self.row_header_width(80)
        self.header_list=["A","B","C"]
        self.cols(3)
        self.rows(2)
        self.end()

    def draw_cell(self, context, r=0, c=0, x=0, y=0, w=0, h=0):
        fl_push_clip(x, y, w, h)

        if context==self.CONTEXT_STARTPAGE:
            pass
        elif context == self.CONTEXT_ENDPAGE:
            pass
        elif context == self.CONTEXT_RC_RESIZE:
            pass
        elif context == self.CONTEXT_COL_HEADER:
            fl_draw_box(FL_THIN_UP_BOX, x, y, w, h, self.color())
            fl_color(FL_BLACK)
            try:
                fl_draw(self.header_list[c], x, y, w, h, FL_ALIGN_CENTER)
            except:
                pass
        elif context==self.CONTEXT_ROW_HEADER:
            fl_draw_box(FL_THIN_UP_BOX, x, y, w, h, self.color())
            fl_color(FL_BLACK)
            try:
                fl_draw(str(r+1), x, y, w, h, FL_ALIGN_CENTER)
            except:
                pass
        elif context==self.CONTEXT_CELL:
            # BG color
            if self.row_selected(r):
                fl_color(self.selection_color())
            else:
                fl_color(FL_WHITE)
            fl_rectf(x, y, w, h)

            # TEXT
            fl_color(FL_BLACK)
            try:
                fl_draw(self.Buffer[r][c], x, y, w, h, self.align_list[c])
            except:
                pass

            # BORDER
            fl_color(FL_LIGHT2)
            fl_rect(x, y, w, h)
        elif context==self.CONTEXT_TABLE:
            pass
        else:
            pass
        #end if

        fl_pop_clip()
        return None

    def Cell(self, r, c, txt=None):
        try:
            if txt is None:
                return self.Buffer[r][c]
            else:
                self.Buffer[r][c]=txt
                self.redraw()
        except:
            pass

    def Row(self, r, items=None):
        try:
            if items is None:
                return self.Buffer[r]
            else:
                self.Buffer[r] = items
                self.redraw()
        except:
            pass

    @staticmethod
    def getwidth(w):
        try:
            ret = int(w)
        except:
            ret = 80
        return ret

    def Header(self, titles):
        self.header_list = []
        self.align_list = []
        self.width_list = []

        colnames = titles.split(",")
        for colname in colnames:
            if '@' in colname:
                title, style = colname.split("@")
                if style[0]=='>':
                    align = FL_ALIGN_RIGHT
                    width = self.getwidth(style[1:])
                elif style[0]=='<':
                    align = FL_ALIGN_LEFT
                    width = self.getwidth(style[1:])
                else:
                    align = FL_ALIGN_CENTER
                    width = self.getwidth(style)
            else:
                title = colname
                align = FL_ALIGN_CENTER
                width = 80

            self.header_list.append(title.strip())
            self.align_list.append(align)
            self.width_list.append(width)

        num = len(colnames)
        self.cols(num)
        for i in range(num):
            self.col_width(i, self.width_list[i])

    def Dump(self, data):
        self.Buffer = data
        self.rows(len(data))

if __name__ == '__main__':
    def cb_grid1(ptr, table):
        print("callback: row=%d col=%d, context=%d, event_button=%d, event=%d, clicks=%d" % (
              table.callback_row(), table.callback_col(), table.callback_context(),
              Fl.event_button(), Fl.event(), Fl.event_clicks()))

    form7 = Fl_Window(600, 380, "Form7")
    form7.color(FL_LIGHT2)
    command1 = Fl_Button(40, 15, 120, 30, "Command1")
    command2 = Fl_Button(220, 15, 120, 30, "Command2")
    grid1 = FltkGrid(10, 60, 580, 300, None)

    grid1.row_header(0)
    grid1.Header("中文@>160 , BBBB@60, cc@<, 国中")
    data = [["1","2","3","汉字"],["5","6","7","8"],['11','22'],['asd','zxczxc']]

    grid1.Dump(data)
    grid1.Row(1, ["100","200","300","汉字"])
    grid1.Buffer[2] = ["100","200","300","汉字"]

##    grid1.when(FL_WHEN_CHANGED|FL_WHEN_RELEASE_ALWAYS)    # handle table events on release
    grid1.callback(cb_grid1, grid1)

    form7.end()
    form7.show()

    Fl.mt_run(form7)