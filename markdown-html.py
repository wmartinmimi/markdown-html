import os

# track the index of the parser
class Tracker():

  def __init__(self, parser):
    self.parser = parser
    self.tracked = []

  # save current index location
  def save(self):
    self.tracked.insert(0, self.parser.i)

  # discard saved index
  def discard(self):
    self.tracked = self.tracked[1: len(self.tracked)]

  # revert current index to saved index
  def revert(self):
    self.parser.i = self.tracked[0]
    self.discard()

# a parser for easier parsing operations
class Parser():

  def __init__(self, s):
    # the string to parse
    self.s = s
    # the current character index in string
    self.i = -1
    self.tracker = Tracker(self)

  # move index by 1 and return the next character
  def next(self):
    self.i += 1
    return self.current()

  # return current character
  def current(self):
    return self.s[self.i]

  # return previous character
  def prev(self):
    if self.i > 0:
      return self.s[self.i - 1]
    else:
      return None

  # check if there are any next character
  def has_next(self):
    return not self.peek(1) == None

  # return everything from index to the provided character
  # new index will be at the character
  def until(self, char):
    start = self.i + 1
    size = len(char)
    while self.has_next():
      if self.next() == char:
        return self.s[start: self.i]
    return None

  # return everything until the character is not the provided one
  # new index will be at the new character
  def when(self, char):
    start = self.i + 1
    size = len(char)
    while self.has_next():
      if not self.next() == char:
        return self.s[start: self.i]
    return None

  # return everything from current index to num ahead
  # does not affect current index
  def peek(self, num):
    if self.i + num >= len(self.s):
      return None
    if num == 1:
      return self.s[self.i + 1]
    return self.s[self.i: self.i + num]

  # change current index by i
  def jump(self, i):
    self.i += i

# open markdown file for converting to html
def openMarkDown(path):
  origin = None
  with open(path, "r") as markdown:
    origin = markdown.read()

  if origin == None:
    print("Cannot open: " + path)
    return

  # easier parsing for later
  origin = "\n" + origin

  html_name = path[0:path.rfind(".")] + '.html'

  with open(html_name, 'w') as html:
    # html basics
    html.write("<!DOCTYPE html>")
    html.write("<html lang=\"en\">")

    # <head>
    html.write("<head>")

    # responsive design
    html.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")

    # styling  
    styles = [
      "<style>",
      ":root {",
      "--background-color: #F0F0F0;",
      "--text-color: #333333;",
      "}",
      "@media (prefers-color-scheme: dark) {",
      ":root {",
      "--background-color: #181819;",
      "--text-color: #b0b0b0;",
      "}",
      "}",
      "* {",
      "font-family: Helvetica, Verdana, Arial, sans-serif;",
      "letter-spacing: 0.02em;",
      "}",
      "body {",
      "background-color: var(--background-color);",
      "color: var(--text-color);",
      "}",
      "a {",
      "text-decoration: none;",
      "color: rgb(0, 125, 151);",
      "}",
      "a:visited {",
      "color: rgb(125, 49, 134);",
      "}",
      "</style>"
    ]
    for style in styles:
      html.write(style)

    # title
    html.write("<title>")

    for line in origin.splitlines():
      if line.startswith("#"):
        line = line.strip(" ").strip("#").strip(" ")
        html.write(line)
        break

    html.write("</title>")
    html.write("</head>")

    # <body>
    html.write("<body>")

    parser = Parser(origin)
    tracker = parser.tracker
    is_paragraph = False

    while parser.has_next():
      char = parser.next()

      # not sure if this is needed or not
      if char == "\r" and parser.peek(1) == "\n":
        parser.next()

      if char == "\n":
        if not parser.has_next():
          break

        # jump forward to check next chars
        char = parser.next()

        # parsing headers
        if char == "#":
          heading_size = len(parser.when("#")) + 1

          line = parser.until("\n").strip(" ").rstrip('#').rstrip(" ")

          html.write("<h" + str(heading_size) + ">")
          html.write(line)
          html.write("</h" + str(heading_size) + ">")
          continue

        if char == "-":

          # --- horizontal line
          tracker.save()
          parser.when("-")

          if parser.peek(1) == "\n":
            html.write("<hr/>")
            tracker.discard()
            continue

          tracker.revert()

          # unordered list
          html.write("<ul>")

          indention = 0
          level = 0
          while True:
            html.write("<li>")

            line = parser.until("\n")

            html.write(line.strip(" "))

            html.write("</li>")

            if len(parser.s[parser.i: len(parser.s)].strip()) == 0:
              while level > 0:
                level -= 1
                html.write("</ul>")
              break

            tracker.save()
            if parser.peek(1) != "-" or level > 0:
              this_indention = 0
              this_indention += len(parser.when(" "))
              char = parser.current()
              if this_indention > indention and char == "-":
                indention = this_indention
                html.write("<ul>")
                level += 1
                tracker.discard()
                continue

              elif this_indention < indention and char == "-":
                indention = this_indention
                html.write("</ul>")
                level -= 1
                tracker.discard()
                continue

              elif char == "-":
                tracker.discard()
                continue

              tracker.revert()
              break

            tracker.revert()
            parser.next()

          html.write("</ul>")
          continue

        # for empty lines
        if char == "\n":
          if is_paragraph:
            html.write("</p>")
            is_paragraph = False
          parser.jump(-1)
          continue

        # jump back revert the jump forward character check
        parser.jump(-1)
        continue

      if not is_paragraph:
        html.write("<p>")
        is_paragraph = True

      elif parser.prev() == "\n":
        html.write(" ")

      # parsing links
      if char == "[":

        # [link name](link url)
        link_name = parser.until("]")
        parser.until("(")
        link = parser.until(")")

        html.write("<a href=\"" + link.strip(" ") + "\">")
        html.write(link_name)
        html.write("</a>")

      # img
      elif char == "!" and parser.peek(1) == "[":

        # ![img name](image link)
        char = parser.next()
        img_name = parser.until("]")
        parser.until("(")
        img_link = parser.until(")")

        html.write("<img src=\"" + img_link.strip(" ") + "\"")
        html.write(" alt=\"" + img_name + "\" />")

      # parsing plain text
      else:
        html.write(char)

    # end paragraph
    if is_paragraph:
      html.write("</p>")
      is_paragraph = False

    # html basics
    html.write("</body>")
    html.write("</html>")


# open directory containing the markdown
def openRoot(root):
  for path, subdirs, files in os.walk(root):
    for name in files:
      if name.endswith(".md"):
        openMarkDown(os.path.join(path, name))
      if name.endswith(".markdown"):
        openMarkDown(os.path.join(path, name))


# open all files from current working directory
openRoot(os.getcwd())
