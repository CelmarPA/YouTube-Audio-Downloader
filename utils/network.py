# utils/network.py

import requests

def has_internet_connection(timeout: float = 3.0) -> bool:
    """
    Check if there is an active internet connection using an HTTP request.

    :param timeout: Timeout in seconds for the request
    :type timeout: float
    :return: True if internet connection is available, False otherwise
    :rtype: bool
    """
    try:
        response = requests.get("https://www.google.com/generate_204", timeout=timeout)

        return response.status_code == 204

    except requests.RequestException:
        return False
