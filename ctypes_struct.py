# -*- coding: gbk -*-


from __future__ import print_function
from __future__ import division
##from __future__ import unicode_literals

import io
import re

srctxt = """
typedef struct  tagICMPHDR
{
    unsigned char *type;         /* ���� */
    unsigned char* code;         // ����
    unsigned short * * checksum;    /* У��� */
    unsigned short id;          /* ��ʶ�� */
    u_long seq;         /* ���к� */

    // ��֮��Ĳ��Ǳ�׼ ICMP �ײ�, ���ڼ�¼ʱ��
    unsigned long timestamp;
}ICMPHDR, *LPICMPHDR; //aaaaaaa

struct  ICMPHDR1 {// 11111111
    unsigned char type;         /* ���� */
    unsigned   char   code;         // ����
    long   timestamp[12];
};  //2222222222

struct  ICMPHDR2
{    /* xxxxxxxxx */
    unsigned char type;         /* ���� */
    unsigned   char   code [ 10][10] ;         // ����
};

struct  ICMPHDR3 // 3333333
{
    unsigned char type;         /* ���� */
    unsigned char code;         // ����
    TCHAR *szType;  /* �ؼ�����: button, edit etc. */
    TCHAR *szTitle; /* �ؼ�����ʾ������ */
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
                if name=='':    # ��ע��
                    stmt = u' '*4 + '# ' + note
                else:
                    # ({name}, {type}){sep=,| }    {note=# | }
                    tmpl = u'("{}", {}){}    # {}' if note else u'("{}", {}){}{}'
                    if name != lastfield:   # �ָ�����','
                        stmt = ' '*4 + tmpl.format(name, ftype, ',', note)
                    else:   # ���һ����Ա���޷ָ���
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
            # ����������']'
            stringio_struct.write(stmt + '\n')

            is_struct = False
            fields = []
            lastfield = ''
            continue
        #end if
        if is_struct:
            line = line.strip()
            if not line: continue   # ����
            if line.startswith(r'/'):    # ע����
                name, ftype, note = '', '', line
            else:
                statement, _, comment = line.partition(';')
                note = comment.strip()

                if '*' in statement:    # ��ָ��
                    is_pointer = True
                    statement = statement.replace('*', ' ', 1)
                else:
                    is_pointer = False
                #end if

                if '[' in statement:     # ������
                    statement, _, part2 = statement.partition('[')
                    part2 = part2.replace('[', ' ').replace(']', ' ')
                    arraysize = part2.split()
                    is_array = True
                else:
                    is_array = False
                #end if

                expr = statement.strip().split()
                name, ftype = expr[-1].strip(), ' '.join(expr[:-1])

                # c����ת����python ctypes
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

