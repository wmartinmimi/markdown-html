
with open("test.md", "r") as markdown:
  origin = markdown.read().splitlines()

  with open('test.html', 'w') as html:
    # html basics
    html.write("<!DOCTYPE html>")
    html.write("<html lang=\"en\">")

    # <head>
    html.write("<head>")

    # title
    html.write("<title>")
    has_title = False
    for line in origin:
      if has_title:
        break
      if line.startswith("?title:"):
        line = line.removeprefix("?title:").rstrip(" ")
        html.write(line)
        has_title = True
    
    for line in origin:
      if has_title:
        break
      if line.startswith("#"):
        line = line.removeprefix("#").lstrip(" ").rstrip("#").rstrip(" ")
        html.write(line)
        has_title = True
    
    html.write("</title>")

    html.write("</head>")

    # <body>
    html.write("<body>")
    for line in origin:
      if len(line) == 0:
        continue
      if not line.startswith("?"):

        # parsing headers
        if line.startswith("#"):
          heading_size = 0
          while line.startswith("#"):
            line = line.removeprefix("#")
            heading_size += 1

          line = line.lstrip(" ").rstrip("#").rstrip(" ")
          if heading_size > 0:
            html.write("<h" + str(heading_size) + ">")
            html.write(line)
            html.write("</h" + str(heading_size) + ">")

        # parsing plain text
        else:
          html.write("<p>" + line + "</p>")
          
    html.write("</body>")

    # html basics
    html.write("</html>")