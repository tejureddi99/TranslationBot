from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from translation.translation_settings import TranslationSettings

class MicrosoftTranslator:
    def __init__(self, subscription_key: str, subscription_region: str):
        self.client = TextTranslationClient(
            endpoint="https://api.cognitive.microsofttranslator.com/",
            credential=AzureKeyCredential(subscription_key)
        )
        self.region = subscription_region

    async def translate(self, text_input, language_output):
        try:
            response = await self.client.translate(
                content=[{"text": text_input}],
                to=[language_output],
                api_version="3.0"
            )
            translation = response[0].translations[0].text
            return translation
        except HttpResponseError as e:
            return f"Unable to translate text. Error: {str(e)}"
