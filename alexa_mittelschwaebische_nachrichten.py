from __future__ import print_function
import json
import urllib
import re
from dateutil.parser import parse
import locale

print('Loading function')

items = []

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    outputNew = '<speak>' + output + '</speak>'
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
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



def on_launch(request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    if (len(items) == 0):
        on_session_started()
    session_attributes = {}
    card_title = "Willkommen"
    speech_output = "Willkommen bei Mittelschwäbische Nachrichten - Es gibt " + str(len(items)) + " neue Nachrichten."
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Soll ich dir aktuelle Nachrichten vorlesen?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def on_session_started():
    with urllib.request.urlopen('http://www.augsburger-allgemeine.de/krumbach/rss') as response:
        page = response.read().decode('utf-8')
        items.extend(re.findall('<item>(.*?)</item>', page, re.S))


def on_intent(request, session):
    if (len(items) == 0):
        on_session_started()
        
    speech_output = ""
    
    if (request['intent']['name'] == 'Ueberschriften'):
        headlines = get_headlines()
        speech_output = '<p>Hier die Überschriften der aktuellen Nachrichten</p> {}'.format(headlines)
    if (request['intent']['name'] == 'Detail'):
        slotvalue = request['intent']['slots']['ArtikelNummer']['value']
        if (slotvalue == '?'):
            speech_output = "<p>Ich habe leider nicht verstanden, welcher Artikel vorgelesen werden soll. Sag bitte die Nummer dazu.</p>"
        else:
            speech_output = get_details(slotvalue)
            
    
    session_attributes = {}
    
    card_title = "Aktuelle Lokalnachrichten"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))

def get_details(artNum):
    item = items[int(artNum)-1]
    title = re.search('<title>(.*?)</title>', item, re.S).group(1).strip()
    titleNew = re.sub('^(.*?)\:', '<s>\\1</s>',title)
    
    #<pubDate>	Sun, 11 Jun 2017 07:25:00 GMT</pubDate>
    pubDate = re.search('<pubDate>(.*?)</pubDate>', item, re.S).group(1).strip() 
    dt = parse(pubDate)
    dateString = dt.strftime('????%m%d')
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

    weekDay = dt.strftime('%A')
    

    description = re.search('<description>(.*?)</description>', item, re.S).group(1).strip()
    articleString = '<p>Hier Artikel ' + str(artNum) + '</p> vom ' + weekDay + ', <say-as interpret-as="date">' + dateString + '</say-as><p>' + titleNew + '</p>' + '<p>' + description + '</p>'
    return articleString

def get_headlines():
    titles = [re.search('<title>(.*?)</title>', item, re.S).group(1).strip() for item in items]
    titleString = ""
    i = 1
    for title in titles:
        titleNew = re.sub('^(.*?)\:', '<s>\\1</s>',title)
        titleString = titleString + '<p><say-as interpret-as="ordinal">' + str(i) + '</say-as>. ' +  titleNew + '</p>'
        i+=1
    
    return titleString
    
    
# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    
    if event['session']['new']:
        on_session_started()
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
