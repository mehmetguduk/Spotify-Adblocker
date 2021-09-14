# © Designed and Developed by Mehmet Güdük.
# © Licensed with GPL-3.0 License, Author is Mehmet Güdük.


import time
import sys
import os
import win32gui
from database_functions import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction, qApp, QSystemTrayIcon
from PyQt5.QtCore import QThread, pyqtSignal
from interface import Ui_MainWindow
from PyQt5.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Blocker(QThread):
    block = pyqtSignal()
    playing = pyqtSignal(tuple)
    count = pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def run(self):
        
        while True:
            import ctypes
            from pycaw.pycaw import AudioUtilities 
            EnumWindows = ctypes.windll.user32.EnumWindows    
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible
            titles = []
            def foreach_window(hwnd, lParam):
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLength(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    titles.append(buff.value)
                return True
            EnumWindows(EnumWindowsProc(foreach_window), 0)
            sessions = AudioUtilities.GetAllSessions()
            if "Advertisement" in titles:
                for session in sessions:
                    try:
                        if 'Spotify' in session.Process.name():
                            volume = session.SimpleAudioVolume
                            volume.SetMute(1, None)
                            self.block.emit()
                            empty_tuple = ("","")
                            self.playing.emit(empty_tuple)
                            self.count.emit(1)
                    except AttributeError:
                        pass
            else:
                self.count.emit(0)
                for session in sessions:
                    try:
                        if 'Spotify' in session.Process.name():
                            volume = session.SimpleAudioVolume
                            volume.SetMute(0, None)
                            try:
                                self.playing.emit(self.catch_song_name())
                            except:
                                pass
                    except AttributeError:
                        pass
            time.sleep(0.2)
 
    def catch_song_name(self):
        list_of_windows = []
        finding_window = win32gui.FindWindow("SpotifyMainWindow", None)
        found = win32gui.GetWindowText(finding_window)
        def find_spotify_uwp(hwnd, list_of_windows):
            text_of_windows = win32gui.GetWindowText(hwnd)
            catched_classname = win32gui.GetClassName(hwnd)
            if catched_classname == "Chrome_WidgetWin_0" and len(text_of_windows) > 0:
                list_of_windows.append(text_of_windows)
        if found:
            list_of_windows.append(found)
        else:
            win32gui.EnumWindows(find_spotify_uwp, list_of_windows)
        if len(list_of_windows) == 0:
            pass
        try:
            artist, songname = list_of_windows[0].split(" - ", 1)
        except ValueError:
            artist = ''
            songname = list_of_windows[0]
        except IndexError:
            pass
        return songname, artist



class myApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.blocker = Blocker()
        self.blocker.block.connect(ADDING_LAST_BLOCKED_TIME)
        self.blocker.block.connect(self.changingLabels)
        self.blocker.playing.connect(self.song)
        self.blocker.count.connect(self.blockCounter_tool_one)
        self.blocker.start()
      
        DB_CONNECT()
        DB_TABLES()
        self.changingLabels()

        if DB_CHECKBOX() == "CHECKED":
            self.ui.checkbox.setChecked(True)
            try:
                spotify_location = str(os.getenv('APPDATA')) + "/Spotify/Spotify.exe"
                os.startfile(spotify_location)
            except:
                pass
        else:
            self.ui.checkbox.setChecked(False)
    
        self.ui.combobox.setHidden(1)
        Logo = resource_path("adblocker.ico")
        self.tray_icon = QSystemTrayIcon(self)
        self.icon = QIcon(Logo)
        self.tray_icon.setIcon(self.icon)  
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.beforeQuit)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


        

        self.ui.lbl_copyright.setOpenExternalLinks(True)
        self.ui.checkbox.clicked.connect(self.checkboxControl)
        self.ui.combobox.setCurrentIndex(-1)
        self.ui.combobox.currentIndexChanged.connect(self.lockCounter_tool_two)


    def checkboxControl(self):
        if self.ui.checkbox.isChecked() == True:
            DB_CHECKBOX_CHANGE("CHECKED")
        elif self.ui.checkbox.isChecked() == False:
            DB_CHECKBOX_CHANGE("NOT CHECKED")
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def beforeQuit(self):
        DB_DISCONNECT()
        import ctypes
        from pycaw.pycaw import AudioUtilities 
        EnumWindows = ctypes.windll.user32.EnumWindows    
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        titles = []
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            try:
                if 'Spotify' in session.Process.name():
                    volume = session.SimpleAudioVolume
                    volume.SetMute(0, None)
            except AttributeError:
                pass
    
    def changingLabels(self):
        self.ui.lbl_lasttime.setText(f"{GETTING_LAST_BLOCKED_TIME()}")
        self.ui.lbl_counter.setText(f"{GETTING_BLOCK_COUNT()}")

    def song(self, tuple):
        if str(tuple[1]) != "" and str(tuple[0]) != "":
            self.ui.lbl_song.setText(f"{str(tuple[1])} - {str(tuple[0])}")
        else:
            self.ui.lbl_song.setText("Nothing")

    def blockCounter_tool_one(self, int):
        if int == 1:
            self.ui.combobox.setCurrentIndex(1)
        elif int == 0:
            self.ui.combobox.setCurrentIndex(0)

    def lockCounter_tool_two(self):
        if self.ui.combobox.currentText() == "b":
            ADDING_BLOCK_COUNT()

if __name__ == '__main__': 
    app = QtWidgets.QApplication(sys.argv)
    win = myApp()
    win.show()
    sys.exit(app.exec_())
