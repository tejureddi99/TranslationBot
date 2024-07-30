# config.py
import os

class DefaultConfig:
    PORT = 4000
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")
    SUBSCRIPTION_KEY = os.environ.get("SubscriptionKey", "ea800e77eed8493995a8b4997c21f678")
    SUBSCRIPTION_REGION = os.environ.get("SubscriptionRegion", "centralus")
    SUBSCRIPTION_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
