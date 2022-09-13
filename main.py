import os
#-------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
#-------------------------------------------------
import sqlite3 as db
#-------------------------------------------------
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
#-------------------------------------------------
import smtplib
#-------------------------------------------------
import imaplib
#-------------------------------------------------
import email
#-------------------------------------------------

con = db.connect('user.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT,
    serverSMTP TEXT,
    serverIMAP TEXT
)""")
con.commit()

class GUI(object):
    def __init__(self):
        self.isLogined = False
        a = self.getDataIntoDB()
        self.filepath=''
        self.filename = os.path.basename(self.filepath)
        self.allFiles = list()

        self.root = tk.Tk()
        self.root.title('')
        self.root.geometry('900x400')

        self.mainMenu = tk.Menu(self.root)
        self.root.config(menu=self.mainMenu)
        self.filemenu = tk.Menu(self.mainMenu, tearoff=0)
        self.filemenu.add_command(label="Выйти из аккаунта", command=self.deleteDataIntoDB)
        self.mainMenu.add_cascade(label='File', menu=self.filemenu)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack()
        self.mainFrame1 = tk.Frame(self.root)
        self.mainFrame1.pack()
        self.mainFrame2 = tk.Frame(self.root)
        self.mainFrame2.pack()
        self.notebook.add(self.mainFrame1, text='Send Message')
        self.notebook.add(self.mainFrame2, text='Get and Read Message')
        self.uiFrame = tk.Frame(self.mainFrame1)
        self.uiFrame.pack(side=tk.LEFT)
        self.treeviewFrame = tk.Frame(self.mainFrame1)
        self.treeviewFrame.pack(side=tk.RIGHT)

        if self.isLogined == True:
            self.load()
        if self.isLogined == False:
            self.login()

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.__exit)
        self.root.mainloop()
 
    def __exit(self):
        self.root.destroy()

    def send(self):
        a = self.getDataIntoDB()
        msg = MIMEMultipart()
        message = self.message.get(0.1, tk.END)
        password = a[2]
        msg['From'] = a[1]
        msg['To'] = self.sendTo.get()
        msg['Subject'] = self.subject.get()
        msg.attach(MIMEText(message, 'plain'))
        #------------------------------------------------------------
        for i in self.allFiles:
            filename = os.path.basename(i)
            with open(i, 'rb') as fp:
                ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                file = MIMEBase(maintype, subtype)
                file.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(file)
            file.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(file)
        #------------------------------------------------------------
        server = smtplib.SMTP(a[3])
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("successfully sent email to %s:" % (msg['To']))
        self.sendTo.delete(0, tk.END)
        self.subject.delete(0, tk.END)
        self.message.delete(1.0, tk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)
        messagebox.showinfo(title="Sent successfully !", message="successfully sent email to %s" % (msg['To']))

    def login(self):
        self.win = tk.Tk()
        self.win.geometry('300x300')
        self.emailLabel = tk.Label(self.win, text='Email')
        self.emailLabel.pack()
        self.email = tk.Entry(self.win)
        self.email.pack()
        self.passwordLabel = tk.Label(self.win, text='Password')
        self.passwordLabel.pack()
        self.password = tk.Entry(self.win)
        self.password.pack()
        self.serverSMTPLabel = tk.Label(self.win, text='Server SMTP')
        self.serverSMTPLabel.pack()
        self.serverSMTP = tk.Entry(self.win)
        self.serverSMTP.pack()
        self.serverIMAPLabel = tk.Label(self.win, text='Server IMAP')
        self.serverIMAPLabel.pack()
        self.serverIMAP = tk.Entry(self.win)
        self.serverIMAP.pack()
        self.addUser = tk.Button(self.win, text='Add user', command=self.addUserFunc)
        self.addUser.pack()

    def load(self):

        self.sendToLabel = tk.Label(self.uiFrame, text='Send to')
        self.sendToLabel.pack()
        self.sendTo = tk.Entry(self.uiFrame)
        self.sendTo.pack()
        self.subjectLabel = tk.Label(self.uiFrame, text='Subject')
        self.subjectLabel.pack()
        self.subject = tk.Entry(self.uiFrame)
        self.subject.pack()
        self.messageLabel = tk.Label(self.uiFrame, text='Message')
        self.messageLabel.pack()
        self.message = tk.Text(self.uiFrame)
        self.message.pack()

        self.treeviewFrameCont = tk.Frame(self.treeviewFrame)
        self.treeviewFrameCont.pack()

        columns = ("#1")
        self.tree = ttk.Treeview(self.treeviewFrameCont, show="headings", columns=columns)
        self.tree.heading("#1", text="File name")
        ysb = tk.Scrollbar(self.treeviewFrameCont, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky=tk.N + tk.S)

        self.addFile = tk.Button(self.treeviewFrameCont, text='Add a file', command=self.addFileFunc)
        self.addFile.grid(row=1, column=0)
        self.clearList = tk.Button(self.treeviewFrameCont, text='Clear list', command=self.clearListFunc)
        self.clearList.grid(row=2, column=0)
        self.send = tk.Button(self.treeviewFrameCont, text='Send', command=self.send)
        self.send.grid(row=3, column=0)

        self.printButton = tk.Label(self.mainFrame2, text='Not worked\nDo it')
        self.printButton.pack()

        self.treeviewFrameCont2 = tk.Frame(self.mainFrame2)
        self.treeviewFrameCont2.pack()

        columns = ("#1")
        self.tree2 = ttk.Treeview(self.treeviewFrameCont2, show="headings", columns=columns)
        self.tree2.heading("#1", text="Mail")
        ysb = tk.Scrollbar(self.treeviewFrameCont2, orient=tk.VERTICAL, command=self.tree2.yview)
        self.tree2.configure(yscroll=ysb.set)
        self.tree2.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky=tk.N + tk.S)


    def print_selection(self, event):
        for selection in self.tree2.selection():
            item = self.tree2.item(selection)
            email = item["values"][0]
            text = "Выбор: {}"
            print(text.format(email))

    def clearListFunc(self):
        self.allFiles = list()
        for i in self.tree.get_children():
            self.tree.delete(i)
        messagebox.showinfo(title="Canceled", message="All files are canceled")

    def addUserFunc(self):
        self.addDataIntoDB(0, self.email.get(), self.password.get(), self.serverSMTP.get(), self.serverIMAP.get())
        self.win.destroy()
        self.load()

    def addDataIntoDB(self, id, email, password, serverSMTP, serverIMAP):
        con = db.connect('user.db')
        cur = con.cursor()

        user = (id, email, password, serverSMTP, serverIMAP)

        cur.execute("INSERT OR IGNORE INTO user VALUES(?, ?, ?, ?, ?);", user)
        self.isLogined = True
        con.commit()

    def deleteDataIntoDB(self):
        con = db.connect('user.db')
        cur = con.cursor()
        cur.execute("DELETE FROM user WHERE id=0")
        con.commit()

        self.sendToLabel.destroy()
        self.sendTo.destroy()
        self.subjectLabel.destroy()
        self.subject.destroy()
        self.messageLabel.destroy()
        self.message.destroy()
        self.treeviewFrameCont.destroy()
        self.printButton.destroy()
        self.treeviewFrameCont2.destroy()
        self.filemenu.destroy()
        self.mainMenu.pack_forget()

        self.login()

        self.isLogined = False
        print('exit')

    def getDataIntoDB(self):
        con = db.connect('user.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM user WHERE  id = 0')
        a = cur.fetchone()
        con.commit()

        if a != None:
            self.isLogined = True
        elif a == None:
            self.isLogined = False
        return a

    def addFileFunc(self):
        self.filepath = askopenfilename()
        self.filename = os.path.basename(self.filepath)
        self.allFiles.insert(-1, self.filepath)
        self.tree.insert("", tk.END, values=self.filename)

if __name__ == '__main__':
    app = GUI()
    app.start()
