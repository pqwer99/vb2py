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

class OPENFILENAME(Structure):
    _fields_ = [("lStructSize", DWORD),
                ("hwndOwner", HWND),
                ("hInstance", HINSTANCE),
                ("lpstrFilter", POINTER(c_wchar)), #LPCTSTR),
                ("lpstrCustomFilter", LPTSTR),
                ("nMaxCustFilter", DWORD),
                ("nFilterIndex", DWORD),
                ("lpstrFile", POINTER(c_wchar)),    #LPTSTR),   #LPCTSTR无法保存NULL
                ("nMaxFile", DWORD),
                ("lpstrFileTitle", LPTSTR),
                ("nMaxFileTitle", DWORD),
                ("lpstrInitialDir", LPCTSTR),
                ("lpstrTitle", LPCTSTR),
                ("flags", DWORD),
                ("nFileOffset", WORD),
                ("nFileExtension", WORD),
                ("lpstrDefExt", LPCTSTR),
                ("lCustData", LPARAM),
                ("lpfnHook", LPVOID),
                ("lpTemplateName", LPCTSTR),
                ("pvReserved", LPVOID),
                ("dwReserved", DWORD),
                ("flagsEx", DWORD)]

GetActiveWindow = windll.user32.GetActiveWindow #(VOID);
CommDlgExtendedError = windll.comdlg32.CommDlgExtendedError #(VOID);
##GetOpenFileName = WINFUNCTYPE(c_bool, POINTER(OPENFILENAME))(('GetOpenFileNameW', windll.comdlg32))
GetOpenFileName = windll.comdlg32.GetOpenFileNameW #(LPOPENFILENAME lpofn)
GetSaveFileName = windll.comdlg32.GetSaveFileNameW #(LPOPENFILENAME lpofn)

class FileDialog(object):
    def __init__(self, title="", maxfilesize=MAX_PATH*80):
        self._ofn = OPENFILENAME()
        self._ofn.lStructSize = sizeof(OPENFILENAME)
        self._ofn.hwndOwner = GetActiveWindow()
        self._ofn.flags = OFN_EXPLORER | OFN_NOCHANGEDIR
        self._ofn.nMaxFile = MAX_PATH if maxfilesize < MAX_PATH else maxfilesize

        self._ofn.lpstrTitle = title
        self._ofn.lpstrInitialDir = os.getcwd()
        self._ofn.lpstrFile = create_unicode_buffer(self._ofn.nMaxFile)
        self._ofn.lpstrFilter = create_unicode_buffer('All Files (*.*)\0*.*\0\0', MAX_PATH * 10)
        self._ofn.lpstrDefExt = '\0' * MAX_PATH

        self.__filename = ''
        self.mutliselected = False
        self.error = 0

    @property
    def initdir(self):
        return self._ofn.lpstrInitialDir
    @initdir.setter
    def initdir(self, initdir):
        self._ofn.lpstrInitialDir = initdir

    @property
    def defext(self):
        return self._ofn.lpstrDefExt
    @defext.setter
    def defext(self, ext):
        self._ofn.lpstrDefExt = ext

    @property
    def filterstr(self):
        return wstring_at(self._ofn.lpstrFilter, self._ofn.nMaxFile).split('\0\0', 1)[0].replace('\0', '|')
    @filterstr.setter
    def filterstr(self, setfilter):
        self._ofn.lpstrFilter = create_unicode_buffer(setfilter.replace('|', '\0') + '\0\0')

    @property
    def filterindex(self):
        return self._ofn.nFilterIndex
    @filterindex.setter
    def filterindex(self, filterindex):
        self._ofn.nFilterIndex = filterindex

    @property
    def filename(self):
        return self.__filename
    @filename.setter
    def filename(self, setfilename):
        self._ofn.lpstrFile = create_unicode_buffer(setfilename, self._ofn.nMaxFile)

    def showopen(self, allowmultiselect=False):
        self.error = 0
        if allowmultiselect:    # 多选
            self._ofn.flags = OFN_EXPLORER | OFN_NOCHANGEDIR | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_ALLOWMULTISELECT
        else:
            self._ofn.flags = OFN_EXPLORER | OFN_NOCHANGEDIR | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
        ret = GetOpenFileName(byref(self._ofn))
        if ret==0:  # 取消或出错
            self.__filename = ''
            self.error = CommDlgExtendedError()
        else:
            # lpstrFile以双NULL结尾
            # 如果是多选，格式为D:\PATH(NULL)FILE1(NULL)FILE2(NULL)FILE3...(NULL)(NULL)

            lpstrFile_buffer = wstring_at(self._ofn.lpstrFile, self._ofn.nMaxFile)
            lpstrFile_buffer = lpstrFile_buffer.split('\0\0', 1)[0]  # 忽略缓冲区里双NULL后的无用字符
            if '\0' in lpstrFile_buffer:
                lpstrFile_buffer = lpstrFile_buffer.split('\0')
                fpath = lpstrFile_buffer[0]
                self.__filename = [fpath + '\\' + fname for fname in lpstrFile_buffer[1:]]
                self.mutliselected = True
            else:
                self.__filename = lpstrFile_buffer
                self.mutliselected = False
        return False if ret==0 else True

    def showsave(self):
        self._ofn.flags = OFN_EXPLORER | OFN_NOCHANGEDIR | OFN_OVERWRITEPROMPT
        ret = GetSaveFileName(byref(self._ofn))
        if ret == 0:
            self.__filename = ''
            self.error = CommDlgExtendedError()
        else:
            self.__filename =  wstring_at(self._ofn.lpstrFile)
        return False if ret==0 else True

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

#MessageBox = windll.user32.MessageBoxW #(HWND hWnd,LPCWSTR lpText,LPCWSTR lpCaption,UINT uType);
MessageBox = WINFUNCTYPE(UINT, HWND, LPCWSTR, LPCWSTR, UINT)(('MessageBoxW', windll.user32))
##MessageBox = WINFUNCTYPE(UINT, HWND, LPCSTR, LPCSTR, UINT)(('MessageBoxA', windll.user32))

def msgbox(text, caption='MessageBox', style=0):
    if style==0:
        flags = MB_ICONQUESTION | MB_YESNO | MB_SYSTEMMODAL
    else:
        flags = MB_ICONWARNING | MB_OKCANCEL | MB_SYSTEMMODAL

    ret = MessageBox(0, text, caption, flags)
##    ret = MessageBox(0, LPCTSTR(text), LPCTSTR(caption), flags)
    return True if ret in [1, 6] else False

#------------------------------ Test ------------------------------
if __name__ == '__main__':
    if 0:
    ##if 1:
        mmm=msgbox('中国\nHello', '提示', 0)
        print(mmm)

##    if 0:
    if 1:
        ddd=browsefolder('中国')
        print(ddd)

    if 0:
##    if 1:
        dlg = FileDialog("选择文件")
        dlg.filterstr='Python 文件|*.py;*.pyw|All Files (*.*)|*.*'
        dlg.filterindex=2
    ##    dlg.filename="中国aaaa.txt"
        ooo=dlg.showopen(True)
        print(ooo, dlg.mutliselected, dlg.filename, sep=",")

##    if 0:
    if 1:
        dlg = FileDialog()
        dlg.filename="中国bbbb.txt"
    ##    dlg.defext='cpp'
        dlg.filterstr='Python 文件|*.py;*.pyw|C&C++ 文件|*.c;*.cpp|All Files (*.*)|*.*'
        ooo=dlg.showsave()
        print(ooo, dlg.filename, sep=",")
