# -*- coding: gbk -*-

from __future__ import print_function
##from __future__ import unicode_literals

from ctypes import *
from ctypes.wintypes import *

import os

__all__ = ['FileDialog', 'browsefolder', 'msgbox']

MAX_PATH = 260

LPCTSTR = LPCWSTR        #c_wchar_p
LPTSTR = LPWSTR       #c_wchar_p

#------------------------------ FileDialog ------------------------------

FNERR_FILENAMECODES    = 0x3000
FNERR_SUBCLASSFAILURE  = 0x3001
FNERR_INVALIDFILENAME  = 0x3002
FNERR_BUFFERTOOSMALL   = 0x3003

OFN_EXPLORER = 0x80000
OFN_ALLOWMULTISELECT = 512
OFN_PATHMUSTEXIST = 0x800
OFN_FILEMUSTEXIST = 0x1000
OFN_OVERWRITEPROMPT = 2
OFN_NOCHANGEDIR = 8


##UINT_PTR = DWORD
###TODO
### UINT_PTR CALLBACK OFNHookProc(
### HWND hdlg,      // handle to child dialog box
### UINT uiMsg,     // message identifier
### WPARAM wParam,  // message parameter
### LPARAM lParam);   // message parameter
##OFNHookProc = WINFUNCTYPE(UINT_PTR, HWND, UINT, WPARAM, LPARAM)
##LPOFNHOOKPROC = OFNHookProc
LPOFNHOOKPROC = LPVOID #TODO

class OPENFILENAME(Structure):
    _fields_ = [("lStructSize", DWORD),
                ("hwndOwner", HWND),
                ("hInstance", HINSTANCE),
                ("lpstrFilter", POINTER(c_wchar)), #LPCTSTR),
                ("lpstrCustomFilter", LPTSTR),
                ("nMaxCustFilter", DWORD),
                ("nFilterIndex", DWORD),
                ("lpstrFile", POINTER(c_wchar)),    #LPTSTR),   #LPCTSTR�޷�����NULL
                ("nMaxFile", DWORD),
                ("lpstrFileTitle", LPTSTR),
                ("nMaxFileTitle", DWORD),
                ("lpstrInitialDir", LPCTSTR),
                ("lpstrTitle", LPCTSTR),
                ("Flags", DWORD),
                ("nFileOffset", WORD),
                ("nFileExtension", WORD),
                ("lpstrDefExt", LPCTSTR),
                ("lCustData", LPARAM),
                ("lpfnHook", LPOFNHOOKPROC),
                ("lpTemplateName", LPCTSTR),
                ("pvReserved", LPVOID),
                ("dwReserved", DWORD),
                ("FlagsEx", DWORD)]


GetActiveWindow = windll.user32.GetActiveWindow #(VOID);
CommDlgExtendedError = windll.comdlg32.CommDlgExtendedError #(VOID);
##GetOpenFileName = WINFUNCTYPE(c_bool, POINTER(OPENFILENAME))(('GetOpenFileNameW', windll.comdlg32))
GetOpenFileName = windll.comdlg32.GetOpenFileNameW #(LPOPENFILENAME lpofn)
GetSaveFileName = windll.comdlg32.GetSaveFileNameW #(LPOPENFILENAME lpofn)

class FileDialog(OPENFILENAME):
    def __init__(self):
        self.ExtendedError = 0

        self.lStructSize = sizeof(OPENFILENAME)
        self.hwndOwner = GetActiveWindow()
        self.Flags = OFN_EXPLORER #| OFN_NOCHANGEDIR
        self.nMaxFile = MAX_PATH
        self.lpstrDefExt = '\0'

