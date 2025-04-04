import chainlit as cl
from openai import AsyncOpenAI  # importing openai for API usage
from chainlit.input_widget import Select, Slider  # importing input widgets
from dotenv import load_dotenv

load_dotenv()

# ChatOpenAI Templates
system_template = """You are a helpful assistant who always speaks in a pleasant tone!
"""

user_template = """{input}
Think through your response step by step.
"""

@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Model",
                values=["gpt-4", "gpt-3.5-turbo"],
                initial_value="gpt-3.5-turbo",
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=0,
                min=0,
                max=2,
                step=0.1,
            ),
        ]
    ).send()
    cl.user_session.set("settings", settings)


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)
    cl.user_session.set("settings", settings)

@cl.on_message
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    client = AsyncOpenAI()

    print(message.content)

    messages = [
        {"role": "system", "content": system_template},
        {"role": "user", "content": user_template.format(input=message.content)}
    ]

    msg = cl.Message(content="")

    # Call OpenAI
    async for stream_resp in await client.chat.completions.create(
        messages=messages,
        stream=True,
        model=settings["model"],
        temperature=settings["temperature"],
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    ):
        token = stream_resp.choices[0].delta.content
        if token:
            await msg.stream_token(token)

    await msg.send()

    # # Send a response back to the user
    # await cl.Message(
    #     content=f"Received: {message.content}",
    # ).send()