from padatious.util import tokenize, expand_parentheses, remove_comments


def expand_options(sentece):
    sentences = []
    sentece = sentece.replace("[", "(").replace("]", "| )")
    for exp in expand_parentheses(tokenize(sentece)):
        sentences.append(" ".join(exp).replace("(", "[").replace(")", "]"))
    return sentences


def expand_keywords(sentece):
    kwords = {"required": [], "optional": []}

    in_optional = False
    for exp in expand_parentheses(tokenize(sentece)):
        if "[" in exp:
            in_optional = True
            required = exp[:exp.index("[")]
            kwords["required"].append(" ".join(required))
            optional = exp[exp.index("[") + 1:]
            kwords["optional"].append(" ".join(optional).replace("]", "").strip())
        elif in_optional:
            optional = exp
            kwords["optional"].append(" ".join(optional).replace("]", "").strip())
            if "]" in exp:
                in_optional = False
        else:
            kwords["required"].append(" ".join(exp))
    return kwords


if __name__ == "__main__":
    sentences = ['i ( love | like ) mycroft',
                  'mycroft is ( open | free | private )']
   # for s in sentences:
   #     print(expand_options(s))

    sentences += ['what is weather like [ in canada | in france | in portugal ]',
              'how is weather like [ in { location } ]',
              'tell me weather [ at { location } | in { location } ]']
    for s in sentences:
        print(expand_keywords(s))