
import tempfile
import subprocess
import re


def pdf_to_string(file_object):
    pdfData = file_object.read()
    tf = tempfile.NamedTemporaryFile()
    tf.write(pdfData)
    tf.seek(0)
    outputTf = tempfile.NamedTemporaryFile()

    if (len(pdfData) > 0):
        out, err = subprocess.Popen(
            ["pdftotext", "-layout", tf.name, outputTf.name]).communicate()
        return outputTf.read()
    else:
        return None


# find out the summary paragraph
# why rb - read and binary?
# 无文本文件预处理-导致需要decode-bytes 用utf-8的方式解码

def read_file(filen):
    with open('../DebitStatement/' + filen + '.pdf', 'rb') as f:
        s = pdf_to_string(f).decode('utf-8')
    return s


def string_split(filen, i):
    summary = read_file(filen).split('JIAWEI XIA', 3)[2]
    sp1 = re.split('\n', summary)
    sp2 = [x.strip() for x in sp1[3:10] if x != '']
    if 0 <= i < 6:
        sp_am = re.findall('(-|\$)?([\d|,]+\.\d{2})', sp2[i])
        res = sp_am
    else:
        res = 'none'
    return res


def dic_money_amount(filen, i):
    (neg, am) = string_split(filen, i)[0]
    amr = re.sub(',', '', am)
    f_am = float(amr)
    if len(amr) > 0:
        if neg == '-':
            r_am = f_am*(-1)
            return r_am
        else:
            return f_am
    else:
        return 'none'


def dic_statement(filen):
    summary_statement = {
        'Beginning balance': dic_money_amount(filen, 0),
        'Deposits and other additions': dic_money_amount(filen, 1),
        'Withdrawals and other subtractions': dic_money_amount(filen, 2),
        'Checks': dic_money_amount(filen, 3),
        'Service fees': dic_money_amount(filen, 4),
        'Ending balance': dic_money_amount(filen, 5)
    }
    return summary_statement


def cat_name(filen):
    catn = []
    for key in dic_statement(filen):
        if read_file(filen).count(key) > 1:
            catn.append(key)
        else:
            continue
    return catn


def part_split(filen):
    cat_list = []
    for part in cat_name(filen):
        pre_part = read_file(filen).split(part, 2)[2]
        ext_part = pre_part.split('Total ' + part.lower(), 1)[0]
        cat_list.append(ext_part)
    return cat_list


print()
