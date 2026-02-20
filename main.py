from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.core.text import LabelBase
from plyer import storagepath
import os
import traceback
from kivy.clock import Clock
from kivy.resources import resource_find
from datetime import datetime
import numpy as np

# --- KIVY_HOME FIX ---
if os.environ.get('KIVY_BUILD') == 'android':
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        current_activity = PythonActivity.mActivity
        internal_files_dir = current_activity.getFilesDir().getAbsolutePath()
        kivy_home_path = os.path.join(internal_files_dir, '.kivy_data')
        os.makedirs(kivy_home_path, exist_ok=True)
        os.environ['KIVY_HOME'] = kivy_home_path
    except Exception as e:
        print(f"Error setting KIVY_HOME: {e}")

# Register font
LabelBase.register(name="AbyssinicaSIL", fn_regular="fonts/AbyssinicaSIL-Regular.ttf")

# Platform Detection & Imports
try:
    from jnius import autoclass
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

    MediaRecorder = autoclass('android.media.MediaRecorder')
    MediaRecorderAudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    MediaRecorderOutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    MediaRecorderAudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    is_android = True
except ImportError:
    is_android = False
    import sounddevice as sd
    try:
        import wavio
    except ImportError:
        wavio = None

class LoginScreen(Screen):
    def do_login(self, username, password):
        if username and password:
            self.manager.get_screen('main').current_user = username
            self.manager.current = 'main'

class MainScreen(Screen):
    current_line = StringProperty("")
    current_index = NumericProperty(0)
    current_user = StringProperty("")
    is_recording = BooleanProperty(False)
    recordings_directory = StringProperty("")
    
    fs = 16000
    channels = 1
    available_text_files = ListProperty([])
    selected_text_file = StringProperty("file1.txt (bundled)")
    lines = ListProperty([])

    def on_pre_enter(self):
        if is_android:
            self.request_android_permissions()
        else:
            self.setup_paths_and_load()

    def request_android_permissions(self):
        """Cross-version permission handling (Android 11-14)"""
        perms = [Permission.RECORD_AUDIO]
        
        # Modern Android (13+) Media permission
        if hasattr(Permission, 'READ_MEDIA_AUDIO'):
            perms.append(Permission.READ_MEDIA_AUDIO)
        
        # Legacy Android (11/12) Storage permissions
        perms.append(Permission.WRITE_EXTERNAL_STORAGE)
        perms.append(Permission.READ_EXTERNAL_STORAGE)
        
        request_permissions(perms, self.on_permission_callback)

    def on_permission_callback(self, permissions, granted):
        Clock.schedule_once(lambda dt: self.setup_paths_and_load())

    def setup_paths_and_load(self):
        self.set_recordings_directory()
        self.populate_text_file_spinner()
        self.load_lines()

    def set_recordings_directory(self):
        if is_android:
            try:
                base = primary_external_storage_path()
                self.recordings_directory = os.path.join(base, "Music", "LineRecordings", self.current_user)
            except:
                self.recordings_directory = os.path.join(App.get_running_app().user_data_dir, "LineRecordings")
        else:
            self.recordings_directory = os.path.join(os.path.expanduser("~"), "Music", "LineRecordings", self.current_user)
        os.makedirs(self.recordings_directory, exist_ok=True)

    def populate_text_file_spinner(self):
        files = [f"file{i}.txt (bundled)" for i in range(1, 9)]
        files.append("line.txt (bundled)")
        self.available_text_files = sorted(files)

    def on_text_file_selected(self, text_file_name):
        """Logic for Spinner selection changes"""
        self.selected_text_file = text_file_name
        self.load_lines()

    def load_lines(self):
        """Thread-safe loading to prevent UI crashes"""
        file_to_load = self.selected_text_file
        new_lines = []
        
        if "(bundled)" in file_to_load:
            actual_name = file_to_load.replace(" (bundled)", "")
            path = resource_find(actual_name)
            if path:
                try:
                    with open(path, encoding='utf-8') as f:
                        new_lines = [l.strip() for l in f if l.strip()]
                except Exception as e:
                    print(f"File Read Error: {e}")

        if not new_lines:
            new_lines = ["No lines available in this file."]
        
        self.lines = new_lines
        self.current_index = 0
        Clock.schedule_once(lambda dt: self.display_line(0))

    def display_line(self, index):
        if not self.lines:
            return
            
        if 0 <= index < len(self.lines):
            self.current_line = self.lines[index]
            if self.ids and 'line_number_input' in self.ids:
                self.ids.line_number_input.text = str(index + 1)
        else:
            self.current_index = 0
            self.current_line = self.lines[0]

    def start_recording(self):
        if self.is_recording: return
        self.set_recordings_directory()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_line = "".join(c if c.isalnum() else "_" for c in self.current_line)[:30]
        
        # SEQ PREFIX: 001, 002, etc for sorting
        line_num = "{:03d}".format(self.current_index + 1)
        filename = f"{line_num}_{self.current_user}_{clean_line}_{timestamp}"
        
        if is_android:
            try:
                self.recorder = MediaRecorder()
                self.recorder.setAudioSource(MediaRecorderAudioSource.MIC)
                self.recorder.setOutputFormat(MediaRecorderOutputFormat.MPEG_4)
                self.recorder.setAudioEncoder(MediaRecorderAudioEncoder.AAC)
                self.recorder.setAudioSamplingRate(self.fs)
                
                self.audio_path = os.path.join(self.recordings_directory, f"{filename}.m4a")
                self.recorder.setOutputFile(self.audio_path)
                self.recorder.prepare()
                self.recorder.start()
                self.is_recording = True
            except Exception as e:
                print(f"Android record error: {e}")
        else:
            self.audio_path = os.path.join(self.recordings_directory, f"{filename}.wav")
            self.recording_data = sd.rec(int(10 * self.fs), samplerate=self.fs, channels=self.channels)
            self.is_recording = True

    def stop_recording(self):
        if not self.is_recording: return
        if is_android:
            try:
                self.recorder.stop()
                self.recorder.release()
            except: pass
            self.recorder = None
        else:
            sd.stop()
        self.is_recording = False

    def next_line(self):
        if self.current_index < len(self.lines) - 1:
            self.current_index += 1
            self.display_line(self.current_index)

    def prev_line(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_line(self.current_index)

    def go_to_line(self):
        try:
            idx = int(self.ids.line_number_input.text) - 1
            if 0 <= idx < len(self.lines):
                self.current_index = idx
                self.display_line(idx)
        except: pass

    def save_recording(self):
        pass # Auto-saved on stop

class LineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    LineApp().run()
