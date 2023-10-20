VERSION 5.00
Object = "{BDC217C8-ED16-11CD-956C-0000C04E4C0A}#1.1#0"; "tabctl32.ocx"
Begin VB.Form FormFltk 
   Caption         =   "VB.Form -> pyfltk"
   ClientHeight    =   6612
   ClientLeft      =   120
   ClientTop       =   468
   ClientWidth     =   9360
   LinkTopic       =   "Form5"
   ScaleHeight     =   6612
   ScaleWidth      =   9360
   StartUpPosition =   3  '窗口缺省
   Begin TabDlg.SSTab SSTab1 
      Height          =   5775
      Left            =   45
      TabIndex        =   2
      Top             =   795
      Width           =   9270
      _ExtentX        =   16341
      _ExtentY        =   10181
      _Version        =   393216
      Style           =   1
      Tab             =   2
      TabHeight       =   582
      TabCaption(0)   =   " Frm文件 "
      TabPicture(0)   =   "FormFltk.frx":0000
      Tab(0).ControlEnabled=   0   'False
      Tab(0).Control(0)=   "Option2"
      Tab(0).Control(0).Enabled=   0   'False
      Tab(0).Control(1)=   "Option1"
      Tab(0).Control(1).Enabled=   0   'False
      Tab(0).Control(2)=   "Command2"
      Tab(0).Control(2).Enabled=   0   'False
      Tab(0).Control(3)=   "Text2"
      Tab(0).Control(3).Enabled=   0   'False
      Tab(0).ControlCount=   4
      TabCaption(1)   =   " 过程数据 "
      TabPicture(1)   =   "FormFltk.frx":001C
      Tab(1).ControlEnabled=   0   'False
      Tab(1).Control(0)=   "Text3"
      Tab(1).Control(0).Enabled=   0   'False
      Tab(1).ControlCount=   1
      TabCaption(2)   =   " 程序代码 "
      TabPicture(2)   =   "FormFltk.frx":0038
      Tab(2).ControlEnabled=   -1  'True
      Tab(2).Control(0)=   "Text4"
      Tab(2).Control(0).Enabled=   0   'False
      Tab(2).Control(1)=   "Command3"
      Tab(2).Control(1).Enabled=   0   'False
      Tab(2).Control(2)=   "Command4"
      Tab(2).Control(2).Enabled=   0   'False
      Tab(2).ControlCount=   3
      Begin VB.CommandButton Command4 
         Caption         =   "保存到文件"
         Height          =   360
         Left            =   4815
         TabIndex        =   10
         Top             =   5145
         Width           =   1800
      End
      Begin VB.CommandButton Command3 
         Caption         =   "复制到剪贴板"
         Height          =   360
         Left            =   2190
         TabIndex        =   9
         Top             =   5145
         Width           =   1800
      End
      Begin VB.OptionButton Option2 
         Caption         =   "仅界面类"
         Height          =   360
         Left            =   -69180
         TabIndex        =   8
         Top             =   5175
         Width           =   1140
      End
      Begin VB.OptionButton Option1 
         Caption         =   "全部源码"
         Height          =   360
         Left            =   -70545
         TabIndex        =   7
         Top             =   5175
         Value           =   -1  'True
         Width           =   1140
      End
      Begin VB.CommandButton Command2 
         Caption         =   "生成代码"
         Height          =   360
         Left            =   -72810
         TabIndex        =   6
         Top             =   5145
         Width           =   1800
      End
      Begin VB.TextBox Text4 
         Height          =   4605
         Left            =   48
         TabIndex        =   5
         Tag             =   "Fl_Text_Display"
         Top             =   375
         Width           =   9180
      End
      Begin VB.TextBox Text3 
         Height          =   5385
         Left            =   -74952
         TabIndex        =   4
         Tag             =   "Fl_Text_Display"
         Top             =   375
         Width           =   9180
      End
      Begin VB.TextBox Text2 
         Height          =   4605
         Left            =   -74952
         TabIndex        =   3
         Tag             =   "Fl_Text_Display"
         Top             =   375
         Width           =   9180
      End
   End
   Begin VB.CommandButton Command1 
      Caption         =   "选择文件"
      Height          =   360
      Left            =   315
      TabIndex        =   1
      Top             =   210
      Width           =   1800
   End
   Begin VB.TextBox Text1 
      Height          =   360
      Left            =   2400
      Locked          =   -1  'True
      TabIndex        =   0
      Text            =   "Text1"
      Top             =   225
      Width           =   6600
   End
End
Attribute VB_Name = "FormFltk"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

