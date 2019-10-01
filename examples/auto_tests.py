from intent_assistant import IntentAssistant
from pprint import pprint

verbose = False

i = IntentAssistant()
i.load_folder("/home/user/PycharmProjects/intent_assistant/test/weather")

for intent in i.test_utterances:
    for s in i.test_utterances[intent]["must_match"]:
        if verbose:
            print("testing utterance", s)
        assert intent == i.fuzzy_best(s).get("intent_name")

    print(len(i.test_utterances[intent]["must_match"]), "matched", intent, "as expected")

# filtering ambiguous wildcards
# these intents should probably be inspected and manual tests written
ambiguous = []
for intent in i.generated_wildcards:
    for s in i.generated_wildcards[intent]:
        if verbose:
            print("testing wildcard", s)
        # NOTE notice we are using fuzzy match here
        # this means we are testing logic meant to be used in fallback handlers
        # might be good candidate intents for adding more samples to .entity files
        if intent != i.fuzzy_best(s).get("intent_name"):
            if verbose:
                print("WARNING: wild card is ambiguous")
                print("intent:", intent, "wilcard:", s)
                print("matches:", i.fuzzy_best(s))
            if {intent, i.fuzzy_best(s).get("intent_name")} not in ambiguous:
                ambiguous.append({intent, i.fuzzy_best(s).get("intent_name")})


print("\nThe following intents are ambiguous")
pprint(ambiguous)



# OUTPUT
# 108 matched weather_location as expected
# 12 matched weather_tomorrow as expected
# 360 matched weather_location_tomorrow as expected
# 6 matched weather_now as expected
#
# The following intents are ambiguous
# [{'weather_now', 'weather_location'},
#  {'weather_location_tomorrow', 'weather_tomorrow'}]