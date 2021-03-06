import os
import email
from ChineseSegmentation import JB, parseEmail as pe, myEmail, FileController as fc, MongoDB
import re
from _datetime import datetime
import sys

def get_content(email_text):
    email_content = ""
    pos = max(email_text.find("X-MimeOLE"), email_text.find("X-Mailer"), email_text.find("Content-Type"), email_text.find("boundary"),
              email_text.find("charset"),email_text.find("Disposition-Notification-To"))
    i = 0
    for line in email_text[pos:].splitlines(keepends=True):
        r1 = "\s+"
        line = re.sub(r1, " ", line)
        line = line.replace("\n", "")
        if i > 0:
            email_content += line
        i += 1
    return email_content


def get_date(email_text):
    date = ""
    pos = email_text.find("Date")
    existTime = True
    # 如果邮件格式中不含有Date标签
    if pos == -1:
        pos = find_min_date_pos(email_text)
        existTime = False
    # 获取时间
    for line in email_text[pos:].splitlines(keepends=True):
        r1 = "\s+"
        line = re.sub(r1, " ", line)
        line = line.replace("\n", "")
        date += line
        break
    if existTime:
        date = date[6:]
    if pos != -1:
        return datetime.strptime(date[5:24], '%d %b %Y %H:%M:%S')
    else:
        return None


def find_min_date_pos(email_text):
    min_pos = sys.maxsize
    for date in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        pos = email_text.find(date)
        if pos > 0:
            min_pos = min(min_pos, pos)
            print(pos)
    if min_pos != sys.maxsize:
        return min_pos
    else:
        return -1


def get_emails(db):
    path = "trec06c/data"
    dirs = os.listdir(path)
    new_emails = []
    i = 0
    for dir in dirs:
        new_emails.clear()
        user = MongoDB.choose_user(db, dir)
        emails = os.listdir(path + "/" + dir)
        j = 0
        for e in emails:
            print(dir + "/" + e, end=" ")
            text = fc.get_text(path + "/" + dir + "/" + e)
            print("邮件长度:", len(text))
            # 打印某封邮件内容
            j = j + 1
            msg = email.message_from_string(text)
            title, addresser, addressee, copy = pe.parse_header(msg)
            date = get_date(text)
            print(date)
            content = get_content(text)
            doc = re.split('。|；|·|！|？|\n', content)
            doc = list(filter(None, doc))
            split = []
            for i in range(len(doc)):
                split.append(JB.participle_text(doc[i]))
                doc[i] = doc[i] + "。"
            # print(split)
            emailKind = ""
            new_email = myEmail.set_email(title, addresser, addressee, copy, date, doc, split, emailKind)
            new_emails.append(new_email)
        i = i + 1
        MongoDB.insert_many(user, new_emails)


if __name__ == '__main__':
    myClient = MongoDB.connect_mongodb()
    emaildb = MongoDB.choose_database(myClient)
    get_emails(emaildb)
    MongoDB.disconnect_mongodb(myClient)