##    @property
##    def filterstr(self):
##        return wstring_at(self.lpstrFilter, self.nMaxFile).split('\0\0', 1)[0]
##    @filterstr.setter
##    def filterstr(self, setfilter):
##        self.lpstrFilter = create_unicode_buffer(setfilter.replace('|', '\0') + '\0\0')

    def showopen(self, Title='���ļ�', File='', InitDir='',
                       Filter="�����ļ� (*.*)|*.*", FilterIndex=1,
                       MultiSel=False, MaxFile=-1):

        if MultiSel:    # ��ѡ
            self.Flags = self.Flags | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_ALLOWMULTISELECT
            self.nMaxFile = MAX_PATH*65535 if MaxFile<MAX_PATH else MaxFile
        else:
            self.Flags = self.Flags | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
            self.nMaxFile = MAX_PATH
        #end if

        self.lpstrTitle = Title
##        self.lpstrFile = create_unicode_buffer(self.nMaxFile)
##        self.lpstrFile.raw = File
        self.lpstrFile = create_unicode_buffer(File, self.nMaxFile)
        self.lpstrInitialDir = InitDir if InitDir else os.getcwd()
        self.lpstrFilter = create_unicode_buffer(Filter.replace('|', '\0') + '\0\0')
        self.nFilterIndex = FilterIndex

        ret = GetOpenFileName(byref(self))
        if ret==0:  # ȡ�������
            __filename = []
        else:
            # lpstrFile��˫NULL��β
            # ����Ƕ�ѡ����ʽΪD:\PATH(NULL)FILE1(NULL)FILE2(NULL)FILE3...(NULL)(NULL)

            lpstrFile_buffer = wstring_at(self.lpstrFile, self.nMaxFile)
##            lpstrFile_buffer = wstring_at(self.__lpstrFile, self.nMaxFile).strip('\0')

            lpstrFile_buffer = lpstrFile_buffer.split('\0\0', 1)[0]  # ���Ի�������˫NULL��������ַ�
            if '\0' in lpstrFile_buffer:
                lpstrFile_buffer = lpstrFile_buffer.split('\0')
                fpath = lpstrFile_buffer[0]
                __filename = [fpath + '\\' + fname for fname in lpstrFile_buffer[1:]]
            else:
                __filename = [lpstrFile_buffer]
            #endif
        #end if
        self.ExtendedError = CommDlgExtendedError()
        return __filename

    def showsave(self, Title='�����ļ�', File='', InitDir='',
                       Filter="�����ļ� (*.*)|*.*", FilterIndex=1):

        self.Flags = self.Flags | OFN_OVERWRITEPROMPT
        self.nMaxFile = MAX_PATH

        self.lpstrTitle = Title
        self.lpstrFile = create_unicode_buffer(File + '\0\0', self.nMaxFile)
        self.lpstrInitialDir = InitDir if InitDir else os.getcwd()
        self.lpstrFilter = create_unicode_buffer(Filter.replace('|', '\0') + '\0\0')
##        self.lpstrDefExt = DefExt
        self.nFilterIndex = FilterIndex

        ret = GetSaveFileName(byref(self))
        if ret == 0:
            __filename = ''
        else:
            __filename =  wstring_at(self.lpstrFile)  #lpstrFile_buffer
        #end if
        self.ExtendedError = CommDlgExtendedError()
        return __filename

#------------------------------ BrowseFolder ------------------------------

BIF_RETURNONLYFSDIRS = 0x1
BIF_STATUSTEXT = 0x4
BIF_EDITBOX = 0x10
BIF_VALIDATE = 0x20
BIF_NEWDIALOGSTYLE = 0x40
BIF_USENEWUI = BIF_EDITBOX + BIF_NEWDIALOGSTYLE
BIF_NONEWFOLDERBUTTON = 0x200

class BROWSEINFO(Structure):
    _fields_ = [("hwndOwner", HWND),
                ("pidlRoot", DWORD),
                ("pszDisplayName", LPTSTR),
                ("lpszTitle", LPCTSTR),
                ("ulFlags", DWORD),
                ("lpfn", LPVOID),
                ("lParam", LPARAM),
                ("iImage", DWORD)]

