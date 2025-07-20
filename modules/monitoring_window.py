from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import cv2, time, pandas as pd
from datetime import datetime
from ultralytics import YOLO
import test_driver_drowsiness_detector_module as monitor
from PyQt5.QtWidgets import QApplication



class MonitoringThread(QThread):
    update_status = pyqtSignal(str)
    session_complete = pyqtSignal(pd.DataFrame)

    def __init__(self, username, sessions_col):
        super().__init__()
        self.username = username
        self.sessions_col = sessions_col
        self.running = False

    def run(self):
        self.running = True
        session_id = f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        model = YOLO(monitor.resource_path("path _for_model_weights"))
        cap = cv2.VideoCapture(0)
        blink_tracker = monitor.BlinkTracker()
        yawn_tracker = monitor.YawnTracker()
        df = pd.DataFrame(columns=[
            "timestamp", "blink_count", "avg_blink_duration",
            "total_eye_closure_duration", "yawn_count",
            "drowsiness_state", "reroute_triggered"
        ])
        last_collect_time = time.time()
        state = "NORMAL"

        while self.running:
            ret, frame = cap.read()
            if not ret: break
            try:
                results = model(frame)
            except Exception: continue

            eye_conf = {"eye_open": 0.0, "eye_closed": 0.0}
            classes = set()
            for box in results[0].boxes:
                cid = int(box.cls[0].item())
                conf = box.conf[0].item()
                nm = results[0].names[cid]
                if nm in eye_conf:
                    eye_conf[nm] = max(eye_conf[nm], conf)
                else:
                    classes.add(nm)
            if eye_conf["eye_closed"] or eye_conf["eye_open"]:
                dominant_eye = max(eye_conf, key=eye_conf.get)
                classes.add(dominant_eye)

            blink_tracker.update(classes)
            yawn_tracker.update(classes)
            blink_count, avg_blink_duration, total_eye_closure_duration = blink_tracker.get_stats()
            yawn_count = yawn_tracker.get_stats()

            state, (msg, sound) = monitor.evaluate_driver_state(
                blink_count, avg_blink_duration,
                total_eye_closure_duration, yawn_count, classes
            )
            self.update_status.emit(f"[STATE: {state}] {msg}")

            now = time.time()
            if now - last_collect_time >= 1.0:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[len(df)] = [ts, blink_count, avg_blink_duration,
                    total_eye_closure_duration, yawn_count, state, "None"]
                last_collect_time = now

            if state == "STRONG":
                cap.release()
                monitor.play_sound(sound)

                monitor.reroute_to_nearest_stop()
                time.sleep(5)  # Give browser time to launch before logging and exiting

                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[len(df)] = [ts, blink_count, avg_blink_duration,
                    total_eye_closure_duration, yawn_count, state, "Yes"]
                
                break

            elif state == "MODERATE":
                # cap.release()
                monitor.play_sound(sound)
                app = QApplication.instance()
                user_choice = QMessageBox.question(
                    app.activeWindow() or app.focusWidget(),
                    "Moderate Drowsiness",
                    "Reroute to rest stop?",
                    QMessageBox.Yes | QMessageBox.No
                )
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[len(df)] = [ts, blink_count, avg_blink_duration,
                    total_eye_closure_duration, yawn_count, state,
                    "Yes" if user_choice == QMessageBox.Yes else "No"]
                if user_choice == QMessageBox.Yes:
                    monitor.reroute_to_nearest_stop()
                    time.sleep(5)
                    break
                else:
                    blink_tracker.reset()
                    yawn_tracker.reset()
                    last_collect_time = time.time()
                    state = "NORMAL"

            # annotated = results[0].plot()
            # cv2.imshow("Driver Monitor", annotated)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        cap.release()
        # cv2.destroyAllWindows()
        self.log_session_to_db(session_id, df)
        self.session_complete.emit(df)

    def stop(self):
        self.running = False

    def log_session_to_db(self, session_id, df):
        try:
            metrics_list = df.to_dict(orient="records")
            session_entry = {
                "username": self.username,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics_list
            }
            self.sessions_col.insert_one(session_entry)
        except Exception as e:
            print(f"[ERROR] Failed to save session: {e}")

class MonitoringWindow(QDialog):
    def __init__(self, username, sessions_col):
        super().__init__()
        self.username = username
        self.sessions_col = sessions_col
        self.setWindowTitle(f"Monitoring Panel ({username})")
        self.setFixedSize(300, 200)

        self.start_btn = QPushButton("Start Monitoring")
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn.clicked.connect(self.stop_monitoring)

        self.monitor_thread = None

    def start_monitoring(self):
        self.monitor_thread = MonitoringThread(self.username, self.sessions_col)
        self.monitor_thread.update_status.connect(self.show_status)
        self.monitor_thread.session_complete.connect(self.session_done)
        self.monitor_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitoring(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def show_status(self, msg):
        print(msg)  # Or update a GUI label if you want

    def session_done(self, df):
        QMessageBox.information(self, "Session Complete", "Session metrics saved to cloud.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)