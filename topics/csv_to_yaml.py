import csv

with open("command_topics.csv", "r") as csv_file:
    topics = csv.reader(csv_file)

    with open("topics.yaml", "w") as topic_file:
        topic_file.write("ROOT_TOPIC:\r\n")
        topic_file.write("  description: Insteon pub/sub topics\r\n")
        topic_file.write("  topics:\r\n")
        topic_file.write("  - topic: command\r\n")
        topic_file.write("    description: Device command.\r\n")
        topic_file.write("    topics:\r\n")
        prev_topic = ""
        level = 0
        indent = "    {}{}{}{}\r\n"
        spacing = "  "
        new_topic = "- "
        for row in topics:
            topic = str(row[1]).strip().replace("  ", " ")
            subtopic = str(row[2]).strip().replace("  ", " ")
            topic_desc = str(row[3]).strip().replace("  ", " ")
            subtopic_desc = str(row[4]).strip().replace("  ", " ")
            if topic != prev_topic:
                level = 0
                topic_file.write(
                    indent.format(spacing * level, new_topic, "topic: ", topic)
                )
                topic_file.write(
                    indent.format(spacing * level, spacing, "description: ", topic_desc)
                )
                topic_file.write(indent.format(spacing * level, spacing, "topics:", ""))
                level = 1
                prev_topic = topic

            topic_file.write(
                indent.format(spacing * level, new_topic, "topic: ", subtopic)
            )
            topic_file.write(
                indent.format(spacing * level, spacing, "description: ", subtopic_desc)
            )
