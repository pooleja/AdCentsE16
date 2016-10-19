import json
import logging
import psutil
import subprocess
import os
import yaml
import random
import string
import threading
import datetime

from flask import Flask
from flask import request
from sqldb import AdsSQL
from adCentsE16 import AdCentsE16

from two1.commands.util import config
from two1.wallet.two1_wallet import Wallet
from two1.bitserv.flask import Payment
from two1.bitserv import BitTransfer
from two1.bitrequests import BitTransferRequests

app = Flask(__name__)
# app.debug = True

# Config options
CONTACT = "james@esixteen.co"
SERVER_BASE_URL = "https://www.esixteen.co"
SERVER_SECRET_HEADER = "asdfasdf"
PRICE_SATOSHIS_PER_SECOND = 0.01

# setup wallet
wallet = Wallet()
payment = Payment(app, wallet)
requests = BitTransferRequests(wallet, config.Config().username)

# hide logging
logger = logging.getLogger('werkzeug')

# Create the Database connection object
sql = AdsSQL()

# Create the ES connection object
ads = AdCentsE16(SERVER_BASE_URL)

# Lock for pricing and buying
buy_rlock = threading.RLock()


class MockRequest:
    """
    This is a fake class.
    """

    text = ""


@app.route('/registrations', methods=['POST'])
@payment.required(10)
def register_url():
    """
    Creates a new Registration and returns a secret code for the specified domain to put into meta.
    """
    postData = json.loads(request.data.decode('UTF-8'))

    # Get and validate the url
    url = postData['url']
    if url.startswith("http") is not True:
        logger.warning("Failure: Invalid URL specified for register call: {}".format(url))
        return json.dumps({"success": False, "error": "Failure: Invalid \'url'\ parameter specified."}), 500

    # Get and validate the username
    username = postData['username']
    if not username:
        logger.warning("Failure: Invalid username specified for register call: {}".format(username))
        return json.dumps({"success": False, "error": "Failure: Invalid \'username'\ parameter specified."}), 500

    # Get and validate the username
    address = postData['address']
    if not address:
        logger.warning("Failure: Invalid address specified for register call: {}".format(address))
        return json.dumps({"success": False, "error": "Failure: Invalid \'address'\ parameter specified."}), 500

    try:
        # Generate a random key for this request
        unique_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))

        sql.insert_new_registration(url, username, unique_key, address)

        return json.dumps({
            "success": True,
            "key": unique_key,
            "message": "URL has been registered.  Place a meta tag with name=\'AdCentsE16-site-verification\' "
            "and content=\'{}\' at URL: {}".format(unique_key, url)
        })

    except Exception as err:
        logger.error("Failure: {0}".format(err))
        return json.dumps({"success": False, "error": "Error: {0}".format(err)}), 500


@app.route('/registration/<key>')
@payment.required(10)
def validate_registration(key):
    """
    Gets the registion and validates that the appropriate metadata key was placed on the url that was registered.
    """
    # Get and validate the key
    if not key:
        logger.warning("Failure: Invalid \'key\' specified for validate call: {}".format(key))
        return json.dumps({"success": False, "error": "Failure: Invalid \'key'\ parameter specified."}), 500

    # Get the registration object based on the key
    registration = sql.get_registration(key)
    if not registration:
        logger.warning("Failure: Could not find \'key\' specified for validate call: {}".format(key))
        return json.dumps({"success": False, "error": "Failure: Invalid \'key'\ parameter specified."}), 404

    try:

        # Check if the meta key is found on the page
        if ads.validate_url(registration[AdsSQL.REG_URL], registration[AdsSQL.REG_KEY]):
            # Meta was found.  Mark the registration as validated.
            sql.mark_registration_validated(registration[AdsSQL.REG_KEY])

            code = '<iframe width="600" frameborder="1" src="'
            code += SERVER_BASE_URL + "/ad/" + registration[AdsSQL.REG_KEY]
            code += '" frameborder="0" allowfullscreen ></iframe>'

            return json.dumps({
                "success": True,
                "validated": True,
                "message": "URL {} has been validated with proper owner via meta tag.".format(registration[AdsSQL.REG_URL]),
                "embedable_code": code
            })
        else:
            # Meta was not found
            return json.dumps({
                "success": True,
                "validated": False,
                "message": "URL {} could not be validated.  No meta tag was found with proper value {}.".format(registration[AdsSQL.REG_URL], key)
            })

    except Exception as err:
        logger.error("Failure: {0}".format(err))
        return json.dumps({"success": False, "error": "Error: {0}".format(err)}), 500


