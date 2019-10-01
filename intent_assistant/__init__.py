from adapt.engine import IntentDeterminationEngine as AdaptEngine
from adapt.intent import Intent as AdaptIntent, IntentBuilder as AdaptBuilder

from padatious import IntentContainer as PadatiousEngine
from padaos import IntentContainer as PadaosEngine

from lingua_franca.parse import normalize

from intent_assistant.utils import tokenize, expand_options, expand_keywords
from intent_assistant.utils.json_helper import merge_dict, invert_dict
from intent_assistant.utils.auto_regex import AutoRegex
from intent_assistant.utils.fuzzy import match_one

from os.path import dirname, expanduser, isdir, isfile, join, basename
from os import listdir


class IntentAssistant:
    GENERIC_STOP_WORDS = ["'", "-", ",", ";", "."]
    ENGLISH_STOP_WORDS = ["the", "a", "an", "is", "in", "s", "of", "on", "at", "for", "to", "me", "that", "very", "i"]
    PORTUGUESE_STOP_WORDS = ["e", "a", "o", "os", "as", "em", "de", "da", "do", "das", "dos"]

    def __init__(self, ignore_erros=False, stop_words=None, normalize=True, lang="en"):
        self._entities = {}
        self._intents = {}
        self._regex = {}
        self.ignore_errors = ignore_erros
        self._stop_words = stop_words
        self._normalize = normalize
        self.lang = lang.lower()

    @property
    def stop_words(self):
        if self._stop_words is None:
            if self.lang.startswith("en"):
                return self.ENGLISH_STOP_WORDS + self.GENERIC_STOP_WORDS
            elif self.lang.startswith("pt"):
                return self.PORTUGUESE_STOP_WORDS + self.GENERIC_STOP_WORDS
            else:
                return self.GENERIC_STOP_WORDS
        return self._stop_words + self.GENERIC_STOP_WORDS

    @property
    def intents(self):
        return self._intents

    @property
    def entities(self):
        return self._entities

    def load_folder(self, path):
        path = expanduser(path)
        if not isinstance(path, str):
            raise ValueError
        if not isdir(path):
            raise NotADirectoryError
        for f in listdir(path):
            if self.ignore_errors:
                self.load_file(join(path, f))
            elif f.endswith(".intent") or f.endswith(".entity") or \
                    f.endswith(".voc") or f.endswith(".rx"):
                self.load_file(join(path, f))
            else:
                print("WARNING: unknown file format, skipping {}".format(path))

    def load_file(self, path):
        path = expanduser(path)
        if not isinstance(path, str):
            raise ValueError
        if isdir(path):
            raise IsADirectoryError
        if not isfile(path):
            raise FileNotFoundError
        if path.endswith(".intent"):
            self.register_intent_file(path)
        elif path.endswith(".entity") or path.endswith(".voc"):
            self.register_entity_file(path)
        elif path.endswith(".rx"):
            self.register_regex_file(path)
        else:
            print("ERROR: unknown file format {}".format(path))
            raise ValueError

    def register_intent(self, name, samples):
        intent = {name: samples}
        merge_dict(self._intents, intent)

    def register_entity(self, name, samples):
        entity = {name: samples}
        merge_dict(self._entities, entity)

    def register_regex(self, name, samples):
        rx = {name: samples}
        merge_dict(self._regex, rx)

    def _load(self, path):
        with open(path) as f:
            samples = f.readlines()
        samples = [s.strip() for s in samples if not s.strip().startswith("#")]  # filter comments
        samples = [s.replace("{{", "{").replace("}}", "}") for s in samples]  # clean double brackets
        samples = [s.replace("(", " ( ").replace(")", " ) ").replace("{", " { ").replace("}", " } ")
                       .replace("|", " | ").replace("]", " ] ").replace("[", " [ ") for s in
                   samples]  # add missing spaces
        samples = [" ".join(s.split()) for s in samples]  # clean extra white spaces
        if self._normalize:
            samples = [normalize(s, self.lang, remove_articles=True) for s in samples]
        return samples

    def register_intent_file(self, path):
        path = expanduser(path)
        if not isinstance(path, str):
            raise ValueError
        if isdir(path):
            raise IsADirectoryError
        if not isfile(path):
            raise FileNotFoundError
        if not path.endswith(".intent"):
            print("ERROR: wrong file format {}".format(path))
            if not self.ignore_errors:
                raise ValueError
        name = basename(path).replace(".intent", "")
        samples = self._load(path)
        self.register_intent(name, samples)

    def register_entity_file(self, path):
        path = expanduser(path)
        if not isinstance(path, str):
            raise ValueError
        if isdir(path):
            raise IsADirectoryError
        if not isfile(path):
            raise FileNotFoundError
        if not path.endswith(".entity") and not path.endswith(".voc"):
            print("ERROR: wrong file format {}".format(path))
            if not self.ignore_errors:
                raise ValueError
        name = basename(path).replace(".entity", "").replace(".voc", "")
        samples = self._load(path)
        self.register_entity(name, samples)

    def register_regex_file(self, path):
        path = expanduser(path)
        if not isinstance(path, str):
            raise ValueError
        if isdir(path):
            raise IsADirectoryError
        if not isfile(path):
            raise FileNotFoundError
        if not path.endswith(".rx"):
            print("ERROR: wrong file format {}".format(path))
            if not self.ignore_errors:
                raise ValueError
        name = basename(path).replace(".rx", "")
        samples = self._load(path)
        self.register_regex(name, samples)

    def deregister_intent(self, name):
        if name not in self._intents:
            raise KeyError
        self._intents.pop(name)

    def deregister_entity(self, name):
        if name not in self._entities:
            raise KeyError
        self._entities.pop(name)

    def deregister_regex(self, name):
        if name not in self._regex:
            raise KeyError
        self._regex.pop(name)

    def _extract_rx_kword(self, sample):

        kwords = {}

        # expand parentheses into multiple samples
        samples = expand_options(sample)

        # create regex for variables - {some var}
        for s in samples:
            if "{" in s:
                s = s.replace("[", "(").replace("]", ")")
                rx = list(AutoRegex.get_expressions(s))
                kws = AutoRegex.get_unique_kwords(s)
                for kw in kws:
                    if kw not in kwords:
                        kwords[kw] = {"name": kw + "_rx",
                                      "samples": [],
                                      "required": True,  # TODO handle optional regex
                                      "type": "regex"}
                    kwords[kw]["samples"] += rx

        return kwords

    def _extract_regex(self, samples):
        kwords = {}
        for s in samples:
            merge_dict(kwords, self._extract_rx_kword(s))

        return kwords

    def samples_to_adapt_keywords(self, samples):
        rx_kw = self._extract_regex(samples)
        keywords = []

        kw = {
            "name": "required_kw",
            "required": True,
            "samples": []
        }
        opt_kw = {
            "name": "optional_kw",
            "required": False,
            "samples": []
        }
        for s in samples:
            parsed = expand_keywords(s)
            kw["samples"] += parsed["required"]
            opt_kw["samples"] += parsed["optional"]

        rx = [r for r in kw["samples"] if "{" in r]
        opt_rx = [r for r in opt_kw["samples"] if "{" in r]
        kw["samples"] = list(set([r for r in kw["samples"] if "{" not in r]))
        opt_kw["samples"] = list(set([r for r in opt_kw["samples"] if "{" not in r]))

        if len(kw["samples"]):
            keywords.append(kw)
        if len(opt_kw["samples"]):
            keywords.append(opt_kw)

        for k in rx_kw:
            kw_name = "{ " + k.replace("_rx", "") + " }"
            for s in opt_rx:
                if kw_name in s:
                    kw = {
                        "name": k,
                        "required": False,
                        "regex": True,
                        "samples": list(set(rx_kw[k]["samples"]))
                    }
                    if kw not in keywords:
                        keywords.append(kw)

            reqs = []
            for s in rx:

                for ka in AutoRegex.extract_adapt_keywords([s]):
                    reqs += [ko for ko in ka]

                if kw_name in s:
                    kw = {
                        "name": k,
                        "required": True,
                        "regex": True,
                        "samples": list(set(rx_kw[k]["samples"]))
                    }
                    if kw not in keywords:
                        keywords.append(kw)
            for idx, kw in enumerate(list(set(reqs))):
                opt_kw = {
                    "name": "regex_helper_kw_" + str(idx),
                    "required": False,
                    "regex": True,
                    "samples": [kw]
                }
                keywords.append(opt_kw)

        return keywords

    @property
    def adapt_intents(self):
        intents = {}

        for intent_name in self.intents:
            intents[intent_name] = []

            keywords = self.samples_to_adapt_keywords(self.intents[intent_name])
            self.strict = True  # TODO WIP
            if self.strict:
                intent = AdaptBuilder(intent_name)
                for kw in keywords:
                    if kw["required"]:
                        intent.require(kw["name"])
                    else:
                        intent.optionally(kw["name"])
                intents[intent_name] += [{
                    "intent": intent.build().__dict__,
                    "entities": keywords
                }]

            else:
                print("WARNING: strict is an experimental setting, heavy WIP")

                required_kws = [k for k in keywords if k["required"] and not k.get("regex")]
                optional_kws = [k for k in keywords if not k["required"] and not k.get("regex")]

                for k in required_kws:
                    for s in k["samples"]:
                        new_required_keywords = []
                        for t in tokenize(s):
                            if t in self.stop_words:
                                continue
                            kw = {
                                "name": t + "_token",
                                "required": True,
                                "samples": [t]
                            }
                            new_required_keywords.append(kw)

                        intent = AdaptBuilder(intent_name)
                        for kw in new_required_keywords:
                            if kw["required"]:
                                intent.require(kw["name"])
                            else:
                                intent.optionally(kw["name"])
                        intents[intent_name] += [{
                            "intent": intent.build().__dict__,
                            "entities": new_required_keywords + optional_kws
                        }]

        return intents

    @property
    def padaos_intents(self):
        intents = {}

        for intent_name in self.intents:
            samples = []
            ents = []
            for sent in self.intents[intent_name]:
                samples += expand_options(sent)
            for ent in AutoRegex.get_unique_kwords(self.intents[intent_name]):
                if self.entities.get(ent):
                    ents.append({ent: self.entities[ent]})
            intents[intent_name] = [{
                "samples": samples,
                "entities": ents
            }]

        return intents

    @property
    def padatious_intents(self):
        return self.padaos_intents

    @property
    def fuzzy_intents(self):
        intents = {}

        for intent_name in self.intents:
            samples = []
            ents = {}
            for sent in self.intents[intent_name]:
                if "{" in sent:
                    for ent in AutoRegex.get_unique_kwords(self.intents[intent_name]):
                        if ent in self.entities:
                            ents[ent] = self.entities[ent]
                            for valid in self.entities.get(ent, []):
                                samples += [s.replace("{ " + ent + " }", valid) for s in expand_options(sent)]
                        samples += [s.replace("{ " + ent + " }", "*") for s in expand_options(sent)]
                else:
                    samples += expand_options(sent)

            intents[intent_name] = [{
                "samples": list(set(samples)),
                "entities": ents
            }]

        return intents

    @property
    def expanded_samples(self):
        intents = {}
        for intent in self.fuzzy_intents:
            samples = self.fuzzy_intents[intent][0]["samples"]
            intents[intent] = [s for s in samples if "*" not in s]
        return intents

    @property
    def test_utterances(self):
        intents = {}
        for intent in self.fuzzy_intents:
            samples = self.fuzzy_intents[intent][0]["samples"]
            intents[intent] = {"must_match": [s for s in samples if "*" not in s],
                               "wildcards": [s for s in samples if "*" in s],
                               "auto_generated": []}
        return intents

    @property
    def generated_wildcards(self):
        intents = {}
        for intent in self.expanded_samples:
            samples = self.expanded_samples[intent]
            wild_cards = []
            for s in samples:
                for ent in self.entities:
                    for token in self.entities[ent]:
                        if token in s:
                            wild_cards.append(s.replace(token, "*"))
            intents[intent] = list(set(wild_cards))
        return intents

    def match_fuzzy(self, sentence):
        scores = {}
        for intent in self.expanded_samples:
            samples = self.expanded_samples[intent]
            sent, score = match_one(sentence, samples)
            scores[intent] = {"best_match": sent, "conf": score, "intent_name": intent}
        return scores

    def fuzzy_best(self, sentence, min_conf=0.4):
        scores = {}
        best_s = 0
        best_intent = None
        for intent in self.expanded_samples:
            samples = self.expanded_samples[intent]
            sent, score = match_one(sentence, samples)
            scores[intent] = {"best_match": sent, "conf": score, "intent_name": intent}
            if score > best_s:
                best_s = score
                best_intent = intent
        return scores[best_intent] if best_s > min_conf else {"best_match": None, "conf": 0, "intent_name": None}


if __name__ == "__main__":
    from pprint import pprint

    i = IntentAssistant()
    i.load_folder("/home/user/PycharmProjects/intent_assistant/test/intents")

    print("\nADAPT:")
    pprint(i.adapt_intents)

    print("\nPADATIOUS:")
    pprint(i.padatious_intents)

    print("\nFUZZY MATCH:")
    pprint(i.fuzzy_intents)
