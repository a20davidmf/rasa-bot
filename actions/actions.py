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

from actions.utils.WikipediaActions import search_wikipedia


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
            if result == "page_not_found":
                dispatcher.utter_message(text="Sorry, I couldn't sort out that information")
            else:
                dispatcher.utter_message(text=result)
                dispatcher.utter_message(text="Was that helpful?",
                                         buttons=[
                                             {"title": "Yes", "payload": "/affirm"},
                                             {"title": "Not at all", "payload": "/deny"}
                                         ])
            return [SlotSet("wikipedia_search", None)]