# -*- coding: GBK -*-

from __future__ import print_function
from __future__ import division
##from __future__ import unicode_literals

import io
import sys
import re

##from ctypes import *

import parse

__all__ = ['getvbdeclare', 'makectypes']

PY2 = sys.version_info[0]==2
PY3 = sys.version_info[0]==3

if PY2:
    open = io.open

"""
语法 1
[Public | Private] Declare Sub name Lib "libname" [Alias "aliasname"] [([arglist])]

语法 2
[Public | Private] Declare Function name Lib "libname" [Alias "aliasname"] [([arglist])] [As type]

语法
[Private | Public] Type varname
    elementname [([subscripts])] As type
    . . .
End Type
数据类型；Byte(1)、Boolean(2)、Integer(2)、Long(4)、Currency(8)、Single(4)、Double(8)、
          Date(8)、String（对变长的字符串）、String * length（对定长的字符串）、
          Object(4)、Variant(4)、其它的用户自定义的类型或对象类型。

"""

def getvbdeclare(filename):
    stringio_vb = io.StringIO()
    is_code = False

    with open(filename, encoding="gbk") as vf:
        for line in vf:
            # 忽略Form文件中的界面部分
            if line.startswith('Attribute '):
                is_code = True
                continue
            if not is_code: continue

            aline = ' ' + line.strip()     #消除语句后的'\n'及空格
            # 前面加空格，能保证正确取得无Private或Public的定义
            statement, _, _ = aline.partition("'")  # 排除注释里的 Sub, Function, Declare

            # 以下两条，保证只取（声明）部分，忽略后面的代码
            if (' Sub ' in statement or ' Function ' in statement) and not (' Declare ' in statement): break
            if ' Property ' in statement: break

            # 保存原VB代码
            stringio_vb.write(line)
##            print(line)
        #end for
    #end with
    return stringio_vb

##def vbnum(value):
##    value = value[:-1] if value[-1:] in '!@#%&' else value
##    value = value.replace('&H', '0x', 1)    # 十六进制转换， &H -> 0x
##    value = value.replace('Or', '+')    # Or -> +
##    return value

def vbnum(value):
    """VB常量的右值转换
    """
    value = value.replace('Or', '+')    # Or -> +
    value = value.replace('&H', '0x')    # 十六进制转换， &H -> 0x
    for v in '!@#%&':    # 数值尾部的类型符号
        value = value.replace(v, '')
    return value

p_api = parse.compile('{}Declare {} {name} Lib {libname} {arglist}')
p_api_alias = parse.compile('{}Declare {} {name} Lib {libname} Alias {aliasname} {arglist}')
def build_declare(stmt):
    if ' Alias ' in stmt:
        p = p_api_alias.parse(stmt)
        aliasname = p['aliasname'][1:-1]
    else:
        p = p_api.parse(stmt)
        aliasname = p['name']
    #end if
    name, libname, arglist = p['name'], p['libname'][1:-1], p['arglist'].strip()

    libname = libname.split('.')[0]     # xxxxx.dll消去.dll
    if aliasname[:1] == '#':    # api是数字编号
        aliasname = aliasname[1:]
        api_tmpl = u'{} = windll.{}[{}]  #{}'    # windll.xxx[yyy]
    else:
        api_tmpl = u'{} = windll.{}.{}  #{}'     # windll.xxx.yyy
    #end if
    api_stmt = api_tmpl.format(name, libname, aliasname, arglist)
    return api_stmt

p_const = parse.compile('{name} = {value}')
p_const_as = parse.compile('{name} As {} = {value}')
def build_const(expr):
    expr = expr.strip()
    p = p_const_as.parse(expr) if ' As ' in expr else p_const.parse(expr)
    name, value = p['name'].strip(), p['value'].strip()
    if '"' not in value: value = vbnum(value)   # 数值处理
    const_stmt = u'{} = {}'.format(name, value)
##    print(const_stmt)
    return const_stmt

