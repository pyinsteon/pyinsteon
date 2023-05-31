"""Parse the topic map and print a human readable format."""
from pyinsteon.address import Address

FILE = "/workspaces/pyinsteon/pyinsteon.py"

topics: list[list[list[str]]] = []
topic_args: dict[str, list[str]] = {}
curr_topic: list[str] = []
curr_args: list[str] = []

address = ""
with open(file=FILE, mode="r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for line in lines:
        if ": Any" in line:
            print(line)
        if "class" in line:
            prev_topic = curr_topic
            indent = int(line.count("  ") / 2)
            curr_topic = [
                prev_topic[item] for item in range(0, min(len(prev_topic), indent))
            ]
            sub_topic = line.split(" ")[-1].split(":")[0]
            if indent == 0 and address == "":
                try:
                    address = Address(sub_topic).id
                except ValueError:
                    pass
            if sub_topic == address:
                sub_topic = "<address>"
            else:
                try:
                    sub_topic = int(sub_topic)
                    if sub_topic in range(0, 255):
                        sub_topic = "<group>"
                except ValueError:
                    pass
            curr_topic.append(sub_topic)
            if curr_topic not in topics:
                curr_args = []
                topics.append(curr_topic)

        elif "msgDataSpec" in line:
            args = line.strip().split("(")[-1][:-2]
            topic_str = ".".join(curr_topic)
            topic_args[topic_str] = args

for topic in topics:
    topic_str = ".".join(topic)
    print(topic_str, ": ", topic_args.get(topic_str, "None"))
