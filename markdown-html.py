import os

# extract string from index "start" to character "trim_char"
def trimTo(origin, start, trim_char):
  i = start
  char = origin[i]
  while char != trim_char:
    i += 1
    char = origin[i]

  return origin[start + 1:i]
  
def newI(i, line):
  return i + len(line) + 1

# open markdown file for converting to html
def openMarkDown(path):
  origin = None
  with open(path, "r") as markdown:
    origin = markdown.read()

  if origin == None:
    print("Cannot open: " + path)
    return

  html_name = path[::-1][path[::-1].find(".") + 1:len(path[::-1])][::-1] + ".html"

  with open(html_name, 'w') as html:
    # html basics
    html.write("<!DOCTYPE html>")
    html.write("<html lang=\"en\">")

    # <head>
    html.write("<head>")

    # <style>
    html.write("<style>")
    html.write(":root {")
    html.write("--background-color: #F0F0F0;")
    html.write("--text-color: #333333;")
    html.write("--link-color: rgb(0, 125, 151);")
    html.write("--visited-link-color: rgb(125, 49, 134);")
    html.write("}")
    html.write("@media (prefers-color-scheme: dark) {")
    html.write(":root {")
    html.write("--background-color: #0d1717;")
    html.write("--text-color: #b1b1b1;")
    html.write("--link-color: rgb(10, 77, 108);")
    html.write("--visited-link-color: rgb(86, 10, 95);")
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
    html.write("color: var(--link-color)")
    html.write("}")
    html.write("a:visited {")
    html.write("color: var(--visited-link-color);")
    html.write("}")
    html.write("</style>")
    # title
    html.write("<title>")
    has_title = False
    for line in origin.splitlines():
      if has_title:
        break
      if line.startswith("?title:"):
        line = line.removeprefix("?title:").rstrip(" ")
        html.write(line)
        has_title = True
    
    for line in origin.splitlines():
      if has_title:
        break
      if line.startswith("#"):
        line = line.strip("#").strip(" ")
        html.write(line)
        has_title = True
    
    html.write("</title>")

    html.write("</head>")

    # <body>
    html.write("<body>")

    i = 0
    size = len(origin)
    is_paragraph = False

    while i < size:
      char = origin[i]
      if char == "\n" or i == 0:

        if i + 1 >= size:
          break

        # for first chars
        if not i == 0:
          i += 1
          char = origin[i]

        # for special hooks
        if char == "?":
          line = trimTo(origin, i, "\n")
          i = newI(i, line)

        # parsing headers
        elif char == "#":
          heading_size = 0
          while char == "#":
            i += 1
            char = origin[i]
            heading_size += 1

          line = trimTo(origin, i, "\n")
          i = newI(i, line)

          line = line.lstrip(" ").rstrip("#").rstrip(" ")
          if heading_size > 0:
            html.write("<h" + str(heading_size) + ">")
            html.write(line)
            html.write("</h" + str(heading_size) + ">")

        elif char == "-":

          # horizontal line
          t = i
          while char == "-":
            t += 1
            char = origin[t]

          if origin[t + 1] == "\n":
            i = t
            html.write("<hr/>")
            continue

          # unordered list
          html.write("<ul>")
          
          indention = 0
          level = 0
          while True:
            html.write("<li>")

            line = trimTo(origin, i, "\n")
            i = newI(i, line)

            html.write(line.strip(" "))

            html.write("</li>")


            if len(origin) <= i + 1:
              while level > 0:
                level -= 1
                html.write("</ul>")
              break

            if origin[i + 1] != "-" or level > 0:
              this_indention = 0
              t = i + 1
              char = origin[t]
              while len(origin) > t and char == " ":
                this_indention += 1
                t += 1
                char = origin[t]

              if this_indention > indention and origin[t] == "-":
                indention = this_indention
                html.write("<ul>")
                i = t
                level += 1
                continue
              
              elif this_indention < indention and origin[t] == "-":
                indention = this_indention
                html.write("</ul>")
                i = t
                level -= 1
                continue

              elif origin[t] == "-":
                i = t
                continue

              break

            i += 1
          
          html.write("</ul>")
          continue
            

        # for empty lines
        elif char == "\n":
          if is_paragraph:
            html.write("</p>")
            is_paragraph = False
          continue
        
        else:
          i -= 1
        i += 1
        continue

      if not is_paragraph:
        html.write("<p>")
        is_paragraph = True

      elif origin[i - 1] == "\n":
        html.write(" ")

      # parsing links
      if char == "[":

        link_name = trimTo(origin, i, "]")
        i = newI(i, link_name)

        char = origin[i]

        while not char == "(":
          i += 1
          char = origin[i]

        link = trimTo(origin, i, ")")
        i = newI(i, link)
          
        html.write("<a href=\"" + link.strip(" ") + "\">")
        html.write(link_name)
        html.write("</a>")

      # img
      elif char == "!" and origin[i + 1] == "[":
        i += 1
        char = origin[i]

        img_name = trimTo(origin, i, "]")
        i = newI(i, img_name)

        char = origin[i]

        while not char == "(":
          i += 1
          char = origin[i]

        img_link = trimTo(origin, i, ")")
        i = newI(i, img_link)
          
        html.write("<img src=\"" + img_link.strip(" ") + "\"")
        html.write(" alt=\"" + img_name + "\" />")

      # parsing plain text
      else:
        html.write(char)
      
      i += 1
          
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

openRoot(os.getcwd())
