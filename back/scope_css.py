from BeautifulSoup import BeautifulSoup as bs
import tinycss2
from htmlentitydefs import entitydefs, codepoint2name

# Returns the HTML entity corresponding to unicode character 'uni'. If 'uni' cannot
# be converted, return ''.
def htmlEntity(uni):
   try:
      return entitydefs[codepoint2name[ord(uni)]]
   except:
      return ''

# Returns a copy of unicode string 'uni' with all non-ascii characters
# escaped to HTML entities.
def escapeUnicode(uni):
   ascii = lambda c : ord(c) < 128
   uni = unicode(uni)
   return ''.join([ c if ascii(c) else htmlEntity(c) for c in uni ])

PREFIX_BASE = '_pre'

# Returns a pair (style, clean) where 'style' is a list of <style> tag contents
# from given html and 'clean' is the remaining html after all such 'style' tags are
# removed.
def extractStyle(html):
   soup = bs(html, smartQuotesTo=None)
   sheets = []
   for elt in soup.findAll('style'):
      styles = elt.contents
      if len(styles) > 0:  # Empty <style> tag.
         sheets.append(styles[0])
      elt.decompose()
   return (sheets, unicode(soup))

# Returns a new prelude with all the tokens from the given prelude, except that
# the tokens representing ".classSelector" are included at the beginning of the
# prelude and after every comma.
def prefixPrelude(classSelector, prelude):
   prefixed = tinycss2.parse_component_value_list('.' + classSelector + ' ')
   dot, identifier, whitespace = prefixed
   # Insert prefix at the beginning of the rule.
   for token in prelude:
      prefixed.append(token)
      if token.type == 'literal' and token.value == ',':
         prefixed.append(whitespace)
         prefixed.append(dot)
         prefixed.append(identifier)
         prefixed.append(whitespace)
   return prefixed

# Returns a list of unicode rules in given 'css' bytes with each qualified rule
# prefixed by given prefix. Leaves at-rules unchanged.
def prefixed_rule_list(prefix, css):
   def serialize(rule):
      if rule.type == 'qualified-rule':
         rule.prelude = prefixPrelude(prefix, rule.prelude)
      return rule.serialize()
   rules, encoding = tinycss2.parse_stylesheet_bytes(css, skip_whitespace=True)
   #print rules[-2].serialize()
   return map(serialize, rules)

# Returns a pair (markup, style) where 'style' is a full list of all rules that
# appear anywhere in any strip, and 'markup' is a list of
#    { 'prefix': _, 'markup': _ }
# dicts. Each returned qualified style rule is prefixed with the prefix class
# stored in the corresponding markup object.
# Iff escapeMarkup is True, converts all non-ascii characters in the markup into
# HTML entities.
def consolidate(strips, escapeMarkup=True):
   allStyle = []
   clean = []
   unique = 1
   for strip in strips:
      styles, markup = extractStyle(strip)
      prefix = PREFIX_BASE + str(unique)
      clean.append({
         'prefix': prefix,
         'markup': escapeUnicode(markup) if escapeMarkup else markup
      })
      for sheet in styles:
         # TODO: Remove this hack by moving to bs4. We compensate for bogus
         # html escaping off CSS.
         sheet = sheet.replace('&gt', '>').replace('&lt', '<').replace('&amp', '&')
         for rule in prefixed_rule_list(prefix, str(sheet)):
            allStyle.append(rule)
      unique += 1
   return (clean, allStyle)
