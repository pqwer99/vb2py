VERSION 5.00
Object = "{BDC217C8-ED16-11CD-956C-0000C04E4C0A}#1.1#0"; "tabctl32.ocx"
Begin VB.Form FormCtypes 
   Caption         =   "api -> ctypes"
   ClientHeight    =   7815
   ClientLeft      =   120
   ClientTop       =   465
   ClientWidth     =   12555
   LinkTopic       =   "Form8"
   ScaleHeight     =   7815
   ScaleWidth      =   12555
   StartUpPosition =   3  '窗口缺省
   Begin TabDlg.SSTab SSTab1 
      Height          =   7740
      Left            =   30
      TabIndex        =   0
      Top             =   30
      Width           =   12480
      _ExtentX        =   22013
      _ExtentY        =   13653
      _Version        =   393216
      Style           =   1
      Tabs            =   2
      TabHeight       =   582
      TabCaption(0)   =   " VB源码 或 C结构体 "
      TabPicture(0)   =   "FormCtypes.frx":0000
      Tab(0).ControlEnabled=   -1  'True
      Tab(0).Control(0)=   "Command1"
      Tab(0).Control(0).Enabled=   0   'False
      Tab(0).Control(1)=   "Command2"
      Tab(0).Control(1).Enabled=   0   'False
      Tab(0).Control(2)=   "Text1"
      Tab(0).Control(2).Enabled=   0   'False
      Tab(0).Control(3)=   "Command3"
      Tab(0).Control(3).Enabled=   0   'False
      Tab(0).ControlCount=   4
      TabCaption(1)   =   " Python代码 "
      TabPicture(1)   =   "FormCtypes.frx":001C
      Tab(1).ControlEnabled=   0   'False
      Tab(1).Control(0)=   "Text2"
      Tab(1).Control(0).Enabled=   0   'False
      Tab(1).ControlCount=   1
      Begin VB.CommandButton Command3 
         Caption         =   "转换C结构体"
         Height          =   330
         Left            =   4830
         TabIndex        =   5
         Top             =   540
         Width           =   1600
      End
      Begin VB.TextBox Text2 
         Height          =   7335
         Left            =   -74940
         TabIndex        =   4
         Tag             =   "fl_text_editor"
         Top             =   360
         Width           =   12375
      End
      Begin VB.TextBox Text1 
         Height          =   6660
         Left            =   60
         TabIndex        =   3
         Tag             =   "fl_text_editor"
         Top             =   1035
         Width           =   12375
      End
      Begin VB.CommandButton Command2 
         Caption         =   "转换VB源玛"
         Height          =   330
         Left            =   2670
         TabIndex        =   2
         Top             =   540
         Width           =   1600
      End
      Begin VB.CommandButton Command1 
         Caption         =   "打开VB文件"
         Height          =   330
         Left            =   450
         TabIndex        =   1
         Top             =   540
         Width           =   1600
      End
   End
End
Attribute VB_Name = "FormCtypes"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

