from tkinter import Tk, BOTH, X, LEFT, IntVar, Radiobutton, Checkbutton, END, Spinbox, RIGHT, Menu
from tkinter.ttk import Frame, Label, Entry, LabelFrame, Button, Separator
from tkinter.filedialog import askopenfile, asksaveasfile, askopenfilename
from tkinter.messagebox import showinfo, showerror
from tkinter.simpledialog import askstring

import subprocess
import json
import os

class OptoController(Frame):

    def __init__(self, path):
        super().__init__()

        menuBar = Menu(self)

        menuFile = Menu(menuBar, tearoff=0)
        menuFile.add_command(label="Load...", command=self.openFile)
        menuFile.add_command(label="Save...", command=self.saveFile)

        menuFile.add_command(label="Reset", command=self.reset)
        menuFile.add_separator()
        menuFile.add_command(label="Locate Arduino...", command=self.defineArduinoProg)
        #menuFile.add_command(label="Define port...", command=self.defineArduinoPort)
        menuFile.add_separator()
        menuFile.add_command(label="Exit", command=self.quitApp)
        menuBar.add_cascade( label="File", menu=menuFile)

        menuHelp = Menu(menuBar, tearoff=0)
        menuHelp.add_command(label="About", command=self.about)
        menuBar.add_cascade( label="Help", menu=menuHelp)

        self.master.config(menu=menuBar)

        self.params = [[1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5]]
        self.clipboard = None
        self.arduinoProg=""
        self.port = "COM18"

        self.master.bind('<Control-c>', self.copyParams)
        self.master.bind('<Control-v>', self.pasteParams)

        if not os.path.exists('sketch'):
            os.makedirs('sketch')

        self.isEnabled = self.params[2][0]
        self.initUI()
        self.update()

        try:
            f = open("optocontroller.cfg", "r")
            l = f.readline().split("=")
            f.close()
            if (len(l)==2 and l[0]=="arduinoProg"):
                self.arduinoProg = l[1]
            else:
                raise IOError
        except IOError:
            self.askArduinoProg()

    def initUI(self):

        self.master.title("TEMPO")
        self.pack(fill=BOTH, expand=True)

        self.selectedBlock=IntVar()
        self.selectedBlock.set(1)


        # PANNEAU 1

        index=[None, None, 1, 0, 2, 5, 3, 4, 7, 6, 9, 8, 11, 15, 10, 14, 13, 17, 12, None, None, None, 16, None]

        self.gridFrame = LabelFrame(self, text="LED block control")
        self.gridFrame.grid(row=0, column=0, padx=(20, 20), pady=(20, 20))

        radio = Radiobutton(self.gridFrame, text=1, variable=self.selectedBlock, value=-1, command=self.update, indicatoron=0, width=2, state='disabled')
        radio.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

        radio = Radiobutton(self.gridFrame, text=2, variable=self.selectedBlock, value=-2, command=self.update, indicatoron=0, width=2, state='disabled')
        radio.grid(row=1, column=0, padx=(10, 10), pady=(10, 10))

        radio = Radiobutton(self.gridFrame, text=3, variable=self.selectedBlock, value=index[2], command=self.update, indicatoron=0, width=2)
        radio.grid(row=2, column=0, padx=(10, 10), pady=(10, 10))
        radio.select()

        for i in range(3, 18):
            radio = Radiobutton(self.gridFrame, text=i+1, variable=self.selectedBlock, value=index[i], command=self.update, indicatoron=0, width=2)
            radio.grid(row=i%4, column=i//4, padx=(10, 10), pady=(10, 10))


        radio = Radiobutton(self.gridFrame, text="19\n\n20", variable=self.selectedBlock, value=index[18], command=self.update, indicatoron=0, width=2, height=4)
        radio.grid(row=2, column=4, padx=(10, 10), pady=(10, 10), rowspan=2, sticky="NE")

        radio = Radiobutton(self.gridFrame, text=21, variable=self.selectedBlock, value=-3, command=self.update, indicatoron=0, width=2, state='disabled')
        radio.grid(row=0, column=5, padx=(10, 10), pady=(10, 10))

        radio = Radiobutton(self.gridFrame, text=22, variable=self.selectedBlock, value=-4, command=self.update, indicatoron=0, width=2, state='disabled')
        radio.grid(row=1, column=5, padx=(10, 10), pady=(10, 10))

        radio = Radiobutton(self.gridFrame, text="23\n\n24", variable=self.selectedBlock, value=index[22], command=self.update, indicatoron=0, width=2, height=4)
        radio.grid(row=2, column=5, padx=(10, 10), pady=(10, 10), rowspan=2, sticky="NE")


        # PANNEAU 2

        self.paramFrame = LabelFrame(self, text="Settings")
        self.paramFrame.grid(row=3, column=0, padx=(20, 20), pady=(20, 20))

        self.enabled = Checkbutton(self.paramFrame, text="Active", variable=self.isEnabled, command=self.updateEnabled)
        self.enabled.select()
        self.enabled.pack(fill=X)



        self.nbPulseFrame = Frame(self.paramFrame)
        self.nbPulseFrame.pack(fill=X)

        self.nbPulseLabel = Label(self.nbPulseFrame, text="Number of pulses:", width=25)
        self.nbPulseLabel.pack(side=LEFT, padx=5, pady=5)

        self.nbPulseEntry = Spinbox(self.nbPulseFrame, from_=1, to=99)
        self.nbPulseEntry.pack(fill=X, padx=5, expand=True)


        vcmd = (self.register(self.validate))


        self.intervalFrame = Frame(self.paramFrame)
        self.intervalFrame.pack(fill=X)

        self.intervalLabel = Label(self.intervalFrame, text="Time interval between pulses:", width=25)
        self.intervalLabel.pack(side=LEFT, padx=5, pady=5)

        self.intervalLabel2 = Label(self.intervalFrame, text="min", width=4)
        self.intervalLabel2.pack(side=RIGHT, padx=5, pady=5)

        self.intervalEntry = Entry(self.intervalFrame, validate="all", validatecommand=(vcmd, '%P'))
        self.intervalEntry.pack(fill=X, padx=5, expand=True)




        self.pulseDurationFrame = Frame(self.paramFrame)
        self.pulseDurationFrame.pack(fill=X)

        self.pulseDurationLabel = Label(self.pulseDurationFrame, text="Pulse duration:", width=25)
        self.pulseDurationLabel.pack(side=LEFT, padx=5, pady=5)

        self.pulseDurationLabel2 = Label(self.pulseDurationFrame, text="s", width=4)
        self.pulseDurationLabel2.pack(side=RIGHT, padx=5, pady=5)

        self.pulseDurationEntry = Entry(self.pulseDurationFrame, validate="all", validatecommand=(vcmd, '%P'))
        self.pulseDurationEntry.pack(fill=X, padx=5, expand=True)




        self.copy = Button(self, text="Copy preset (Ctrl+C)", width=50, command=self.copyParams)
        self.copy.grid(row=1, column=0)

        self.paste = Button(self, text="Paste preset (Ctrl+V)", width=50, command=self.pasteParams)
        self.paste.grid(row=2, column=0)

        self.confirm = Button(self, text="Apply", width=50, command=self.apply)
        self.confirm.grid(row=4, column=0)

        self.separator = Separator(self, orient='horizontal')
        self.separator.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

        self.confirm = Button(self, text="Confirm", width=50, command=self.submit)
        self.confirm.grid(row=6, column=0)

    def update(self):
        i = self.selectedBlock.get();
        if(not self.params[i][0]):
            self.enabled.deselect()
            self.isEnabled=0
            self.nbPulseEntry.delete(0, END)
            self.nbPulseEntry.insert(0, self.params[i][1])
            self.nbPulseEntry.configure(state='disabled')
            self.intervalEntry.delete(0, END)
            self.intervalEntry.insert(0, self.params[i][2])
            self.intervalEntry.configure(state='disabled')
            self.pulseDurationEntry.delete(0, END)
            self.pulseDurationEntry.insert(0, self.params[i][3])
            self.pulseDurationEntry.configure(state='disabled')
        else:
            self.enabled.select()
            self.isEnabled=1
            self.nbPulseEntry.configure(state='normal')
            self.nbPulseEntry.delete(0, END)
            self.nbPulseEntry.insert(0, self.params[i][1])
            self.intervalEntry.configure(state='enabled')
            self.intervalEntry.delete(0, END)
            self.intervalEntry.insert(0, self.params[i][2])
            self.pulseDurationEntry.configure(state='enabled')
            self.pulseDurationEntry.delete(0, END)
            self.pulseDurationEntry.insert(0, self.params[i][3])

    def updateEnabled(self):
        i = self.selectedBlock.get();
        if(self.isEnabled):
            self.params[i][0] = 0
            self.isEnabled = 0
        else:
            self.params[i][0] = 1
            self.isEnabled = 1
        self.apply()
        self.update()
        #print(np.array(self.params)[:,0])

    def apply(self):
        i = self.selectedBlock.get();
        self.params[i][1] = int(self.nbPulseEntry.get())
        self.params[i][2] = int(self.intervalEntry.get())
        self.params[i][3] = int(self.pulseDurationEntry.get())

    def validate(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def openFile(self):
        f = askopenfile(title="Load file:",  mode="r",
                filetypes=[("TEMPO preset", ".oc"), ("All files", ".*")])
        if f is not None:
            self.params=json.load(f)
            f.close()
        self.update()

    def saveFile(self):
        f = asksaveasfile(title="Save:", initialfile="default", mode='w', defaultextension=".oc", filetypes=[("TEMPO preset", ".oc"), ("All files", ".*")])
        if f is not None:
            json.dump(self.params, f)
            f.close()

    def reset(self):
        self.params = [[1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5], [1, 1, 10, 5]]
        self.update()

    def quitApp(self):
        self.master.destroy()

    def about(self):
        showinfo("About", """TEMPO is a software created by the PSC-BIO02 group for the Ecole Polytechnique Collaborative Science Project.\n
                This software is licensed and cannot be distributed or reproduced without the express consent of its owner.\n
                For more information, please contact ysjanati@gmail.com.""")

    def askArduinoProg(self):
        showinfo(title="Locate Arduino", message="TEMPO could not locate Arduino. Please enter arduino.exe path.")
        self.defineArduinoProg()

    def defineArduinoProg(self):
        self.arduinoProg = askopenfilename(title="Locate arduino.exe :", filetypes=[("Executable", ".exe"), ("All files", ".*")])
        f = open("optocontroller.cfg", "w")
        f.write("arduinoProg="+self.arduinoProg)
        f.close()

    def submit(self):
        code = """
long params[18][4] = {"""

        for i in range(len(self.params)):
            if(self.params[i]):
                if(self.params[i][0]):
                    code+="{"+str(self.params[i][1])+", "+str(self.params[i][2]*60000)+", "+str(self.params[i][3]*1000)+"},"
                else:
                    code+="{0, 0, 0},"

        code=code[:-1]
        code+="""};

int ledStates[] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

long previousMillis[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

int index[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3, A4, A5};

void setup() {
  // put your setup code here, to run once:
  for(int i = 0; i < 18; i++) {
    pinMode(index[i], OUTPUT);
    digitalWrite(index[i], ledStates[i]);
  }
  delay(60000);
  long currentMillis = millis()-60000;
  for(int i = 0; i < 18; i++) {
    if(params[i][0] > 0) {
          ledStates[i] = LOW;
          digitalWrite(index[i], LOW);
          previousMillis[i] = currentMillis;
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:

  long currentMillis = millis()-60000;

  for(int i = 0; i < 18; i++) {
    if(params[i][0] > 0) {
      if(ledStates[i] == HIGH) { // Si la LED est eteinte, on l'allume apres un temps current - previous valant interval
        if((currentMillis - previousMillis[i]) >= params[i][1]) {
          ledStates[i] = LOW;
          digitalWrite(index[i], LOW);
          previousMillis[i] = currentMillis;
        }
      } else { // Si la LED est allumee, on l'allume apres un temps current - previous valant pulseDuration
        if((currentMillis - previousMillis[i]) >= params[i][2]) {
          ledStates[i] = HIGH;
          digitalWrite(index[i], HIGH);
          params[i][0] = params[i][0] - 1;
          previousMillis[i] = currentMillis;
        }
      }
    }
  }
}"""

        f = open("sketch/sketch.ino", "w")
        f.write(code)
        f.close()
        if self.arduinoProg != "":
            self.runSketch()

    def runSketch(self):
        self.port = askstring("Arduino port", "Please enter Arduino port:", initialvalue=self.port)
        if self.port=="":
            return
        arduinoCommand = "\"" + self.arduinoProg[:-4] + "_debug.exe\" --upload --board arduino:megaavr:uno2018 --port " + self.port + " sketch/sketch.ino"
        print(arduinoCommand)
        self.master.config(cursor="wait")
        try:
            presult = subprocess.call(arduinoCommand, shell=True)
            self.master.config(cursor="")

            if presult != 0:
                	raise
            else:
                	showinfo("Success", "Compilation is successful.")
        except:
            showerror("Error : code " + str(presult), """TEMPO could not upload Arduino code. \n Please do as the following:\n
                 • Check that the Arduino card is connected and that the Arduino environment is properly configured on the computer;
                 • Check that TEMPO is linked to the arduino.exe executable (File > Locate Arduino...);\n
                 • Check your Arduino port (Windows Start Menu > Device manager > Ports).\n\n
If it still doesn't work, you can compile and upload manually the sketch.ino Arduino code that has been generated in the sketch folder.""")

    def copyParams(self, event=None):
        self.apply()
        i = self.selectedBlock.get();
        self.clipboard = self.params[i][:]

    def pasteParams(self, event=None):
        if self.clipboard:
            i = self.selectedBlock.get();
            self.params[i] = self.clipboard[:]
        self.update()



def main():

    path = "params.txt"

    root = Tk()
    root.geometry("380x575+"+str(int(root.winfo_screenwidth()/2-190))+"+"+str(int(root.winfo_screenheight()/2-280)))
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    app = OptoController(path)
    root.mainloop()


if __name__ == '__main__':
    main()