SHBrowseForFolder = windll.shell32.SHBrowseForFolderW #(LPBROWSEINFO lpbi)
SHGetPathFromIDList = windll.shell32.SHGetPathFromIDListW #(LPCITEMIDLIST pidl, LPTSTR pszPath);
CoTaskMemFree = windll.ole32.CoTaskMemFree #(void *pv)  //Pointer to memory block to be freed

def browsefolder(title=""):
    bi = BROWSEINFO()
    bi.hwndOwner = GetActiveWindow()
    bi.pszDisplayName = '\0' * MAX_PATH
    bi.lpszTitle = title
    bi.ulFlags = BIF_RETURNONLYFSDIRS + BIF_USENEWUI + BIF_VALIDATE + BIF_STATUSTEXT # + BIF_NONEWFOLDERBUTTON

    pidl = SHBrowseForFolder(byref(bi))
    if pidl:
        lpBuffer = create_unicode_buffer(MAX_PATH)# c_wchar_p('\0' * MAX_PATH)
        SHGetPathFromIDList(pidl, lpBuffer)
        CoTaskMemFree(pidl)     #Clean it
        return lpBuffer.value

#------------------------------ Msgbox ------------------------------

MB_ICONQUESTION = 0x20
MB_YESNO = 0x4
MB_ICONWARNING = 0x30
MB_OKCANCEL = 0x1
MB_SYSTEMMODAL = 0x1000

MessageBox = WINFUNCTYPE(UINT, HWND, LPCWSTR, LPCWSTR, UINT)(('MessageBoxW', windll.user32))
#MessageBox = windll.user32.MessageBoxW #(HWND hWnd,LPCWSTR lpText,LPCWSTR lpCaption,UINT uType);
MessageBoxTimeout = windll.user32.MessageBoxTimeoutW #(Optional ByVal hwndOwner As Long, Optional ByVal lpszText As Long, Optional ByVal lpszCaption As Long, Optional ByVal dwStyle As Long, Optional ByVal wLanguageId As Integer, Optional ByVal dwTimeOut As Long) As Long
#' dwStyle:��ť����,vbYesNo...; wLanguageId:һ��Ϊ0; dwTimeout:�Ժ���Ϊ��λ.  �����ʱ�����û�δ��������Ϣ���Զ��رգ�����32000��

def msgbox(text, caption='MessageBox', style=0, timeout=-1):
    if style==0:
        flags = MB_ICONQUESTION | MB_YESNO | MB_SYSTEMMODAL
    else:
        flags = MB_ICONWARNING | MB_OKCANCEL | MB_SYSTEMMODAL
    #end if

    if timeout == -1:
        ret = MessageBox(0, text, caption, flags)
    else:
        ret = MessageBoxTimeout(0, text, caption, flags, 0, timeout)
    #end if
##    ret = MessageBox(0, LPCTSTR(text), LPCTSTR(caption), flags)
    return True if ret in [1, 6] else False

#------------------------------ Test ------------------------------
if __name__ == '__main__':
    if 0:
    ##if 1:
        mmm=msgbox('�й�\nHello', '��ʾ', 0, 3000)
        print(mmm)

##    if 0:
    if 0:
        ddd=browsefolder('�й�')
        print(ddd)

##    if 0:
    if 1:
        dlg = FileDialog()
        ooo=dlg.showopen(File="z:\\�й�aaaa", FilterIndex=1,
                         Filter='Python �ļ�|*.py;*.pyw|All files(*.*)|*.*',
                         MultiSel=True)
        print(ooo)

##    if 0:
    if 0:
        dlg = FileDialog()
        sss=dlg.showsave(File="�й�aaaa.txt",
                         Filter='Python �ļ�|*.py;*.pyw|C&C++ �ļ�|*.c;*.cpp|All Files (*.*)|*.*',
                         FilterIndex=1)
        print(sss)
