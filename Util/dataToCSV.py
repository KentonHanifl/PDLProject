import csv
import re

def get_message(code, log):
    lengthToEndOfMessage = 2

    # Gather index' to extract message from the log
    codeIndex = log.index(code)
    messageEndIndex = log.index("stream")

    # Extract message from the log
    message = log[(codeIndex + len(code)):(messageEndIndex - lengthToEndOfMessage)]

    # Clean up the extracted message
    message = message.replace(',', '')
    message = message.replace('"', '')

    # Remove all non alphabet characters
    regex = re.compile('[^a-zA-Z]')
    message = regex.sub(' ', message)

    # Remove the 'n' at the end of every log
    message = message[:-2]

    return message


csvLines = []

# Open the master log file and remove the noise
with open('master.data') as input_file:
    lines = input_file.readlines()

    for line in lines:
        line = line.lower()

        if "info" in line:
            csvLines.append(['INFO', get_message("info", line)])

        elif "debug" in line:
            csvLines.append(['DEBUG', get_message("debug", line)])

        elif "notice" in line:
            csvLines.append(['NOTICE', get_message("notice", line)])

        elif "warning" in line:
            csvLines.append(['WARNING', get_message("warning", line)])

        elif "error" in line:
            csvLines.append(['ERROR', get_message("error", line)])


# Write the cleaned data to a proper csv file for efficient consumption
with open('test_csv.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['LOGCODE', 'MESSAGE'])
    filewriter.writerows(csvLines)
