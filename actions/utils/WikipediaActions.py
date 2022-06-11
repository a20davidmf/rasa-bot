from wikipedia import wikipedia
import random

def search_wikipedia(key):
    auto_suggest = False
    while True:
        try:
            result = wikipedia.summary(title=key, sentences=2, auto_suggest=auto_suggest)
            return result
        except wikipedia.DisambiguationError as disambiguation_error:
            key = random.choice(disambiguation_error.options[0])
        except wikipedia.PageError as page_error:
            if auto_suggest is False:
                auto_suggest = True
            else:
                return None