@app.route('/registrations')
@payment.required(10)
def get_open_auctions():
    """
    Returns a list of all sites that do not already have a paid auction for today and are validated.
    """
    try:

        available_sites = sql.get_sites_with_no_buys_today()

        return json.dumps({
            "success": True,
            "sites": available_sites
        })

    except Exception as err:
        logger.error("Failure: {0}".format(err))
        return json.dumps({"success": False, "error": "Error: {0}".format(err)}), 500


def get_price_for_url(request, key):
    """
    Gets the price of the url key in the request.

    If the url has already been bought today, then an error is thrown.
    Otherwise, it will return the number of seconds left in the day
    """
    # Get and validate the key
    pieces = request.path.split('/')
    key = pieces[len(pieces) - 1]
    if not key:
        logger.warning("Failure: Invalid \'key\' specified for validate call: {}".format(key))
        return json.dumps({"success": False, "error": "Failure: Invalid \'key\' parameter specified."})

    # Verify the key exists
    reg = sql.get_registration(key)
    if not reg:
        return json.dumps({"success": False, "error": "Failure: Invalid \'key\' parameter specified."})

    with buy_rlock:
        # First validate there is not already a buy on this url key
        currentbuy = sql.get_todays_buy_for_site(key)
        if currentbuy:
            return json.dumps({"success": False, "error": "URL specified is already bought for today."})

        # Calculate seconds left in the day
        now = datetime.datetime.now()
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        tomorrowTime = datetime.datetime.combine(tomorrow_date, datetime.datetime.min.time())
        return int((tomorrowTime - now).seconds * PRICE_SATOSHIS_PER_SECOND)


@app.route('/buy/<key>', methods=['POST'])
@payment.required(get_price_for_url)
def buy(key):
    """
    Tries to buy the auction for the specified registration key.
    """
    # Get and validate the key
    if not key:
        logger.warning("Failure: Invalid \'key\' specified for validate call: {}".format(key))
        return json.dumps({"success": False, "error": "Failure: Invalid \'key'\ parameter specified."}), 400

    postData = json.loads(request.data.decode('UTF-8'))

    # Get and validate the title
    title = postData['title']
    if not title:
        logger.warning("Failure: Invalid \'title\' specified for validate call: {}".format(title))
        return json.dumps({"success": False, "error": "Failure: Invalid \'title'\ parameter specified."}), 400

    # Get and validate the description
    description = postData['description']
    if not description:
        logger.warning("Failure: Invalid \'description\' specified for validate call: {}".format(description))
        return json.dumps({"success": False, "error": "Failure: Invalid \'description'\ parameter specified."}), 400

    # Get and validate the target_url
    target_url = postData['target_url']
    if not target_url:
        logger.warning("Failure: Invalid \'target_url\' specified for validate call: {}".format(target_url))
        return json.dumps({"success": False, "error": "Failure: Invalid \'target_url'\ parameter specified."}), 400

    # Get and validate the image_url
    image_url = postData['image_url']
    if not image_url:
        logger.warning("Failure: Invalid \'image_url\' specified for validate call: {}".format(image_url))
        return json.dumps({"success": False, "error": "Failure: Invalid \'image_url'\ parameter specified."}), 400

    # Generate a random key for this request
    campaignKey = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))

    with buy_rlock:
        incoming_payment_info = json.loads(request.headers['Bitcoin-Transfer'])
        payment_amount = incoming_payment_info['amount']

        # First validate there is not already a buy on this url key
        currentbuy = sql.get_todays_buy_for_site(key)
        if currentbuy:
            # TODO: Tell the user to ask for a refund since this has already been bought.
            return json.dumps({"success": False, "error": "URL specified is already bought for today."}), 400

        # Create the buy for the specified site
        now = datetime.datetime.now()
        sql.insert_new_buy(key, campaignKey, title, description, target_url, image_url, now)
        sql.update_latest_buy_on_registration(key, now)

        # Return success info and send 50% payment price to owner of site
        logger.debug("Looking for registration of key {}".format(key))
        reg = sql.get_registration(key)
        logger.debug("Reg: {}".format(reg))
        logger.debug("Paying user {} for purchase of {}".format(reg[AdsSQL.REG_USERNAME], reg[AdsSQL.REG_URL]))
        paid = pay_user(reg[AdsSQL.REG_USERNAME], reg[AdsSQL.REG_ADDRESS], int(payment_amount / 2))

        if not paid:
            # TODO: Throw error and save DB record
            logger.error("Failure: to pay client 50% payment")
        else:
            logger.debug("Successful payment sent")

        # Upload ad buy to server so it will get shown
        upload = uploadAd(title, description, target_url, reg[AdsSQL.REG_URL], image_url, key, campaignKey)

        if upload:
            return json.dumps({"success": True, "message": "URL successfully bought for tomorrow with Campaign Key {}.".format(campaignKey),
                               "campaignKey": campaignKey})
        else:
            return json.dumps({"success": False, "message": "Failed to upload ad to server."})


