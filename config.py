#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 4000
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")
    SUBSCRIPTION_KEY = os.environ.get("SubscriptionKey","391b26481cc6477f8b82b8429e5a0b9d")
    SUBSCRIPTION_REGION = os.environ.get("SubscriptionRegion", "Central US")
    #SUBSCRIPTION_KEY
    #SUBSCRIPTION_REGION = "Global"
