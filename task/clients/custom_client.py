import json

import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class ChokingDialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        request_data = {"messages": self.__prepare_messages(messages), }

        response = requests.post(url=self._endpoint, headers=self.__headers(), json=request_data)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        choices = response.json().get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content")
            print(content)
            return Message(Role.AI, content)
        raise Exception("No choices in response found")

    async def stream_completion(self, messages: list[Message]) -> Message:
        request_data = {"stream": True, "messages": self.__prepare_messages(messages), }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=self.__headers(), json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            contents.append(data)

        contents = contents[0:-1]
        return Message(role=Role.AI, content=''.join(contents))

    @staticmethod
    def _get_content_snippet(data: str) -> str:
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''

    @staticmethod
    def __prepare_messages(messages: list[Message]) -> list[dict[str, str]]:
        return [message.to_dict() for message in messages]

    def __headers(self) -> dict:
        return {"api-key": self._api_key, "Content-Type": "application/json"}
