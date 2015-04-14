from functools import partial

MISSING_ERROR = 'Configuration must include key "{0}"'
TYPE_ERROR = 'Value for key "{0}" should have type {1} but has type {2}.'

class ValidError(Error):
   pass 

# Raises ValidError if actual is not greater than min.
def greaterThanEqual(min, actual):
   if actual < min:
      raise ValidError

checks = {
   'show': (int, [partial(greaterThanEqual, 0)]),
   'shuffle': (bool, []),
   'strip_path': (str, []),
   'resource_path': (str, [])
}

def validate(config):
   errors = []
   for key in checks:
      if key not in config:
         errors.push(MISSING_ERROR.format(key))
      else:
         actual = config[key].__name__
         expected = checks[key][0].__name__
         if actual != expected:
            errors.append(TYPE_ERROR.format(key, expected, actual))
         for fn in checks[key][0]:
            try:
               fn(config[key])
            except ValidError as e:
               errors.append(str(e))
   return errors
