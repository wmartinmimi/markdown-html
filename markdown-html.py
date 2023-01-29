import os

# a parser for easier parsing operations
class Parser():

    def __init__(self, s):
        # the string to parse
        self.s = s
        # the current character index in string
        self.i = -1
        # checkpoints for reverting
        self.checkpoints = []

    # add a checkpoint (stores current index location)
    # if rebase, remove checkpoint
    # if rollback, jump back to checkpoint
    def checkpoint(self):
        self.checkpoints.insert(0, self.i)

    # jump back to previous checkpoint
    def rollback(self):
        self.i = self.checkpoints[0]
        self.rebase()

    # remove previous checkpoint
    def rebase(self):
        self.checkpoints = self.checkpoints[1: len(self.checkpoints)]

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

    html_name = path[0:path.rfind(".")] + '.html'

    with open(html_name, 'w') as html:
        # html basics
        html.write("<!DOCTYPE html>")
        html.write("<html lang=\"en\">")

        # <head>
        html.write("<head>")

        # responsive design
        html.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")

        # <style>
        html.write("<style>")
        html.write(":root {")
        html.write("--background-color: #F0F0F0;")
        html.write("--text-color: #333333;")
        html.write("}")
        html.write("@media (prefers-color-scheme: dark) {")
        html.write(":root {")
        html.write("--background-color: #181819;")
        html.write("--text-color: #b0b0b0;")
        html.write("}")
        html.write("}")
        html.write("* {")
        html.write("font-family: Helvetica, Verdana, Arial, sans-serif;")
        html.write("letter-spacing: 0.02em;")
        html.write("}")
        html.write("body {")
        html.write("background-color: var(--background-color);")
        html.write("color: var(--text-color);")
        html.write("}")
        html.write("a {")
        html.write("text-decoration: none;")
        html.write("color: rgb(0, 125, 151);")
        html.write("}")
        html.write("a:visited {")
        html.write("color: rgb(125, 49, 134);")
        html.write("}")
        html.write("</style>")
        # title
        html.write("<title>")
        has_title = False
        for line in origin.splitlines():
            if has_title:
                break
            if line.startswith("?title:"):
                line = line.removeprefix("?title:").strip(" ")
                html.write(line)
                has_title = True

        for line in origin.splitlines():
            if has_title:
                break
            if line.startswith("#"):
                line = line.strip(" ").strip("#").strip(" ")
                html.write(line)
                has_title = True

        html.write("</title>")

        html.write("</head>")

        # <body>
        html.write("<body>")

        parser = Parser(origin)
        is_paragraph = False

        while parser.has_next():
            char = parser.next()

            # not sure if this is needed or not
            if char == "\r" and parser.peek(1) == "\n":
                parser.next()

            if char == "\n" or parser.i == 0:
                parser.checkpoint()
                if not parser.has_next():
                    break

                # for non-first chars
                if not parser.i == 0:
                    char = parser.next()

                # for special hooks
                if char == "?":
                    parser.until("\n")
                    parser.rebase()

                # parsing headers
                elif char == "#":
                    heading_size = len(parser.when("#")) + 1

                    line = parser.until("\n").strip(" ").rstrip('#').rstrip(" ")

                    html.write("<h" + str(heading_size) + ">")
                    html.write(line)
                    html.write("</h" + str(heading_size) + ">")
                    parser.rebase()

                elif char == "-":

                    parser.checkpoint()
                    parser.when("-")

                    if parser.peek(1) == "\n":
                        html.write("<hr/>")
                        parser.rebase()
                        continue

                    parser.rollback()

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

                        parser.checkpoint()
                        if parser.peek(1) != "-" or level > 0:
                            this_indention = 0
                            this_indention += len(parser.when(" "))
                            char = parser.current()
                            if this_indention > indention and char == "-":
                                indention = this_indention
                                html.write("<ul>")
                                level += 1
                                parser.rebase()
                                continue

                            elif this_indention < indention and char == "-":
                                indention = this_indention
                                html.write("</ul>")
                                level -= 1
                                parser.rebase()
                                continue

                            elif char == "-":
                                parser.rebase()
                                continue

                            parser.rollback()
                            break
                        
                        parser.rollback()
                        parser.next()

                    html.write("</ul>")
                    parser.rebase()
                    continue

                # for empty lines
                elif char == "\n":
                    if is_paragraph:
                        html.write("</p>")
                        is_paragraph = False
                    parser.rebase()
                    parser.jump(-1)
                    continue

                else:
                    parser.rollback()
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
        html.write("</body>")

        # html basics
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
