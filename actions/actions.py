# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.forms import SlotSet

import re
from datetime import datetime

from actions.utils.WikipediaActions import search_wikipedia
from actions.utils.WeatherActions import search_weather


class ActionWikipediaForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_wikipedia_form"

    def extract_wikipedia_search(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        # Check if the input from the user has ""
        message: str = tracker.latest_message.get("text")
        message_parts = message.split("\"")

        if len(message_parts) == 3:
            wikipedia_search = message_parts[1]
            print(wikipedia_search)
            return {"wikipedia_search": wikipedia_search}

        wikipedia_search = tracker.get_slot("wikipedia_search")
        return {"wikipedia_search": wikipedia_search}

    def validate_wikipedia_search(
        self,
        wikipedia_search: str,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None}

        if wikipedia_search is not None:
            return {"wikipedia_search": wikipedia_search}
        return {"wikipedia_search": None}


class ActionSearchWikipedia(Action):

    def name(self) -> Text:
        return "action_search_wikipedia"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        wikipedia_search = tracker.get_slot("wikipedia_search")

        if wikipedia_search == None:
            dispatcher.utter_message(text="Ok, let's go back to the beginning!")
        else:
            # Make a search on Wikipedia
            result = search_wikipedia(wikipedia_search)
            if result == None:
                dispatcher.utter_message(text="Sorry, I couldn't sort out that information")
            else:
                dispatcher.utter_message(text=result)
                dispatcher.utter_message(text="Was that helpful?",
                                         buttons=[
                                             {"title": "Yes", "payload": "/affirm"},
                                             {"title": "Not at all", "payload": "/deny"}
                                         ])
            return [SlotSet("wikipedia_search", None)]


class ActionWeatherForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_weather_form"

    def extract_weather_location(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:
        # Check latest message
        message = tracker.latest_message.get("text")
        message_parts = message.split("\"")
        if len(message_parts) == 3:
            return {"weather_location": message_parts[1]}

        weather_location = tracker.get_slot("weather_location")
        if type(weather_location) is list:
            return {"weather_location": weather_location[0]}
        return {"weather_location": weather_location}

    def validate_weather_location(
        self,
        weather_location: str,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None}

        if weather_location is not None:
            return {"weather_location": weather_location}


class ActionAskWeather(Action):

    def name(self) -> Text:
        return "action_ask_weather"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        weather_location: str = tracker.get_slot("weather_location")
        weather_location = weather_location.capitalize()

        if weather_location is None:
            dispatcher.utter_message("Ok, let's go back to the beginning")
        else:
            result = search_weather(weather_location)
            if result == None:
                dispatcher.utter_message("Sorry, I couldn't sort out that information")
            else:
                dispatcher.utter_message(result)
            return [SlotSet("weather_location", None)]


class ActionPhoneNumberForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_phone_number_form"

    def extract_phone_number(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        phone_number = tracker.get_slot("phone_number")
        if phone_number is not None:
            return {"phone_number": str(phone_number)}
        else:
            return {"phone_number": None}

    def validate_phone_number(
        self,
        phone_number: str,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None}

        if phone_number is not None:
            return {"phone_number": phone_number}


class ActionCallPhone(Action):

    def name(self) -> Text:
        return "action_call_phone"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        phone_number = tracker.get_slot("phone_number")
        if phone_number is None:
            dispatcher.utter_message("Okay, let's go back to the beginning")
        else:
            dispatcher.utter_message(text=f"Okay, calling {phone_number}...",
                                     json_message={
                                         "intent": "call",
                                         "telephone": phone_number
                                     })
            return [SlotSet("phone_number", None)]


class ActionEmailForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_email_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:

        email_address = tracker.get_slot("email_address")
        email_subject = tracker.get_slot("email_subject")
        email_continue_body = tracker.get_slot("email_continue_body")
        email_body = tracker.get_slot("email_body")

        if email_address and email_subject is not None:
            if email_body is None and email_continue_body is None:
                # The bot is going to ask about the body
                return ["email_continue_body"] + slots_mapped_in_domain
            if email_body is None and email_continue_body is True:
                return ["email_body"] + slots_mapped_in_domain

        return slots_mapped_in_domain

    def extract_email_continue_body(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        intent = tracker.get_intent_of_latest_message()

        if intent == "affirm":
            return {"email_continue_body": True}
        if intent == "deny":
            return {"email_continue_body": False}
        return {"email_continue_body": None}

    def extract_email_address(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        email_address = tracker.get_slot("email_address")

        if tracker.get_intent_of_latest_message() == "email":
            message = tracker.latest_message.get("text")

            position = 0
            position_subject = 0
            position_body = 0
            body_out = False
            subject_out = False
            subject = None
            body = None

            list_email = re.findall(r"\"(.*?)\"", message)

            for word in message.split(" "):
                if word == "subject":
                    if not subject_out:
                        subject_out = True
                        position_subject = position
                        subject = list_email[position_subject]
                        position += 1
                if word == "body":
                    if not body_out:
                        body_out = True
                        position_body = position
                        body = list_email[position_body]
                        position += 1

            return {"email_address": email_address, "email_subject": subject, "email_body": body}

    def extract_email_body(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        message = tracker.latest_message.get("text")
        return {"email_body": message}


class ActionEmail(Action):

    def name(self) -> Text:
        return "action_email"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        email_address = tracker.get_slot("email_address")
        email_subject = tracker.get_slot("email_subject")

        sentence = f"Ok. Sending an email to {email_address} with the subject \"{email_subject}\""

        email_body = tracker.get_slot("email_body")
        if email_body is not None:
            sentence += f" with the body \"{email_body}\""
        else:
            sentence += f" with no body attached"

        dispatcher.utter_message(sentence,
                                 json_message={
                                     "intent": "email",
                                     "emailAddress": email_address,
                                     "emailSubject": email_subject,
                                     "emailBody": email_body
                                 })
        return [SlotSet("email_address", None), SlotSet("email_subject", None), SlotSet("email_body", None), SlotSet("email_continue_body", None)]


class ActionAlarmForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_alarm_form"

    def extract_alarm_time(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        alarm_time = tracker.get_slot("alarm_time")

        if type(alarm_time) is dict:
            return {"alarm_time": None}

        return {"alarm_time": alarm_time}

    def validate_alarm_time(
        self,
        alarm_time: str,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None}

        return {"alarm_time": alarm_time}


class ActionAlarm(Action):

    def name(self) -> Text:
        return "action_alarm"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        alarm_time = tracker.get_slot("alarm_time")
        if alarm_time is None:
            dispatcher.utter_message("Okay, let's go back to the beginning")
        else:
            d1 = datetime.strptime(alarm_time, "%Y-%m-%dT%H:%M:%S.%f%z")
            new_alarm_time = d1.strftime("%d-%m-%Y %H:%M:%S")
            dispatcher.utter_message(text="Ok, setting the alarm at that hour...",
                                     json_message={
                                         "intent": "alarm",
                                         "alarmTime": new_alarm_time
                                     })
            return [SlotSet("alarm_time", None)]