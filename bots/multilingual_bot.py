import json
import os

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    CardFactory,
    MessageFactory,
)
from botbuilder.schema import (
    ChannelAccount,
    Attachment,
    SuggestedActions,
    CardAction,
    ActionTypes,
)

from translation.translation_settings import TranslationSettings


class MultiLingualBot(ActivityHandler):
    """
    This bot demonstrates how to use Microsoft Translator.
    More information can be found at:
    https://docs.microsoft.com/en-us/azure/cognitive-services/translator/translator-info-overview
    """

    def __init__(self, user_state: UserState):
        if user_state is None:
            raise TypeError(
                "[MultiLingualBot]: Missing parameter. user_state is required but None was given"
            )

        self.user_state = user_state
        self.language_preference_accessor = self.user_state.create_property("LanguagePreference")

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.attachment(self._create_adaptive_card_attachment())
                )
                await turn_context.send_activity(
                    "This bot will introduce you to translation middleware. Say 'hi' to get started."
                )

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()

        if text == "hi":
            await turn_context.send_activity(
                MessageFactory.text("Hello! Choose your language:")
            )
            await self._send_language_options(turn_context)
        elif self._is_language_change_requested(text):
            current_language = text
            if current_language in (TranslationSettings.english_english.value, TranslationSettings.hindi_english.value):
                lang = TranslationSettings.english_english.value
            else:
                lang = TranslationSettings.english_hindi.value

            await self.language_preference_accessor.set(turn_context, lang)
            await turn_context.send_activity(f"Your current language code is: {lang}")
            await self.user_state.save_changes(turn_context)
        else:
            await turn_context.send_activity("You said: " + turn_context.activity.text)

    async def _send_language_options(self, turn_context: TurnContext):
        reply = MessageFactory.text("Choose your language:")
        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="हिन्दी",
                    type=ActionTypes.post_back,
                    value=TranslationSettings.english_hindi.value,
                ),
                CardAction(
                    title="English",
                    type=ActionTypes.post_back,
                    value=TranslationSettings.english_english.value,
                ),
            ]
        )
        await turn_context.send_activity(reply)

    def _create_adaptive_card_attachment(self) -> Attachment:
        card_path = os.path.join(os.getcwd(), "cards/welcomeCard.json")
        with open(card_path, "rt") as in_file:
            card_data = json.load(in_file)
        return CardFactory.adaptive_card(card_data)

    def _is_language_change_requested(self, utterance: str) -> bool:
        if not utterance:
            return False
        utterance = utterance.lower()
        return utterance in (
            TranslationSettings.english_hindi.value,
            TranslationSettings.english_english.value,
            TranslationSettings.hindi_hindi.value,
            TranslationSettings.hindi_english.value
        )
