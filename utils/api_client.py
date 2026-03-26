# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import requests
from typing import Optional, Dict, Any, Generator

class RandstadApiClient:
    """
    Client for interacting with the Randstad Agent FastAPI application.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}

    def health_check(self) -> bool:
        """Checks if the API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200 and response.json().get("status") == "ok"
        except requests.RequestException:
            return False

    def create_session(self, user_id: str, app_name: str = "app") -> str:
        """Creates a new session for a user."""
        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions"
        data = {"state": {}}
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["id"]

    def chat_stream(
        self, 
        user_id: str, 
        session_id: str, 
        message: str, 
        app_name: str = "app"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Sends a message to the agent and yields events from the SSE stream.
        """
        url = f"{self.base_url}/run_sse"
        data = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}],
            },
            "streaming": True,
        }

        response = requests.post(url, headers=self.headers, json=data, stream=True, timeout=60)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    yield json.loads(line_str[6:])

    def send_feedback(self, user_id: str, session_id: str, score: int, text: Optional[str] = None) -> bool:
        """Sends feedback for a session."""
        url = f"{self.base_url}/feedback"
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "score": score,
            "text": text
        }
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        return response.status_code == 200
