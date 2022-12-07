from spinrewriterapi import SpinRewriterAPI
import os
from dotenv import load_dotenv
load_dotenv()
###############################################################################
#
# Spin Rewriter API for Python >= 3 (PyPi) example of how to
# generate unique variation.
#
# Note: Spin Rewriter API server is using a 120-second timeout.
# Client scripts should use a 150-second timeout to allow for HTTP connection
# overhead.
#
# SDK Version    : v1.0
# Language       : Python 3
# Dependencies   : spin-rewriter-api
# Website        : https://www.spinrewriter.com/
# Contact email  : info@spinrewriter.com
#
# SDK Author     : Bartosz Wójcik (https://www.pelock.com)
#
###############################################################################

#
# include Spin Rewriter API module
#
from spinrewriterapi import SpinRewriterAPI

# your Spin Rewriter email address goes here
email_address = "adam@sitegrinder.net"

# your unique Spin Rewriter API key goes here
api_key = os.getenv('SPIN_REWRITER_API_KEY')

# Spin Rewriter API settings - authentication:
spinrewriter_api = SpinRewriterAPI(email_address, api_key)
spinrewriter_api.set_add_html_markup(True)
spinrewriter_api.set_confidence_level("high")

def spin_article(file_path, keyword=None, protected_terms=None, add_html_markup=True):
    #protected_terms = ["John", "Douglas", "Adams", "then"]
    print('Spinning article')
    if protected_terms:
        spinrewriter_api.set_protected_terms(protected_terms)
    if add_html_markup:
        spinrewriter_api.set_add_html_markup(True)


    with open(file_path) as f:
        text = f.read()
    result = spinrewriter_api.get_text_with_spintax(text)
    if result:
        # print("Spin Rewriter API response")
        # TODO handle article spin errors
        article = result['response'].replace('h1', 'h2')
        return article
    else:
        print("Spin Rewriter API error")
        return False
 

