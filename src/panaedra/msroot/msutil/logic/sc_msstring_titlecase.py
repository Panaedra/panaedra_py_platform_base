#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Original Perl version by: _PPL_UNDISCLOSED_ _PPL_UNDISCLOSED_ http://daringfireball.net/ 10 May 2008
Python version by _PPL_UNDISCLOSED_ Colville http://muffinresearch.co.uk
License: http://www.opensource.org/licenses/mit-license.php

Based on pip version on titlecase, 0.8.0. Added custom logic for (a.o.) non-english text (french,dutch,spanish).
"""

import re

__all__ = ['titlecaser']
__version__ = '0.8.0.1'

SMALL = 'a|an|and|as|at|but|by|de|den|des|en|een|es|for|het|if|in|l|la|le|les|of|on|or|the|to|un|une|v\.?|via|vs\.?' # [codeQok#7104]
PUNCT = r"""!"#$%&'‘()*+,\-./:;?@[\\\]_`{|}~"""

SMALL_WORDS = re.compile(r'^(%s)$' % SMALL, re.I)
INLINE_PERIOD = re.compile(r'[a-z][.][a-z]', re.I)
UC_ELSEWHERE = re.compile(r'[%s]*?[a-zA-Z]+[A-Z]+?' % PUNCT)
CAPFIRST = re.compile(r"^[%s]*?([\S])" % PUNCT) # Note unicode characters like accented lowercase latin 'e'... so don't use a-zA-Z
SMALL_FIRST = re.compile(r'^([%s]*)(%s)\b' % (PUNCT, SMALL), re.I)
SMALL_LAST = re.compile(r'\b(%s)[%s]?$' % (SMALL, PUNCT), re.I)
SUBPHRASE = re.compile(r'([:.;?!][ ])(%s)' % SMALL)
APOS_SECOND = re.compile(r"^[dol]{1}['â€˜]{1}[a-z]+(?:['s]{2})?$", re.I)
ALL_CAPS = re.compile(r'^[A-Z\s\d%s]+$' % PUNCT)
UC_INITIALS = re.compile(r"^(?:[A-Z]{1}\.{1}|[A-Z]{1}\.{1}[A-Z]{1})+$")
MAC_MC = re.compile(r"^([Mm]c)(\w.+)")

def set_small_word_list(small=SMALL):
  global SMALL_WORDS
  global SMALL_FIRST
  global SMALL_LAST
  global SUBPHRASE
  SMALL_WORDS = re.compile(r'^(%s)$' % small, re.I)
  SMALL_FIRST = re.compile(r'^([%s]*)(%s)\b' % (PUNCT, small), re.I)
  SMALL_LAST = re.compile(r'\b(%s)[%s]?$' % (small, PUNCT), re.I)
  SUBPHRASE = re.compile(r'([:.;?!][ ])(%s)' % small)


def titlecaser(text, callback=None):
  """
  Titlecases input text

  This filter changes all words to Title Caps, and attempts to be clever
  about *un*capitalizing SMALL words like a/an/the in the input.

  The list of "SMALL words" which are not capped comes from
  the New York Times Manual of Style, plus 'vs' and 'v'.

  """

  lines = re.split('[\r\n]+', text)
  processed = []
  for line in lines:
    all_caps = ALL_CAPS.match(line)
    words = re.split('[\t ]', line)
    tc_line = []
    for word in words:
      if callback:
        new_word = callback(word, all_caps=all_caps)
        if new_word:
          tc_line.append(new_word)
          continue

      if all_caps:
        if UC_INITIALS.match(word):
          tc_line.append(word)
          continue

      if "'" in word:
        stword=word.split("'")
        if len(stword) == 2 and len(stword[1]) > 1:
          strophed = map(lambda t: titlecaser(t,callback), word.split("'"))
          tc_line.append("'".join(strophed))
          continue
      
      if APOS_SECOND.match(word):
        if len(word[0]) == 1 and word[0] not in 'aeiouAEIOU':
          word = word[0].lower() + word[1] + word[2].upper() + word[3:]
        else:
          word = word[0].upper() + word[1] + word[2].upper() + word[3:]
        tc_line.append(word)
        continue
      
      if INLINE_PERIOD.search(word) or (not all_caps and UC_ELSEWHERE.match(word)):
        tc_line.append(word)
        continue
      if SMALL_WORDS.match(word):
        tc_line.append(word.lower())
        continue

      match = MAC_MC.match(word)
      if match:
        tc_line.append("%s%s" % (match.group(1).capitalize(),
                                 match.group(2).capitalize()))
        continue

      if "/" in word and "//" not in word:
        slashed = map(lambda t: titlecaser(t,callback), word.split('/'))
        tc_line.append("/".join(slashed))
        continue

      if '-' in word:
        hyphenated = map(lambda t: titlecaser(t,callback), word.split('-'))
        tc_line.append("-".join(hyphenated))
        continue

      if all_caps:
        word = word.lower()

      # Just a normal word that needs to be capitalized
      tc_line.append(CAPFIRST.sub(lambda m: m.group(0).upper(), word))

    result = " ".join(tc_line)

    result = SMALL_FIRST.sub(lambda m: '%s%s' % (
        m.group(1),
        m.group(2).capitalize()
    ), result)

    result = SMALL_LAST.sub(lambda m: m.group(0).capitalize(), result)

    result = SUBPHRASE.sub(lambda m: '%s%s' % (
        m.group(1),
        m.group(2).capitalize()
    ), result)

    processed.append(result)

  return "\n".join(processed)

#EOF
