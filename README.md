## 简介
利用VB6进行可视化界面设计，布置控件、设置控件属性，然后将保存的窗体文件转换成Python的pyfltk界面文件，代码包括界面类和过程类，最后只需要在过程类中编写对应的回调函数和相应的功能代码即可。
pyfltk是一个gui库，是基于开源的C++编写的fltk的python封装。
fltk主页： https://www.fltk.org/
pyfltk主页： https://pyfltk.sourceforge.io/
pyfltk可应付一般GUI的需求，Python自带的标准库TKinter写起来手感不好，而其他第三方工具和框架比如wxPython/PyQt/PySide等太大、太复杂。

## 源文件
* vbfltk.py，主界面，将VB的窗体文件转换成Python文件（本身就是自己转换过来的）。
* fltk_vbform.py，核心代码，对VB窗体文件解析，生成pyfltk窗体和部件代码。
* fltk_pytmpl.py，部分vb转pyfltk代码的模板。
* fltk_ext.py，一些pyfltk的扩展功能。
* dialogbox.py，comdlg32的简单封装。

## 窗体和菜单
1. VB的Form会转换成界面类和过程类，如名称为FormTest，则会生成一个界面类class FormTest(object)，包含主窗体self.formtest和其他控件self.ctrlxxx，另一个是过程类class FormTestProc(FormTest)，以后的编码主要是在这个类中进行。若需要自定义类名，可在tag属性中赋值一个符合python命名规则的字符串，如WinMain，则类名为WinMain和WinMainProc。(python建议命名规则：变量名小写，类名驼峰，过程名下划线。)

2. 窗体菜单只需在菜单编辑器中定义一项，菜单设置和调用需要在过程类中编码。（解析窗体文件时，窗体属性clienttop>600，说明有菜单，菜单高度300twips）


## 控件列表
VB控件转换成pyfltk部件，一般格式是：ctrlname = Fl_Xxxx(left, top, width, height, caption)。
例如: self.command1 = Fl_Button(left, top, width, height, '确定')
* VB有，pyfltk对应很多，(1) 转换成默认部件。(2) 根据VB相应属性设置转换。(3) 根据tag属性值转换。
* VB有，pyfltk无，则转换成 Fl_Box。
* VB无，pyfltk有，在设计时一般用PictureBox代替，并在tag属性里设置成pyfltk的部件名。pyfltk的可视部件名称在fltk_pytmpl.py中。


0. PictureBox
	(1) 无tag, =Fl_Box(), 不如用Image。
	(2) tag=pyfltk的部件名(不区分大小写)，=Fl_XXXX同名控件。
	(3) tag=自定义类名(fltk的部件名), 例如MyBtn(Fl_Button), 则会创建继承类：
		class MyBtn(Fl_Button):
			def __init__(self, x, y, w, h, l):
				super(MyBtn, self).__init__(x, y, w, h, l)
        注意大小写和两个类名正确命名。

1. Label    
    =Fl_Box()。VB可用属性alignment，borderstyle。
2. TextBox    
    Pyfltk的文本框有多种，可根据VB的TextBox的属性值，生成相应的部件。
    (1) tag in ['fl_text_editor', 'fl_text_display'， 'fl_file_input', 'fl_float_input', 'fl_int_input', 'fl_spinner', 'fl_value_input', 'fl_secret_input']
    (2) passwordchar='*'， =Fl_Secret_Input()
    (3) multiline=True and locked=True, =Fl_Multiline_Output()
    (4) multiline=True and locked=False, =Fl_Multiline_Input()
    (5) multiline=False and locked=True, =Fl_Output()
    (6) multiline=False and locked=False, =Fl_Input()
3. Frame    
    =Fl_Group()，做为其他控件的容器。
4. CommandButton
	(1) =Fl_Button()
	(2) default=True, =Fl_Return_Button()
	(3) tag in ['fl_light_button', 'fl_return_button', 'fl_toggle_button', 'fl_menu_button'] 
5. CheckBox    
    =Fl_Check_Button()
6. OptionButton    
    =Fl_Radio_Round_Button()
7. ComboBox    
	(1) style=0(默认，dropdown combo 可编辑)，=Fl_Input_Choice()。
	(2) style!=0(dropdown list 不能编辑)，=Fl_Choice()
8. ListBox    
	(1) style=0(默认，standard)，=Fl_Hold_Browser()。multiselect!=0，=Fl_Multi_Browser()。
	(2) style=1(checkbox)，=Fl_Check_Browser()
9. Timer    
    没有使用=Fl_Timer()， 在程序中用Fl.add_timeout()替代。
10. FileListBox
	=Fl_File_Browser()。可用属性multiselect。
11. Image
    =Fl_Box()。
12. HScroll, VScroll
	参照13。
    
	>以下的控件需要在VB的'控件工具箱'中按右键添加'部件'，选择“Microsoft Windows Common Controls”(mscomctl.ocx 或 comctl32.ocx) 

13. Slider
	可用属性mix, max, smallchange, largechange, value
	(1) =Fl_Hor_Value_Slider()
	(2) =Fl_Value_Slider())
14. Statusbar    
    =Fl_Box(x,y,w,h,simpletext)。
15. ProgressBar    
    =Fl_Progress()。可用属性mix, max, appearance
16. TreeView    
    =Fl_Tree()。
17. SpinBox, Spinner    
	可用属性mix, max, increment, value
    (1) =Fl_Spinner()
	(2) =Fl_Counter(),  increment>2时

	>以下的控件需要选择“Microsoft Tabbed Dialog Controls”(tabctl32.ocx)
	
18. SSTab    
    =Fl_Tab()。
    这个控件作为容器可直接放入其他控件，比TabStrip好用，内部控件也全部转换成pyfltk部件。
    
	>以下的控件需要选择“Microsoft FlexGrid Controls”(msflxgrd.ocx)
	
19. FlexGrid 或 ListView
	可用属性rows, cols, fixedrows, fixedcols。类似于Fl_Table_Row()，但不能直接使用。
	举例说明：控件名MSFlexGrid1，则会生成类class TableMSFlexGrid1(Fl_Table_Row)，然后赋值给控件self.msflexgrid1 =TableMSFlexGrid1()。
	对表格操作代码在类TableMSFlexGrid1中。
	！！！ 现已封装成类FltkGrid(需要文件fltk_grid.py)，grid1 = FltkGrid(x, y, w, h, l)

	>以下的控件需要选择“Microsoft Rich TextBox Controls”(richtx32.ocx)
	
20. RichTextBox 
	locked=0， =Fl_Text_Editor()。
	locked=1， =Fl_Text_Display()。
    也可用TextBox替代，tag in ['fl_text_editor', 'fl_text_display']

## 其他说明
1. 窗体的ScaleMode只能使用默认值(vbTwips)，不要手动修改.frm文件。
2. 在VB中不要使用控件数组。
3. VB中所有控件的ToolTipText都可使用。

## 版本历史
*  v1.0 第一个版本
    TODO：图像部件的图片可设置大小。

  