p_enum = parse.compile('{}Enum {name}')
p_enum_item = parse.compile('{name} = {value}')
def build_enumitem(expr):
    global enum_defaultvalue
    expr = expr.strip()
    if expr:
        if '=' in expr:
            p = p_enum_item.parse(expr)
            name, value = p['name'].strip(), p['value'].strip()
            try:    # 处理类似于：x = a + b
                value = vbnum(value)   # 数值处理
                enum_defaultvalue = eval(value)    # 不要用int(),不能处理十六进制数
            except:
                pass    # enumitem = 变量
        else:   # 无直接赋值， = 上一项的值+1
            enum_defaultvalue += 1
            name, value = expr.strip(), str(enum_defaultvalue)
        #end if
        # 处理带 '[' 或 空格 的名称，如 [xx yy] = 1
        if name[:1] == '[': name = name[1:-1].replace(' ', '_')
        enum_stmt =  u'{} = {}'.format(name, value)
    else:      # 空行
        enum_stmt = u''
    #end if
    return enum_stmt


p_type = parse.compile('{}Type {name}')
p_type_fields = parse.compile('{name} As {type}')

d_vbpy = {'Byte':'c_ubyte', 'Boolean':'c_ushort', 'Integer':'c_short', 'Long':'c_long',
        'Currency':'c_longlong', 'Single':'c_float', 'Double':'c_double',
        'Object':'c_void_p', 'Variant':'c_void_p', 'String':'c_wchar'}    # TCHAR=c_wchar
p_vbpy = re.compile("|".join(d_vbpy.keys()))

def makectypes(vbdeclare):
    stringio_py = io.StringIO()
    stringio_ctypes = io.StringIO()

    mf_api = io.StringIO()
    mf_const = io.StringIO()
    mf_enum = io.StringIO()
    mf_type = io.StringIO()

    backslashline = []
    is_enum = False
    is_type = False

    for line in vbdeclare.splitlines():
        line = ' ' + line.strip()     #消除语句后的'\n'及空格
        # 前面加空格，能保证parse的{}正确匹配无Private或Public的定义

        # 处理续行符，合并
        if line[-2:] == ' _':
            backslashline.append(line[:-1])
            continue
        else:
            aline = ' '.join(backslashline) + line if backslashline else line
            backslashline = []
        #end if

        statement, _, comment = aline.partition("'")

        # ========== API调用 ==========
        if ' Declare ' in statement:
            delare_stmt = build_declare(aline)
##            print(delare_stmt)
            stringio_py.write(delare_stmt + '\n')
            mf_api.write(delare_stmt + '\n')
            continue
        #end if

        # ========== 常量赋值 ==========
        if ' Const ' in statement:
            _, _, stmt = statement.partition(' Const ')
            if ',' in stmt:
                # Const xxx = 1, yyy As Long = 2, zzz = 3
                exprlist = [build_const(expr) for expr in stmt.split(',')]
                const_stmt = '\n'.join(exprlist)
            else:
                const_stmt = build_const(stmt)
            #end if
            note = comment.strip()
            if note: const_stmt = const_stmt + '    # ' + note
#***********************************************************************************
##            try:
##                exec(const_stmt, globals(), locals())    # 处理类似于：x = a + b
##            except:
##                pass
#***********************************************************************************
            stringio_py.write(const_stmt + '\n')
            mf_const.write(const_stmt + '\n')
            continue
        #end if

        # ========== 枚举声明 ==========
        if (' Enum ' in statement) and not (' End Enum' in statement):    # 1, 声明开始
            p = p_enum.parse(statement)
            name, note = p['name'].strip(), comment.strip()
            enum_tmpl = u'if 1: ' + ('##class {}(Enum):    # {}' if note else u'##class {}(Enum):{}')
            enum_stmt = enum_tmpl.format(name, note)
##            print(enum_stmt)
            stringio_py.write(enum_stmt + '\n')
            mf_enum.write('\n' + enum_stmt + '\n')

            is_enum = True
            global enum_defaultvalue
            enum_defaultvalue = -1
            continue
        if ' End Enum' in statement:   # 2，结束
##            print('##End Enum\n')
            stringio_py.write(u'##End Enum\n')
            mf_enum.write(u'##End Enum\n')
            is_enum = False
            continue
        if is_enum:     # 3，遍历枚举成员，！！！1，2，3次序不能变
            if ':' in statement:
                # Const xxx = 1, yyy As Long = 2, zzz = 3
                exprlist = [build_enumitem(expr) for expr in statement.split(':')]
                enum_stmt = u'\n    '.join(exprlist)
            else:
                enum_stmt = build_enumitem(statement)
            #end if
            note = comment.strip()
            if enum_stmt:
                if note: enum_stmt = enum_stmt + '    # ' + note
            else:
                if note: enum_stmt = '# ' + note
            enum_stmt = u' '*4 + enum_stmt
