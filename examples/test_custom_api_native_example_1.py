from lightbulb.api.api_native import LightBulb
import base64

lightbulbapp = LightBulb()
path = "/test/env/bin/lightbulb"  #Path to binary


configuration_A = {'TESTS_FILE_TYPE': 'None', 'ALPHABET': '32-57,58-64,65-126', 'SEED_FILE_TYPE': 'FLEX', 'TESTS_FILE': 'None','DFA1_MINUS_DFA2': 'True', 'SAVE': 'False', 'HANDLER': 'None', 'SEED_FILE': '{library}/regex/BROWSER/html_p_attribute.y'}
configuration_B = {'TESTS_FILE_TYPE': 'None', 'ALPHABET': '32-57,58-64,65-126', 'SEED_FILE_TYPE': 'FLEX', 'TESTS_FILE': 'None','DFA1_MINUS_DFA2': 'True', 'SAVE': 'False', 'HANDLER': 'None', 'SEED_FILE': '{library}/regex/BROWSER/html_p_attribute.y'}
handlerconfig_A = {'WSPORT': '5000','WBPORT': '5080', 'BROWSERPARSE': 'True', 'DELAY': '50', 'HOST': 'localhost'}
handlerconfig_B = {'URL': 'http://127.0.0.1/~fishingspot/securitycheck/index.php', 'BLOCK':'Impact', 'REQUEST_TYPE':'GET','PARAM':'input','BYPASS':'None', 'PROXY_SCHEME': 'None', 'PROXY_HOST': 'None', 'PROXY_PORT': 'None', 'PROXY_USERNAME': 'None', 'PROXY_PASSWORD': 'None','USER_AGENT': "Mozilla/5.0", 'REFERER': "http://google.com"}


stats = lightbulbapp.start_sfadiff_algorithm(
    path,
    configuration_A,
    configuration_B,
    handlerconfig_A,
    handlerconfig_B,
    "BrowserHandler",
    "HTTPHandler")

print stats


