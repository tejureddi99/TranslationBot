from typing import Callable, Awaitable, List
from botbuilder.core import Middleware, UserState, TurnContext
from botbuilder.schema import Activity, ActivityTypes
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from translation.translation_settings import TranslationSettings  # Ensure this import is included

class TranslationMiddleware(Middleware):
    """
    Middleware for translating text between the user and bot.
    Uses the Azure Text Translation SDK.
    """

    def __init__(self, translator: TextTranslationClient, user_state: UserState):
        self.translator = translator
        self.language_preference_accessor = user_state.create_property(
            "LanguagePreference"
        )

    async def on_turn(
        self, context: TurnContext, logic: Callable[[TurnContext], Awaitable]
    ):
        """
        Processes an incoming activity.
        :param context: The context for the current turn.
        :param logic: The logic to execute.
        :return: 
        """
        translate = await self._should_translate(context)
        if translate and context.activity.type == ActivityTypes.message:
            context.activity.text = await self._translate_text(
                context.activity.text, TranslationSettings.default_language.value
            )

        async def aux_on_send(
            ctx: TurnContext, activities: List[Activity], next_send: Callable
        ):
            user_language = await self.language_preference_accessor.get(
                ctx, TranslationSettings.default_language.value
            )
            should_translate = (
                user_language != TranslationSettings.default_language.value
            )

            # Translate messages sent to the user to user language
            if should_translate:
                for activity in activities:
                    if activity.type == ActivityTypes.message:
                        activity.text = await self._translate_text(
                            activity.text, user_language
                        )

            return await next_send()

        async def aux_on_update(
            ctx: TurnContext, activity: Activity, next_update: Callable
        ):
            user_language = await self.language_preference_accessor.get(
                ctx, TranslationSettings.default_language.value
            )
            should_translate = (
                user_language != TranslationSettings.default_language.value
            )

            # Translate messages sent to the user to user language
            if should_translate and activity.type == ActivityTypes.message:
                activity.text = await self._translate_text(
                    activity.text, user_language
                )

            return await next_update()

        context.on_send_activities(aux_on_send)
        context.on_update_activity(aux_on_update)

        await logic()

    async def _should_translate(self, turn_context: TurnContext) -> bool:
        user_language = await self.language_preference_accessor.get(
            turn_context, TranslationSettings.default_language.value
        )
        return user_language != TranslationSettings.default_language.value

    async def _translate_text(self, text: str, target_locale: str) -> str:
        """
        Translates the given text to the target locale.
        :param text: Text to be translated.
        :param target_locale: Target language code.
        :return: Translated text.
        """
        try:
            response = await self.translator.translate(
                content=[{"text": text}],
                to=[target_locale],
                api_version="3.0"
            )
            translation = response[0].translations[0].text
            return translation
        except HttpResponseError as e:
            return f"Unable to translate text. Error: {str(e)}"
