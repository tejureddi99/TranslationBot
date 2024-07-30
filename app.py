from datetime import datetime, timezone
import sys
import traceback
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import MemoryStorage, TurnContext, UserState
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity, ActivityTypes

from bots.multilingual_bot import MultiLingualBot
from config import DefaultConfig
from translation.translation_middleware import TranslationMiddleware
from azure.ai.translation.text import TextTranslationClient  
from azure.core.credentials import AzureKeyCredential

CONFIG = DefaultConfig()

# Create adapter
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Catch-all for errors
async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.now(timezone.utc),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)

ADAPTER.on_turn_error = on_error

# Create MemoryStorage and state
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)

# Create translation client and middleware
translator = TextTranslationClient(
    endpoint=CONFIG.SUBSCRIPTION_ENDPOINT,  # Use endpoint instead of region
    credential=AzureKeyCredential(CONFIG.SUBSCRIPTION_KEY)
)
TRANSLATION_MIDDLEWARE = TranslationMiddleware(translator, USER_STATE)
ADAPTER.use(TRANSLATION_MIDDLEWARE)

# Create Bot
BOT = MultiLingualBot(USER_STATE)

# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, BOT)

APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
