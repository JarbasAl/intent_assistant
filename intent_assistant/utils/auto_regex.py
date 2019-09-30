import re


class AutoRegex:
    @staticmethod
    def clean_line(line):
        # make lower case
        line = line.lower()
        #
        line = line.replace("[", "(").replace("]", ")")
        # replace double spaces with single space : "  " -> " "
        line = " ".join(line.split())
        # if {{ found replace with single { : {{word}} -> {word}
        line = line.replace("{{", "{").replace("}}", "}")
        # trim spaces inside {}: { word } -> {word}
        line = line.replace("{ ", "{").replace(" }", "}")

        # replace spaces in keyword
        if "{" in line:
            e = 0
            words = []
            while "{" in line[e:len(line)] and e >= 0:
                i = line[e:len(line)].find("{") + e
                e = line[e:len(line)].find("}") + 1 + e
                words.append(line[i:e].lstrip().rstrip())
            for word in words:
                line = line.replace(word, word.replace(" ", "_"))
        return line

    @staticmethod
    def get_expressions(lines):
        if not isinstance(lines, list):
            lines = [lines]
        for line in lines:
            yield AutoRegex.create_regex_pattern(line)

    @staticmethod
    def get_kwords(lines):
        if not isinstance(lines, list):
            lines = [lines]
        for line in lines:
            line = AutoRegex.create_regex_pattern(line)
            # TODO dirty parse, can probably do this in a cleaner way
            yield [k.split(">.*?\w.*?)")[0] for k in line.split("(?P<") if ">.*?\w.*?)" in k]

    @staticmethod
    def get_unique_kwords(lines):
        flatten = lambda l: [item for sublist in l for item in sublist]
        flat_list = flatten(list(AutoRegex.get_kwords(lines)))
        return list(set(flat_list))

    @staticmethod
    def _create_pattern(line):
        for pat, rep in (
                # === Preserve Plain Parentheses ===
                (r'\(([^\|)]*)\)', r'{~(\1)~}'),  # (hi) -> {~(hi)~}

                # === Convert to regex literal ===
                (r'(\W)', r'\\\1'),
                (r' {} '.format, None),  # 'abc' -> ' abc '

                # === Unescape Chars for Convenience ===
                (r'\\ ', r' '),  # "\ " -> " "
                (r'\\{', r'{'),  # \{ -> {
                (r'\\}', r'}'),  # \} -> }
                (r'\\#', r'#'),  # \# -> #

                # === Support Parentheses Expansion ===
                (r'(?<!\\{\\~)\\\(', r'(?:'),  # \( -> (  ignoring  \{\~\(
                (r'\\\)(?!\\~\\})', r')'),  # \) -> )  ignoring  \)\~\}
                (r'\\{\\~\\\(', r'\\('),  # \{\~\( -> \(
                (r'\\\)\\~\\}', r'\\)'),  # \)\~\}  -> \)
                (r'\\\|', r'|'),  # \| -> |

                # === Support Special Symbols ===
                (r'(?<=\s)\\:0(?=\s)', r'\\w+'),
                (r'#', r'\\d'),
                (r'\d', r'\\d'),

                # === Space Word Separations ===
                (r'(?<!\\)(\w)([^\w\s}])', r'\1 \2'),  # a:b -> a :b
                (r'([^\\\w\s{])(\w)', r'\1 \2'),  # a :b -> a : b

                # === Make Symbols Optional ===
                (r'(\\[^\w ])', r'\1?'),

                # === Force 1+ Space Between Words ===
                (r'(?<=(\w|\}))(\\\s|\s)+(?=\S)', r'\\W+'),

                # === Force 0+ Space Between Everything Else ===
                (r'\s+', r'\\W*'),
        ):
            if callable(pat):
                line = pat(line)
            else:
                line = re.sub(pat, rep, line)
        return line

    @staticmethod
    def create_regex_pattern(line):
        line = AutoRegex.clean_line(line)
        line = AutoRegex._create_pattern(line)
        replacements = {}
        for ent_name in set(re.findall(r'{([a-z_:]+)}', line)):
            replacements[ent_name] = r'(?P<{}>.*?\w.*?)'.format(ent_name)

        for key, value in replacements.items():
            line = line.replace('{' + key + '}', value)
        return '^{}$'.format(line)

    @staticmethod
    def extract_adapt_keywords(lines, include_regex=False):
        kwords = []
        regex_kwords = AutoRegex.get_unique_kwords(lines)
        if not len(regex_kwords):
            return [lines]
        for l in lines:
            l = AutoRegex.clean_line(l)
            adapt_kwords = []

            for kw in regex_kwords:
                for chunk in l.split("{"):

                    if "}" in chunk:
                        chunk = chunk.split("}")[-1]

                    if chunk.strip():
                        adapt_kwords += [chunk.strip()]
                    if include_regex and kw in l:
                        adapt_kwords.append(kw)
            kwords.append(set(adapt_kwords))
        return kwords


if __name__ == "__main__":
    lines = [
        "say {{something}}",
        "say {{something}} please",
        "{{user}} is my name"
    ]
    for r in AutoRegex.get_expressions(lines[0]):
        print(r)
    for e in AutoRegex.get_kwords(lines[0]):
        print(e)

    print(AutoRegex.extract_adapt_keywords(lines, include_regex=True))