def uploadAd(title, description, target_url, site_url, image_url, key, campaignKey):
    """
    Post result data to server.
    """
    try:
        data = {
            'title': title,
            'description': description,
            'targetUrl': target_url,
            'hostedUrl': site_url,
            'imageUrl': image_url,
            'siteKey': key,
            'campaignKey': campaignKey,
        }

        postHeaders = {"client": SERVER_SECRET_HEADER}
        ret = requests.post(SERVER_BASE_URL + "/ad", json=data, headers=postHeaders)

        if ret.json()['success'] is True:
            logger.info("Successfully saved ad")
            return True
        else:
            logger.error("Failed to upload ad {}".format(ret.json()['message']))
            return False

    except Exception as err:
        logger.error("Unable to upload ad with error: {}".format(err))
        return False


def pay_user(to_user_name, to_address, amount):
    """
    Uses a BitTransferRequests to do an off chain payment.
    """
    headers = {BitTransferRequests.HTTP_BITCOIN_PRICE: amount,
               BitTransferRequests.HTTP_BITCOIN_ADDRESS: to_address,
               BitTransferRequests.HTTP_BITCOIN_USERNAME: to_user_name}
    response = MockRequest()
    setattr(response, 'headers', headers)
    setattr(response, 'url', 'http://10.244.119.122:11116')

    logger.debug("Making 402 payment request with headers: {}".format(response))
    req = requests.make_402_payment(response, amount)
    logger.debug("Have the payment: {}".format(req))
    transfer = BitTransfer(wallet, username=to_user_name)
    logger.debug("Have the transfer: {}".format(transfer))
    return transfer.redeem_payment(amount, req)


@app.route('/campaign/<campaignKey>')
@payment.required(10)
def get_campaign_stats(campaignKey):
    """
    Gets the stats for this campaign from the server.
    """
    postHeaders = {"client": SERVER_SECRET_HEADER}
    ret = requests.get(SERVER_BASE_URL + "/ad/stats/" + campaignKey, headers=postHeaders)

    return ret.text


if __name__ == '__main__':
    import click

    @click.command()
    @click.option("-d", "--daemon", default=False, is_flag=True, help="Run in daemon mode.")
    @click.option("-l", "--log", default="ERROR", help="Logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    def run(daemon, log):
        """
        Run the server.
        """
        # Set logging level
        numeric_level = getattr(logging, log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log)
        logging.basicConfig(level=numeric_level)

        if daemon:
            pid_file = './adCentsE16.pid'
            if os.path.isfile(pid_file):
                pid = int(open(pid_file).read())
                os.remove(pid_file)
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                except:
                    pass
            try:
                p = subprocess.Popen(['python3', 'adCentsE16-server.py'])
                open(pid_file, 'w').write(str(p.pid))
            except subprocess.CalledProcessError:
                raise ValueError("error starting adCentsE16-server.py daemon")
        else:

            logger.info("Server running...")
            app.run(host='::', port=11116)

    run()
