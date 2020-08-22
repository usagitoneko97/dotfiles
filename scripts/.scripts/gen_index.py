#!/bin/env python
import sys

file_name = sys.argv[1]
output_name = sys.argv[2]
with open(file_name, "r") as f:
    contents = f.read().split("\n")
    overwrite_contents = ""
    i = 1
    for content_i, content in enumerate(contents):
        if content == "((index++))":
            # check no #index=n inserted
            previous = content[content_i-1]
            if "index=" not in previous:
                # insert "#index=n\n" before the line
                overwrite_contents += "#index={}\n".format(i)
            i += 1
        overwrite_contents += (content + "\n")
    if output_name == file_name:
        f.write(overwrite_contents)
    else:
        with open(output_name, "w") as out_f:
            out_f.write(overwrite_contents)