#***********************************************************************************
##            try:
##                exec(enum_stmt, globals(), locals())    # 处理类似于：x = a + b
##            except:
##                pass
#***********************************************************************************
            stringio_py.write(enum_stmt + '\n')
            mf_enum.write(enum_stmt + '\n')
            continue
        #end if

        # ========== Type声明 ==========
        if (' Type ' in statement) and not (' End Type' in statement):    # 1, 结构声明开始
            p = p_type.parse(statement)
            name, note = p['name'].strip().upper(), comment.strip()
            type_tmpl = u'class {}(Structure):    #{}' if note else u'class {}(Structure):{}'
            type_stmt = type_tmpl.format(name, note)
            type_stmt = type_stmt + '\n' + ' '*4 + '_fields_ = ['
##            print('\n' + type_stmt)
            stringio_py.write(type_stmt + '\n')
            mf_type.write('\n' + type_stmt + '\n')

            is_type = True
            typefields = []
            lastfield = ''
            continue
        #end if
        if ' End Type' in statement:   # 2，结束
            for (name, ftype, note) in typefields:
                if name=='':    # 空行 或 注释行
                    fields_stmt = '# {}'.format(note) if note else u''
                else:
                    # ({name}, {type}){sep=,| }    {note=# | }
                    fields_tmpl = u'("{}", {}){}    # {}' if note else u'("{}", {}){}{}'
                    if name != lastfield:   # 分隔符是','
                        fields_stmt = fields_tmpl.format(name, ftype, ',', note)
                    else:   # 最后一个成员，无分隔符
                        fields_stmt = fields_tmpl.format(name, ftype, ' ', note)
                    #end if
                #end if
                fields_stmt = u' '*4 + fields_stmt
                stringio_py.write(fields_stmt + '\n')
                mf_type.write(fields_stmt + '\n')
            #end for
            # 声明结束，']'
            stringio_py.write(u']\n')
            mf_type.write(u']\n')

            is_type = False
            typefields = []
            lastfield = ''
            continue
        #end if
        if is_type:     # 3，遍历结构成员，！！！1，2，3次序不能变
            if statement.strip():
                p = p_type_fields.parse(statement)
                name, ftype, note = p['name'].strip(), p['type'].strip(), comment.strip()
                # VB类型转换成ctypes
#***********************************************************************************
                ftype = p_vbpy.sub(lambda m: d_vbpy[re.escape(m.group(0))], ftype)
#***********************************************************************************
                try:
                    if '(' in name:     # 成员是数组
                        if ' To ' in name:  # A(x To y)
                            p = parse.parse('{name}({lbound} To {ubound})', name)
                            size = int(p['ubound']) - int(p['lbound']) + 1
                        else:   # A(x)
                            p = parse.parse('{name}({size})', name)
                            size = int(p['size']) + 1
                        #end if
                        name = p['name']
                        ftype = ftype + ' * {}'.format(size)
                    #end if
                except:
                    note = u'*需要修改！ ' + note #pass
                typefields.append((name, ftype, note))
                lastfield = name
            else:      # 只有注释行
                typefields.append(('', '', comment.strip()))
            #end if
            continue
        #end if

        # ========== 其他语句 ==========
        if ' Dim ' in statement or ' Private ' in statement or ' Public ' in statement:
            # 变量声明，忽略
            continue
        elif aline.strip() == '':
            stringio_py.write(u'\n')
        else:
            stringio_py.write(u'#' + aline + u'\n')
##            stringio_py.write(u'\n')
        #end if
    #end for

    stringio_ctypes.write(mf_api.getvalue())
    stringio_ctypes.write(u'\n')
    stringio_ctypes.write(mf_const.getvalue())
    stringio_ctypes.write(u'\n')
    stringio_ctypes.write(mf_enum.getvalue())
    stringio_ctypes.write(u'\n')
    stringio_ctypes.write(mf_type.getvalue())
    stringio_ctypes.write(u'\n')

##    return stringio_ctypes #stringio_py
    return stringio_py

if __name__ == '__main__':
    vbsrc = getvbdeclare(r'test.bas')
    pysrc = makectypes(vbsrc.getvalue())
##    print(vbsrc.getvalue())
    print(pysrc.getvalue())

