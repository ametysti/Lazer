from globals import *
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class DeletionWorker(QThread):
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str, str)
    total_messages_updated = pyqtSignal(int)
    message_progress = pyqtSignal()
    channel_progress = pyqtSignal(str)

    def __init__(self, channels):
        super().__init__()
        self.channels = channels
        self.running = True
        self.headers = {"Authorization": context.token}
        self.user_id = None
        self.session = self.create_resilient_session()
        self.all_messages = []

    def create_resilient_session(self):
        session = requests.Session()
        retry = Retry(
            total=8,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=frozenset(['GET', 'DELETE'])
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        return session

    def run(self):
        try:
            self.user_id = self.get_user_id()
            
            # Collection phase
            for channel in self.channels:
                if not self.running:
                    break
                try:
                    self.channel_progress.emit(f"Fetching messages from {channel['name']}")
                    if channel["type"] == "dm":
                        self.collect_dm_messages(channel)
                    elif channel["type"] == "server":
                        self.collect_server_messages(channel)
                except Exception as e:
                    self.error_occurred.emit(str(e), channel["name"])

            # Deletion phase
            self.total_messages_updated.emit(len(self.all_messages))
            self.channel_progress.emit("Deleting messages...")
            
            for idx, (msg_id, channel_id, context) in enumerate(self.all_messages):
                if not self.running:
                    break
                try:
                    self.delete_message(msg_id, channel_id)
                except Exception as e:
                    self.error_occurred.emit(str(e), context)
                finally:
                    self.message_progress.emit()
                    time.sleep(0.6)

        except Exception as e:
            self.error_occurred.emit(str(e), "Global")
        finally:
            self.finished.emit()

    def get_user_id(self):
        response = self.session.get(
            f"{BASE_URL}/users/@me",
            headers=self.headers,
            timeout=10,
            verify=True
        )
        return response.json()["id"]

    def collect_dm_messages(self, channel):
        self.collect_messages(channel["id"], channel["name"])

    def collect_server_messages(self, server):
        response = self.session.get(
            f"{BASE_URL}/guilds/{server['id']}/channels",
            headers=self.headers,
            timeout=10
        )
        channels = response.json()
        
        for ch in channels:
            if ch["type"] in [0, 5] and self.running:
                context = f"{server['name']}/#{ch['name']}"
                self.collect_messages(ch["id"], context)

    def collect_messages(self, channel_id, context):
        before = None
        while self.running:
            params = {"limit": 100}
            if before:
                params["before"] = before
                
            response = self.session.get(
                f"{BASE_URL}/channels/{channel_id}/messages",
                headers=self.headers,
                params=params,
                timeout=15
            )
            messages = response.json()
            
            for msg in messages:
                if msg["author"]["id"] == self.user_id:
                    self.all_messages.append((msg["id"], channel_id, context))
            
            if len(messages) < 100:
                break
            before = messages[-1]["id"]

    def delete_message(self, message_id, channel_id):
        response = self.session.delete(
            f"{BASE_URL}/channels/{channel_id}/messages/{message_id}",
            headers=self.headers,
            timeout=15,
            verify=True
        )
        
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            time.sleep(max(retry_after, 5))
            self.delete_message(message_id, channel_id)
            
        response.raise_for_status()

    def stop(self):
        self.running = False