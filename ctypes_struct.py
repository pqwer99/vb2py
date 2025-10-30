# -*- coding: gbk -*-


from __future__ import print_function
from __future__ import division
##from __future__ import unicode_literals

import io
import re

srctxt = """
typedef struct  tagICMPHDR
{
    unsigned char *type;         /* 类型 */
    unsigned char* code;         // 代码
    unsigned short * * checksum;    /* 校验和 */
    unsigned short id;          /* 标识符 */
    u_long seq;         /* 序列号 */

    // 这之后的不是标准 ICMP 首部, 用于记录时间
    unsigned long timestamp;
}ICMPHDR, *LPICMPHDR; //aaaaaaa

struct  ICMPHDR1 {// 11111111
    unsigned char type;         /* 类型 */
    unsigned   char   code;         // 代码
    long   timestamp[12];
};  //2222222222

struct  ICMPHDR2
{    /* xxxxxxxxx */
    unsigned char type;         /* 类型 */
    unsigned   char   code [ 10][10] ;         // 代码
};

struct  ICMPHDR3 // 3333333
{
    unsigned char type;         /* 类型 */
    unsigned char code;         // 代码
    TCHAR *szType;  /* 控件类型: button, edit etc. */
    TCHAR *szTitle; /* 控件上显示的文字 */
};
"""

d_key = {'char':'c_char', 'short':'c_short', 'int':'c_long','long':'c_long',
        'unsigned char':'c_ubyte', 'unsigned short':'c_ushort',
        'unsigned int':'c_ulong', 'unsigned long':'c_ulong',
        'float':'c_float', 'double':'c_double'}

keyrepl = lambda xxx: xxx.replace(xxx, d_key.get(xxx, xxx))

def buildstruct(srctxt):
    stringio_struct = io.StringIO()

    is_struct = False
    fields = []
    lastfield = ''

    srctxt = srctxt.replace('{', '\n')

    for line in srctxt.splitlines():
##        if line.strip().startswith('//'): continue
##        if line.strip().startswith('/*') and line.strip().endswith('*/'): continue

        if (' struct ' in ' ' + line):
            rf = re.findall('.* struct\s* (\w*)\s*(.*)', ' ' + line)[0]
            name, note = rf[0].strip(), rf[1].strip()
            note = note[2:-2].strip() if note.endswith('*/') else note[2:].strip()
            tmpl = u'class {}(Structure):    #{}' if note else u'class {}(Structure):{}'
            stmt = tmpl.format(name, note)
            stmt = stmt + '\n' + ' '*4 + '_fields_ = ['
##            print('\n' + stmt)
            stringio_struct.write('\n' + stmt + '\n')

            is_struct = True
            fields = []
            lastfield = ''
            continue
        #end if
        if '}' in line:
            for (name, ftype, note) in fields:
                if name=='':    # 仅注释
                    stmt = u' '*4 + '# ' + note
                else:
                    # ({name}, {type}){sep=,| }    {note=# | }
                    tmpl = u'("{}", {}){}    # {}' if note else u'("{}", {}){}{}'
                    if name != lastfield:   # 分隔符是','
                        stmt = ' '*4 + tmpl.format(name, ftype, ',', note)
                    else:   # 最后一个成员，无分隔符
                        stmt = ' '*4 + tmpl.format(name, ftype, ' ', note)
                    #end if
                #end if
##                print(stmt)
                stringio_struct.write(stmt + '\n')
            #end for

            _, _, other = line.partition('}')
            other = other.strip()
            if other.startswith(';'): other = other[1:].strip()

            tmpl = u'] #{}' if other else u'] {}'
            stmt = tmpl.format(other)
            # 声明结束，']'
            stringio_struct.write(stmt + '\n')

            is_struct = False
            fields = []
            lastfield = ''
            continue
        #end if
        if is_struct:
            line = line.strip()
            if not line: continue   # 空行
            if line.startswith(r'/'):    # 注释行
                name, ftype, note = '', '', line
            else:
                statement, _, comment = line.partition(';')
                note = comment.strip()

                if '*' in statement:    # 是指针
                    is_pointer = True
                    statement = statement.replace('*', ' ', 1)
                else:
                    is_pointer = False
                #end if

                if '[' in statement:     # 是数组
                    statement, _, part2 = statement.partition('[')
                    part2 = part2.replace('[', ' ').replace(']', ' ')
                    arraysize = part2.split()
                    is_array = True
                else:
                    is_array = False
                #end if

                expr = statement.strip().split()
                name, ftype = expr[-1].strip(), ' '.join(expr[:-1])

                # c类型转换成python ctypes
                ftype = keyrepl(ftype)
                if is_pointer: ftype = "POINTER({})".format(ftype)
                if is_array: ftype = ftype + ' * ' + ' * '.join(arraysize)

                lastfield = name
            #end if
            note = note[2:-2].strip() if note.endswith('*/') else note[2:].strip()
            fields.append((name, ftype, note))
##            print(name, ftype, ' # ', note)
        #end if
    #end for
    return stringio_struct


if __name__ == '__main__':
    pysrc = buildstruct(srctxt)
    print(pysrc.getvalue())

