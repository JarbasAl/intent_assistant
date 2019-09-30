# Intent Assistant

write once, use everywhere

## Usage

```python
from pprint import pprint
from intent_assistant import IntentAssistant

ia = IntentAssistant()
ia.load_folder("/home/user/PycharmProjects/intent_assistant/test/intents")

print("\nADAPT:")
pprint(ia.adapt_intents)

print("\nPADATIOUS:")
pprint(ia.padatious_intents)

print("\nFUZZY MATCH:")
pprint(ia.fuzzy_intents)


```

## Output

### ADAPT:

    {'optional_test': [{'entities': [{'name': 'required_kw',
                                      'required': True,
                                      'samples': ['what is weather like',
                                                  'how is weather like',
                                                  'tell me weather']},
                                     {'name': 'optional_kw',
                                      'required': False,
                                      'samples': ['in canada',
                                                  'in france',
                                                  'in portugal']},
                                     {'name': 'location',
                                      'regex': True,
                                      'required': False,
                                      'samples': ['^\\W*how\\W+is\\W+weather\\W+like\\W+in\\W+(?P<location>.*?\\w.*?)\\W*$',
                                                  '^\\W*tell\\W+me\\W+weather\\W+at\\W+(?P<location>.*?\\w.*?)\\W*$',
                                                  '^\\W*tell\\W+me\\W+weather\\W+in\\W+(?P<location>.*?\\w.*?)\\W*$']}],
                        'intent': {'at_least_one': [],
                                   'name': 'optional_test',
                                   'optional': [('optional_kw', 'optional_kw'),
                                                ('location', 'location')],
                                   'requires': [('required_kw', 'required_kw')]}}],
     'parantheses_test': [{'entities': [{'name': 'required_kw',
                                         'required': True,
                                         'samples': ['i like mycroft',
                                                     'i love mycroft',
                                                     'mycroft is open',
                                                     'mycroft is free',
                                                     'mycroft is private']}],
                           'intent': {'at_least_one': [],
                                      'name': 'parantheses_test',
                                      'optional': [],
                                      'requires': [('required_kw',
                                                    'required_kw')]}}],
     'regex_test': [{'entities': [{'name': 'something',
                                   'regex': True,
                                   'required': True,
                                   'samples': ['^\\W*say\\W+(?P<something>.*?\\w.*?)\\W*$',
                                               '^\\W*repeat\\W+(?P<something>.*?\\w.*?)\\W*$',
                                               '^\\W*repeat\\W+(?P<something>.*?\\w.*?)\\W+to\\W+me\\W*$',
                                               '^\\W*say\\W+(?P<something>.*?\\w.*?)\\W+to\\W+me\\W*$']},
                                  {'name': 'regex_helper_kw_0',
                                   'regex': True,
                                   'required': False,
                                   'samples': ['repeat']},
                                  {'name': 'regex_helper_kw_1',
                                   'regex': True,
                                   'required': False,
                                   'samples': ['say']},
                                  {'name': 'regex_helper_kw_2',
                                   'regex': True,
                                   'required': False,
                                   'samples': ['to me']}],
                     'intent': {'at_least_one': [],
                                'name': 'regex_test',
                                'optional': [('regex_helper_kw_0',
                                              'regex_helper_kw_0'),
                                             ('regex_helper_kw_1',
                                              'regex_helper_kw_1'),
                                             ('regex_helper_kw_2',
                                              'regex_helper_kw_2')],
                                'requires': [('something', 'something')]}}],
     'test': [{'entities': [{'name': 'required_kw',
                             'required': True,
                             'samples': ['test sentence',
                                         'another test sentence',
                                         'very simple test sentence',
                                         'this is same test',
                                         'yet another test']}],
               'intent': {'at_least_one': [],
                          'name': 'test',
                          'optional': [],
                          'requires': [('required_kw', 'required_kw')]}}]}
    
### PADATIOUS:

    {'optional_test': [{'entities': [{'location': ['france',
                                                   'portugal',
                                                   'canada',
                                                   'england',
                                                   'italy',
                                                   'china']}],
                        'samples': ['what is weather like in canada',
                                    'what is weather like in france',
                                    'what is weather like in portugal',
                                    'what is weather like',
                                    'how is weather like in { location }',
                                    'how is weather like',
                                    'tell me weather at { location }',
                                    'tell me weather in { location }',
                                    'tell me weather']}],
     'parantheses_test': [{'entities': [],
                           'samples': ['i like mycroft',
                                       'i love mycroft',
                                       'mycroft is open',
                                       'mycroft is free',
                                       'mycroft is private']}],
     'regex_test': [{'entities': [],
                     'samples': ['say { something }',
                                 'repeat { something }',
                                 'repeat { something } to me',
                                 'say { something } to me']}],
     'test': [{'entities': [],
               'samples': ['test sentence',
                           'another test sentence',
                           'very simple test sentence',
                           'this is same test',
                           'yet another test']}]}
    
### FUZZY MATCH:

    {'optional_test': [{'entities': {'location': ['france',
                                                  'portugal',
                                                  'canada',
                                                  'england',
                                                  'italy',
                                                  'china']},
                        'samples': ['tell me weather at *',
                                    'tell me weather in italy',
                                    'how is weather like',
                                    'tell me weather at italy',
                                    'tell me weather at canada',
                                    'tell me weather at england',
                                    'how is weather like in canada',
                                    'tell me weather in england',
                                    'tell me weather in france',
                                    'what is weather like in canada',
                                    'how is weather like in england',
                                    'tell me weather in canada',
                                    'what is weather like in portugal',
                                    'what is weather like in france',
                                    'how is weather like in portugal',
                                    'how is weather like in china',
                                    'tell me weather at portugal',
                                    'what is weather like',
                                    'tell me weather in china',
                                    'tell me weather',
                                    'tell me weather at france',
                                    'tell me weather at china',
                                    'tell me weather in *',
                                    'tell me weather in portugal',
                                    'how is weather like in *',
                                    'how is weather like in france',
                                    'how is weather like in italy']}],
     'parantheses_test': [{'entities': {},
                           'samples': ['mycroft is open',
                                       'mycroft is private',
                                       'i like mycroft',
                                       'mycroft is free',
                                       'i love mycroft']}],
     'regex_test': [{'entities': {},
                     'samples': ['say * to me',
                                 'repeat * to me',
                                 'say *',
                                 'repeat *']}],
     'test': [{'entities': {},
               'samples': ['test sentence',
                           'very simple test sentence',
                           'yet another test',
                           'another test sentence',
                           'this is same test']}]}
