#!/usr/bin/python
"""
This script generates the fastest possible C code for the following
function: given a string, see if it belongs to a known set of strings.
If it does, return an enum corresponding to that string.
It can be thought of as internalizing a string.

TODO: this is not actually the fastest possible implementation.
Assuming our set of known strings is "a", "abba2", "bo", the fastest
possible implementation would be along the lines:

int FindTag(char *s, size_t len)
{
    char c = *s++; --len;
    if (c == 'a') {
        if (0 == len) return Tag_A;
        if ((len == 4) && memeq(s, "bba2", 4)) return Tag_Abba2;
    } else if (c == 'b') {
        if ((len == 1) && (*s == 'o')) return Tag_Bo;
    }
    return Tag_NotFound;
}

or:

uint32_t GetUpToFour(char*& s, size_t& len)
{
    CrashIf(0 == len);
    size_t n = 0;
    uint32_t v = *s++; len--;
    while ((n < 3) && (len > 0)) {
        v = v << 8;
        v = v | *s++;
        len--; n++;
    }
    return v;
}

#define V_A 'a'
#define V_BO  (('b' << 8) | 'o'))
#define V_ABBA ...
#define V_2 ...

int FindTag(char *s, size_t len)
{
    uint32_t v = GetUpToFour(s, len);
    if (v == V_A) return Tag_A;
    if (v == V_BO) return Tag_B;
    if (v == V_ABBA) {
        v = GetUpToFour(s, len);
        if (v == V_2) return Tag_Abba2;
     }
     return Tag_NotFound;
}

This code generator isn't smart enough to generate such code yet.
"""

import string

# first letter upper case, rest lower case
def capitalize(s):
    s = s.lower()
    return s[0].upper() + s[1:]

# This list has been generated by instrumenting MobiHtmlParse.cpp
# to dump all tags we see in a mobi file
g_tags_str = "a b blockquote body br div font guide h2 head html i img li mbp:pagebreak ol p reference span sup table td tr u ul"
g_attrs_str = "width align height"
g_align_attr_str = "left right center justify"

find_simple_c = """
// enums must match gTags order
enum HtmlTag {
    %s
};

// enums must match gAttrs order
enum HtmlAttr {
    %s
};

// enums must match gAlignAttrs order
enum AlignAttr {
    %s
};

// strings is an array of 0-separated strings consequitevely laid out
// in memory. This functions find the position of str in this array,
// -1 means not found. The search is case-insensitive
static int FindStrPos(const char *strings, char *str, size_t len)
{
    const char *curr = strings;
    char *end = str + len;
    char firstChar = tolower(*str);
    int n = 0;
    for (;;) {
        // we're at the start of the next tag
        char c = *curr;
        if ((0 == c) || (c > firstChar)) {
            // strings are sorted alphabetically, so we
            // can quit if current str is > tastringg
            return -1;
        }
        char *s = str;
        while (*curr && (s < end)) {
            char c = tolower(*s++);
            if (c != *curr++)
                goto Next;
        }
        if ((s == end) && (0 == *curr))
            return n;
Next:
        while (*curr) {
            ++curr;
        }
        ++curr;
        ++n;
    }
    return -1;
}

const char *gTags = "%s";
HtmlTag FindTag(char *tag, size_t len)
{
    return (HtmlTag)FindStrPos(gTags, tag, len);
}

const char *gAttrs = "%s";
static HtmlAttr FindAttr(char *attr, size_t len)
{
    return (HtmlAttr)FindStrPos(gAttrs, attr, len);
}

const char *gAlignAttrs = "%s";
static AlignAttr FindAlignAttr(char *attr, size_t len)
{
    return (AlignAttr)FindStrPos(gAlignAttrs, attr, len);
}
"""

# given e.g. "br", returns "Tag_Br"
def enum_name_from_name(name, prefix):
    parts = name.split(":")
    parts = [capitalize(p) for p in parts]
    parts = [prefix] + parts
    return string.join(parts, "_")

def gen_enum_str_list(strings, prefix):
    strings = [t.lower() for t in strings.split(" ")]
    strings.sort()
    strings.append("last")
    strings_c = string.join(strings, "\\0") + "\\0"
    # el[0] is tag, el[1] is 0-based position of the tag
    enums = [(enum_name_from_name(el[0], prefix), el[1]) for el in zip(strings, range(len(strings)))]
    enums = [(prefix + "_NotFound", -1)] + enums
    enum_strings = ["%s = %d" % t for t in enums]
    enums_string = string.join(enum_strings, ",\n    ")
    return (enums_string, strings_c)

def main():
    (tags_enum_str, gTags_str) = gen_enum_str_list(g_tags_str, "Tag")
    (attrs_enum_str, gAttr_str) = gen_enum_str_list(g_attrs_str, "Attr")
    (align_attrs_enum_str, gAttr_str) = gen_enum_str_list(g_align_attr_str, "Align")

    print(find_simple_c % (tags_enum_str, attrs_enum_str, align_attrs_enum_str, gTags_str, gAttr_str, gAttr_str))
    #print(tags_str)

if __name__ == "__main__":
    main()