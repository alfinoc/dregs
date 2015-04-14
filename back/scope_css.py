from BeautifulSoup import BeautifulSoup as bs
import tinycss2

# Returns a pair (style, clean) where 'style' is a list of <style> tag contents
# from given html and 'clean' is the remaining html after all such 'style' tags are
# removed.
def extractStyle(html):
   soup = bs(html)
   sheets = []
   for elt in soup.findAll('style'):
      styles = elt.contents
      if len(styles) > 0:  # Empty <style> tag.
         sheets.append(styles[0])
      elt.decompose()
   return (sheets, soup.prettify())

# Returns a list of unicode rules in given 'css' bytes with each qualified rule
# prefixed by given prefix. Leaves at-rules unchanged.
def prefixed_rule_list(prefix, css):
   def serialize(rule):
      res = rule.serialize()
      if rule.type == 'qualified-rule':
         res = prefix + ' ' + res
      return res
   rules, encoding = tinycss2.parse_stylesheet_bytes(css, skip_whitespace=True)
   return map(serialize, rules)

# Returns a pair (markup, style) where 'style' is a full list of all rules that
# appear anywhere in any strip, and 'markup' is a list of
#    { 'prefix': _, 'markup': _ }
# dicts. Each returned qualified style rule is prefixed with the prefix class
# stored in the corresponding markup object.
def consolidate(strips):
   allStyle = []
   clean = []
   unique = 1
   for strip in strips:
      styles, markup = extractStyle(strip)
      prefix = '.pre' + str(unique)
      clean.append({
         'prefix': prefix,
         'markup': markup
      })
      for sheet in styles:
         for rule in prefixed_rule_list(prefix, str(sheet)):
            allStyle.append(rule)
      unique += 1
   return (clean, allStyle)
