"""
Orchard Alexa Skill

Orchard can tell the user...
    - where to find an item
    - how much an item costs
    - if the user has coupons for an item
    - if an item is on sale

Created by Zach Komorowski

*Copyright Orchard 2017*

Version 2.0
"""

from __future__ import print_function
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Orchard. " \
                    "Ask me where to find an item by saying, " \
                    "where is the peanut butter?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask my where an item is by saying, " \
                    "where is the peanut butter."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for shopping with Orchard. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# sets the store in session
def set_store(intent):
    store = intent['slots']['Store']['value']
    store.lower()
    return store

# def set_location(intent):
#     location = intent['slots']['Location']['value']
#     return location

# creates 2-d inventory list
def inventoryList(store):
    sheet = client.open("Orchard Mock Data")

    if (store == "home depot"):
        inventory_list = sheet.worksheet('home depot').get_all_values()
    elif (store == "whole foods on washtenaw"):
        inventory_list = sheet.worksheet('whole foods washtenaw').get_all_values()
    elif (store == "whole foods on main street"):
        inventory_list = sheet.worksheet('whole foods main street').get_all_values()
    elif (store == "meijer"):
        inventory_list = sheet.worksheet('meijer').get_all_values()
    elif (store == "trader joe's"):
        inventory_list = sheet.worksheet('trader joes').get_all_values()

    inventory_list.pop(0)

    return inventory_list

# returns aisle number of specified item if in stock, returns 0 if out of stock
def getAisle(item, inventory):
    item = item.lower()
    for i in range(len(inventory)):
        if (inventory[i][0].lower() == item):
            return inventory[i][1]

    return 0

# returns price of item
def getPrice(item, inventory):
    item = item.lower()
    for i in range(len(inventory)):
        if (inventory[i][0].lower() == item):
            return inventory[i][2]

    return 0

# returns coupon for said item
def getCoupon(item, inventory):
    item = item.lower()
    for i in range(len(inventory)):
        if (inventory[i][0].lower() == item):
            return inventory[i][3]

    return 0

# returns the sale for said item
def getSale(item, inventory):
    item = item.lower()
    for i in range(len(inventory)):
        if (inventory[i][0].lower() == item):
            return inventory[i][4]

    return 0

# creates attributes of item
def create_item_attributes(item, intent):
    store = set_store(intent)
    inventory = inventoryList(store)
    aisle = getAisle(item, inventory)
    price = getPrice(item, inventory)
    coupon = getCoupon(item, inventory)
    sale = getSale(item, inventory)

    return {"item": item,
            "aisle" : aisle,
            "store" : store,
            "price" : price,
            "coupon" : coupon,
            "sale" : sale
            }

# for AisleIntent, returns aisle to Alexa user
def set_aisle_in_session(intent, session):
    """ Sets the aisle number in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False


    if 'Item' in intent['slots']:
        item = intent['slots']['Item']['value']
        item_attributes = create_item_attributes(item, intent)
        aisle = item_attributes["aisle"]
        store = item_attributes["store"]

        if aisle == 0:
            speech_output = "Sorry, the" + item + "is not in stock."
        else:
            speech_output = "The " + item + " can be found in aisle " + aisle \
                            + " in " + store
            reprompt_text = "Ask me where an item is by saying, " \
                            "where is the peanut butter."

    else:
        speech_output = "I'm not sure what item you are referencing. " \
                        "Please try again."
        reprompt_text = "I'm not sure what item you are referencing. " \
                        "Ask my where an item is by saying, " \
                        "where is the peanut butter."


    return build_response(item_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# for PriceIntent, returns price to Alexa user
def set_price_in_session(intent, session):
    """ Sets the aisle number in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False


    if 'Item' in intent['slots']:
        item = intent['slots']['Item']['value']
        item_attributes = create_item_attributes(item, intent)
        aisle = item_attributes["aisle"]
        store = item_attributes["store"]
        price = item_attributes["price"]

        if aisle == -1:
            speech_output = "Sorry, the" + item + "is not in stock."
        else:
            speech_output = "The " + item + " costs $" + price \
                            + " at " + store
            reprompt_text = "Ask me how much an item costs by saying, " \
                            "how much is the peanut butter."

    else:
        speech_output = "I'm not sure what item you are referencing. " \
                        "Please try again."
        reprompt_text = "I'm not sure what item you are referencing. " \
                        "Ask my where an item is by saying, " \
                        "where is the peanut butter."


    return build_response(item_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def set_coupon_in_session(intent, session):
    """ Sets the aisle number in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False


    if 'Item' in intent['slots']:
        item = intent['slots']['Item']['value']
        item_attributes = create_item_attributes(item, intent)
        aisle = item_attributes["aisle"]
        store = item_attributes["store"]
        price = item_attributes["price"]
        coupon = item_attributes["coupon"]

        if coupon == 0:
            speech_output = "Sorry, you don't have any coupons for " + item
        else:
            speech_output = "Yes, " + coupon
            reprompt_text = "Ask me if you have any coupons by saying, " \
                            "do I have a coupon for milk."

    else:
        speech_output = "I'm not sure what item you are referencing. " \
                        "Please try again."
        reprompt_text = "I'm not sure what item you are referencing. " \
                        "Ask my where an item is by saying, " \
                        "where is the peanut butter."


    return build_response(item_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# for SaleIntent, returns sale to user
def set_sale_in_session(intent, session):
    """ Sets the aisle number in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False


    if 'Item' in intent['slots']:
        item = intent['slots']['Item']['value']
        item_attributes = create_item_attributes(item, intent)
        aisle = item_attributes["aisle"]
        store = item_attributes["store"]
        price = item_attributes["price"]
        sale = item_attributes["sale"]

        if sale == "":
            speech_output = "Sorry, " + item + " is not on sale."
        else:
            speech_output = "Yes, " + item + " is usually $" + price + ", but now " \
                            "it is on sale for $" + sale
            reprompt_text = "Ask me if you have any coupons by saying, " \
                            "do I have a coupon for milk."

    else:
        speech_output = "I'm not sure what item you are referencing. " \
                        "Please try again."
        reprompt_text = "I'm not sure what item you are referencing. " \
                        "Ask my where an item is by saying, " \
                        "where is the peanut butter."


    return build_response(item_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AisleIntent":
        return set_aisle_in_session(intent, session)
    elif intent_name == "PriceIntent":
        return set_price_in_session(intent, session)
    elif intent_name == "CouponIntent":
        return set_coupon_in_session(intent, session)
    elif intent_name == "SaleIntent":
        return set_sale_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[amzn1.ask.skill.7d0852e1-99e4-4e0d-9eb8-c21d6396331e]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
