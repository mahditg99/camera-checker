import traceback
import requests
from threading import Thread
from datetime import datetime as dt
import time
from pythonping import ping
from typing import List
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout

import jdatetime

def timestamp_to_shamsi(timestamp):
    # Convert the timestamp to a Gregorian datetime object
    gregorian_date = dt.fromtimestamp(timestamp)
    
    # Convert the Gregorian date to a Shamsi (Jalali) date
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    
    # Return the Shamsi date as a formatted string
    return shamsi_date.strftime("%Y-%m-%d %H:%M:%S")



# dt.ti

# input(' .')
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout,QTextEdit

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

        
        # self.setWindowTitle('camera checker')  # Set the window title to "LPR"
            # Set the window icon to your logo image
        # self.setWindowIcon(QIcon('logo.png'))
        # print('hello')
        self.setGeometry(100, 100, 900, 580)
        self.setStyleSheet("""
                QWidget {
                    background-color: #36454f;  /* Charcoal grey for the overall widget background */
                }
                QLabel, QRadioButton, QComboBox {
                    font-family: 'Segoe UI';  /* A clean, modern font */
                    font-size: 11pt;  /* Clear, readable font size */
                    color: #800080;  /* Deep purple color for text in labels, radio buttons, and combo boxes */
                }
                QLabel#speedWLabel, QLabel#numLineLabel {  /* Replace with the actual object names of your labels */
                    color: #800080;  /* Deep purple color for specific labels */
                }
                QPushButton {
                    background-color: #808080;
                    border: 1px solid #707070;
                    border-radius: 10px;
                    padding: 6px 15px;
                    font-weight: bold;
                    color: #800080;
                    border-image: url(path/to/your/shadow-image.png) 10 10 10 10 stretch stretch;
                }
                
                QPushButton:hover {
                    background-color: #909090;
                }
                QTextEdit, QLineEdit {
                    background-color: #3b4b5a;  /* Lighter black for text fields */
                    color: #ffffff;  /* White color for text in input fields */
                    border: 1px solid #3d5565;
                    border-radius: 4px;
                    padding: 2px;  /* Padding inside text fields */
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #34495e;  /* Highlight border when focused */
                }
                QComboBox {
                    background-color: #34495e;  /* Dark navy blue, almost black, for combo box background */
                    color: #ff8c00;  /* Rich orange color for combo box text */
                    border: 1px solid #3d5565;
                    border-radius: 4px;
                    padding: 2px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #3d5565;
                }
                QTaskBox {
                    background-color: #333b45;  /* Darker shade for the task box */
                    color: #27ae60;  /* Green text color */
                    border: 1px solid #3d5565;
                    border-radius: 4px;
                    padding: 2px;  /* Padding inside the task box */
                }
            """)


        # Set up the user interface
  
        # Create a QLineEdit widget (text field)
        self.task_box = QTextEdit(self)
        self.task_box.setReadOnly(True)
        self.task_box.setStyleSheet("""
                QTextEdit {
              
                    color: #33cc33;
                    font: 15pt "Tahoma";
                    
                }
            """)
        # Create a QPushButton widget (button) labeled 'Start'
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.on_click)  # Connect the button's click event to the on_click method

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.task_box)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Camera Status checker')
        self.show()
    
    def on_click(self):
          # Disable the start button to prevent multiple clicks
        self.start_button.setEnabled(False)

        self.worker = Worker()
        self.worker.progress.connect(self.update_text)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()

    def update_text(self, message):
        self.task_box.setText(message)

    def task_finished(self):
        # Re-enable the start button when the task is finished
        self.start_button.setEnabled(True)

        return



