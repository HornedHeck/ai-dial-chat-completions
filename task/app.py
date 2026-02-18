import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    dial_client = DialClient("gpt-4")

    conversation = Conversation()
    conversation.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))

    while True:
        user_input = input().strip()
        if user_input.lower() == "exit":
            break

        conversation.messages.append(Message(Role.SYSTEM, user_input))

        if stream:
            message = await dial_client.stream_completion(conversation.messages)
        else:
            message = dial_client.get_completion(conversation.messages)
        conversation.messages.append(message)

asyncio.run(
    start(True)
)
