from typing import AsyncIterable

from aidial_client import Dial, AsyncDial
from aidial_client.types.chat import ChatCompletionResponse, ChatCompletionChunk

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._client = Dial(base_url=DIAL_ENDPOINT, api_key=self._api_key)
        self._async_client = AsyncDial(base_url=DIAL_ENDPOINT, api_key=self._api_key)

    def get_completion(self, messages: list[Message]) -> Message:
        response: ChatCompletionResponse = self._client.chat.completions.create(deployment_name=self._deployment_name,
            messages=self.__prepare_messages(messages), stream=False, )

        if len(response.choices) < 1:
            raise Exception("No choices in response found")

        message = response.choices[0].message.content
        print(message)
        return Message(Role.AI, message)

    async def stream_completion(self, messages: list[Message]) -> Message:
        response: AsyncIterable[ChatCompletionChunk] = await self._async_client.chat.completions.create(
            deployment_name=self._deployment_name, messages=self.__prepare_messages(messages), stream=True, )

        message = []
        async for chunk in response:
            if len(chunk.choices) > 0 and (content := chunk.choices[0].delta.content):
                message.append(content)
        message = ''.join(message)
        print(message)
        return Message(Role.AI, message)

    @staticmethod
    def __prepare_messages(messages: list[Message]) -> list[dict[str, str]]:
        return [message.to_dict() for message in messages]
