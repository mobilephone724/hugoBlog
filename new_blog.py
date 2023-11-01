import os
import sys

content_prefix      = "content/"
attachment_prefix   = "static/"
markdown_suffix     = ".md"

def create_new_blog(path, title):
    # must be markdown file
    if path[-3:] != ".md":
        print("not a markdown file")
        exit(-1)

    # must create in content/
    if path[:8] != content_prefix:
        print("must start with " + content_prefix)
        return -1

    # content/database/xxx/
    prefix = path[:path.rfind('/')]

    # validate path
    if not os.path.isdir(prefix):
        print("Path doesn't exist: " + prefix)
        return -1

    # Does the file exist?
    if os.path.isfile(path):
        print("File already exists: " + path)
        return -1

    new_file = open(path, "w")
    new_file.write("---\n")
    new_file.write("title: " + title + "\n")
    new_file.write("math: true\n")
    new_file.write("prev: \n")
    new_file.write("next: \n")
    new_file.write("---\n")
    new_file.close()

    # add the attachment directory
    prefix = prefix[8:] # database/xxx/
    file_name = path[path.rfind('/'):-3]
    print(file_name)
    attachment_path = attachment_prefix + prefix + file_name
    print(attachment_path)
    os.makedirs(attachment_path)

    # add news to homepage(content/_index.md)
    homepage = content_prefix + "_index.md"
    print(homepage)
    homepage_data = open(homepage).read().splitlines()
    print(homepage_data[-1:])
    while (homepage_data[-1:] == ['']):
        homepage_data = homepage_data[:-1]
    homepage_data.append("{{< callout emoji=\"🌐\" type=\"info\">}}")
    if (file_name == "index" or file_name == "_index"):
        homepage_data.append("  [" + title + "](" + prefix + "/)")
    else:
        homepage_data.append("  [" + title + "](" + prefix + file_name +"/)")
    homepage_data.append("{{< /callout >}}")

    new_homepage = open(homepage, "w")
    for line in homepage_data:
        new_homepage.write(line + "\n")
    new_homepage.close()

if len(sys.argv) != 3:
    print("call as \"python3 new_blog.py \{filepath\} \{title\} \"")

create_new_blog(sys.argv[1], sys.argv[2])