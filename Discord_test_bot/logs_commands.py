from datetime import datetime


def print_colored(text: str, color_code: str, end='\n', sep=' ') -> None:
    print(f"\033[{color_code}m{text}\033[00m", end=end, sep=sep)


def print_log(type: str, message: str, width: int = 7) -> None:
    """
    Print a log message with a timestamp and colored log level.
    :param type: ERROR, WARNING, SUCCESS, INFO
    :param message:
    :param width:
    :return: printing log message into console

    Example:
    print_log('ERROR', "Error transferring message: 'TonapiClient
    """

    color_map = {
        'ERROR': '91',  # Red
        'WARNING': '93',  # Yellow
        'SUCCESS': '92',  # Green
        'INFO': '96'  # Light Cyan
    }

    color_code = color_map.get(type, '97')  # Default to white if level is unknown
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Center the log level text within the specified width
    level_centered = type.upper().center(width)

    # Format the message
    formatted_message = f"{timestamp} | {level_centered} | {message}"

    # Print the message with the appropriate color
    print_colored(formatted_message, color_code)


print_colored("Logging messages uploaded successfully!", '92')



if __name__ == "__main__":
    print_log('ERROR', "Error transferring message: 'TonapiClient' object has no attribute '_TonapiClient__read_content'")
    print_log('WARNING', "Retrying transfer...")
    print_log('SUCCESS', "Messages transferred successfully!")
    print_log('INFO', "Found 1 recipients.")
    print_log('INFO', "Transferring from 1 wallets to 1 recipients...")