class Worker(QThread):
    # def __init__
    # Define a signal to communicate with the main thread
    progress = pyqtSignal(str)
    # Define a signal to indicate that the task is finished
    finished = pyqtSignal()
    def thread_get(self,connected_cameras,disconnected_cameras,ip,id):
        
        try:

            result=requests.get(f"http://192.168.168.138:5007/api/v1/plate/search?page=1&size=1&order=Dessending&fromSpeed=&toSpeed=&cameraId={id}&showPlateImage=true&hasWanted=false&unknownPlate=false&isInterval=false&plateNumberStatus&plate2No_1=-1&plate2No_2=-1&plate3No_1=-1&plate3No_2=-1&plate3No_3=-1&cityPlateNo_1=-1&cityPlateNo_2=-1&freePlate1=-1&freePlate2=-1&freePlate3=-1&freePlate4=-1&freePlate5=-1&freePlate6=-1&freePlate7=-1&crossingLine&carType=-1&cameraType").json()
            
            result=result['list'][0]
            transit_time = dt.strptime(result['transitTime'], "%Y-%m-%dT%H:%M:%SZ").timestamp()
            # transit_time=int(str(result['referenceID'])[3:13])
            connect=True
            txt = f'Camera : {result['cameraLocation'].ljust(30)} with ip {ip} is '
            # print(time.time()-transit_time,time.time(),transit_time)
            if abs(time.time()-transit_time)/60 >20:
                connect=False
                # print(time.time() ,transit_time ,abs(time.time()-transit_time))
                txt=f'{txt} Disconnected '
                try:
                    response = ping(ip, count=4, timeout=.5,verbose=False)

                    res = any(r.success for r in response)
                except Exception as e:
                    res = False
                if res:
                    successful_rtts = [round(r.time_elapsed,2 )for r in response if r.success]
                    # print(response)
                    txt=f'{txt} but has ping with in 4 retry : {successful_rtts}'
                else:
                    txt=f'{txt} and no ping at last 4 retry'
            else:
                txt=f'{txt} Connected'
                try:
                    if len(result['irImage'])>0:
                        txt=f' {txt} has image'
                    else:
                        txt=f' {txt} has No image'
                except :
                    txt=f' {txt} has No image'

            date= result['name'].split('_')[2:]
            
            txt=f'{txt} -- last data recieved at {timestamp_to_shamsi(transit_time)}\n{'-'*60}\n'
            # txt = f'<p style="line-height: 0.5;">' \
            # f'<font color="green">{txt}</font></p>'
            
            self.line=f'{self.line}{txt}'
            if connect:
                connected_cameras.append(txt)
            else:
                disconnected_cameras.append(txt) 


            self.progress.emit(self.line)
        except :
            print   ( ip, id,traceback.format_exc())



    def run(self):
        self.line=''
        disconnected_cameras=[]
        connected_cameras=[]
        try:
            # camera_ids=[i for i in range(100,500)]
            # self.start_button.setCheckable(False)
        # self.task_box.setText('hello')
 

            cameras = requests.get('http://192.168.168.138:5007/api/v1/get_dashboard_cameras',timeout=5).json()['list']

            cameras=[{'id':cam['id'],'ip':cam['ip']} for cam in cameras]

            # Define the message to display
            # message = 'Button clicked!'
            # self.task_box.setText(message)
            threads:List[Thread]=[]
            for cam in cameras:
               threads.append(Thread(target=self.thread_get,args=(connected_cameras,disconnected_cameras,cam['ip'],cam['id'],)))

            for i in range(0,len(threads),20):
                j= i+20 if i +20 < len(threads) else len(threads)
                for t in threads[i:j]:
                    t.daemon=True
                    t.start()
                for t in threads[i:j]:
                    t.join()

        except:
            print(traceback.format_exc())

        self.line=f'Task completed!\n\nDisconnected cameras :\n\n' if len(disconnected_cameras)>0 else 'Task completed!\n\n'
        # txt = f'<br><br><p style="line-height: 0.5;">' \
        #         f'<font color="green">Task completed!</font></p><br><br>'
        # txt=f'Task completed!\n\n'

        for i in disconnected_cameras:
            self.line=f'{self.line}{i}'

        self.line=f'{self.line}\n\nconnected cameras :\n\n' if len(connected_cameras)>0 else f'{self.line}'
        for i in connected_cameras:
            self.line=f'{self.line}{i}'
        self.progress.emit(f'{self.line}')
        # Emit the finished signal when the task is done
        self.finished.emit()
                # Display the message in the text field
        # self.text_field.setText(message)
# def get_data(arg):
       
        
            # print(txt)
            # print('-'*40)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = SimpleApp()
    ex.show()
    sys.exit(app.exec_())
