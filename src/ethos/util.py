# https://siongui.github.io/2012/10/11/python-parse-accept-language-in-http-request-header/
def parseAcceptLanguage(acceptLanguage):
  languages = acceptLanguage.split(",")
  locale_q_pairs = []

  for language in languages:
    if language.split(";")[0] == language:
      # no q => q = 1
      locale_q_pairs.append((language.strip(), "1"))
    else:
      locale = language.split(";")[0].strip()
      q = language.split(";")[1].split("=")[1]
      locale_q_pairs.append((locale, q))

  return locale_q_pairs
