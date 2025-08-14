import json
import logging
import asyncio
from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, Phind, FreeChatgpt, Liaobots, OpenaiChat

# Configure logging
logger = logging.getLogger(__name__)

def get_ai_response(prompt):
    """
    This function takes a prompt and yields the response from the g4f AI as a stream.
    Uses the new AsyncClient API for better streaming support.
    """
    async def _stream_response():
        try:
            # Use a retry provider to avoid providers that return 429 / unavailable
            client = AsyncClient(
                provider=RetryProvider([Phind, FreeChatgpt, Liaobots, OpenaiChat], shuffle=False)
            )
            
            stream = client.chat.completions.stream(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                web_search=False
            )

            async for chunk in stream:
                # Some providers emit different structures; handle robustly
                try:
                    if hasattr(chunk, "choices") and chunk.choices:
                        choice = chunk.choices[0]
                        # Streaming delta content
                        if hasattr(choice, "delta") and choice.delta:
                            content = choice.delta.get("content") if isinstance(choice.delta, dict) else getattr(choice.delta, "content", None)
                            if content:
                                yield content
                                continue
                        # Non-streaming fallback (full message)
                        if hasattr(choice, "message") and choice.message:
                            content = choice.message.get("content") if isinstance(choice.message, dict) else getattr(choice.message, "content", None)
                            if content:
                                yield content
                                continue
                except Exception:
                    # Skip malformed chunks silently
                    continue
                    
        except Exception as e:
            yield f"An error occurred: {e}"
    
    # Create an async generator and run it in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async_gen = _stream_response()
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()
