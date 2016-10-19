# AdCentsE16

## Overview

WARNING: This is experimental and requires integration with a separate website.  Please contact 'poole_party' on the 21co slack channel if
you are interested in buying or hosting ads.

The AdCentsE16 is a bitcoin powered advertisement network running on the 21.co platform.  Anyone can sign up to host ads on their website and get paid in bitcoin.  Anyone can pay bitcoin to have their ad shown on a specified website.

## How Does it Work?
First, a website owner will need to register with the service and prove ownership of the website.  Once that has been verified, their website
will become available for anyone to bid to pay for an ad to be shown on that website.

Ad spaces are bought for 24 hour blocks of time using a bidding process.  The bidding process for an ad space is determined as follows:
* Every day at midnight EST, all bids will be reset and all ad spaces are available for bidding.
* Buy prices for ad spaces are the number of seconds until midnight EST the next night multiplied by a constant factor of 0.01 Satoshis.
* As the day progresses, the buy price for the ad space goes lower and lower until someone pays to purchase the ad space.
* The first person to successfully bid on an ad space will have their advertisement displayed on the target website the following day starting at midnight.
* The owner of the website will split all revenues 50%/50% with the AdCentsE16 service and payments are sent immediately on a successful bid.

Example:
* James registers and verifies ownership of the eSixteen.co website.
* James embeds the HTML code to show advertisements from the AdCentsE16 service on the eSixteen.co website.
* On Tuesday at 11:00PM EST, John bids to buy an ad on the eSixteen.co website.
  * John pays 36 satoshis since there is 1 hour left in the day (60 seconds * 60 minutes * 0.01 satoshis).
  * James receives 18 satoshis for hosting the ad on his site.
* On Wednesday from 00:00 AM EST to 12:59 PM EST, John's ad is displayed on the eSixteen.co website.

## How to Register a Website to Host Ads
Generate a receive address from your wallet.
```
$ wallet payoutaddress

18r3B1yUr1wduZj5UCyvsLeG8qRZ77ECbv
```

Register your domain using your 21 username and receive address.
```

$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/registrations' -X POST -d '{"url":"https://www.esixteen.co", "username": "poole_party", "address": "18r3B1yUr1wduZj5UCyvsLeG8qRZ77ECbv"}'
{
    "key": "LVFR9EOBZSRHWPBWRPAL",
    "message": "URL has been registered.  Place a meta tag with name='AdCentsE16-site-verification' and content='LVFR9EOBZSRHWPBWRPAL' at URL: https://www.my-web-page.com",
    "success": true
}
```

Check registration and expect it to show false validation.
```
$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/registration/LVFR9EOBZSRHWPBWRPAL'
{
    "message": "URL https://www.my-web-page.com could not be validated.  No meta tag was found with proper value LVFR9EOBZSRHWPBWRPAL.",
    "success": true,
    "validated": false
}
```

Add the meta tag to the head section in your web site.
```
<head>
  ...
  <meta name="AdCentsE16-site-verification" content="LVFR9EOBZSRHWPBWRPAL" />
  ...
</head>
```

Check to see if the server can validate ownership.
```
$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/registration/LVFR9EOBZSRHWPBWRPAL'
{
    "message": "URL https://www.my-web-page.com has been validated with proper owner via meta tag.",
    "success": true,
    "validated": true,
    "embedable_code": "<iframe width=\"600\" height=\"200\" src=\"https://www.esixteen.co/ad/A2561FJD24CXW5IFPH2Z\" frameborder=\"0\" allowfullscreen ></iframe>"
}
```
Next, embed the iframe into your HTML so ads will be shown.

## How to Buy Ad Space on a website

See what URLS are available to bid on for tomorrow.
```
$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/registrations'
{
    "sites": [
        {
            "key": "LVFR9EOBZSRHWPBWRPAL",
            "url": "https://www.my-web-page.com"
        }
    ],
    "success": true
}
```

Check the price of the URL for the site.  Set --maxprice on the cli to 1 satoshi to make sure it doesn't pay.
```
$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/buy/LVFR9EOBZSRHWPBWRPAL' -X POST --maxprice 1
Error: Resource price (23199) exceeds max price (1).
Please use --maxprice to adjust the maximum price.
```

Buy the ad space.  Note that you are given a campaignKey in response.
```
$ 21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/buy/LVFR9EOBZSRHWPBWRPAL' -X POST --maxprice 50 -d '{"title":"eSixteen.co - Welcome to the Grid", "description": "Check out the new grid computing network.", "target_url": "https://www.esixteen.co/", "image_url":"https://www.esixteen.co/img/network.png"}'
{
    "message": "URL successfully bought for tomorrow.",
    "success": true,
    "campaignKey": "9QBEYCOSDE6HEX70RLRS",
}
```
The following parameters are required:
* title: This is the header of text that will be displayed for the ad.
* description: This is the main body of text that will be displayed for the ad.
* image_url: This is an https link to the picture that will be displayed next to the ad.
* target_url: This is the https link where the user will be redirected when they click on the ad.

Use the campaignKey to get stats on your campaign after ads have been displayed.
```
21 buy 'http://[fcce:a977:eef6:442a:aaf8:0000:0000:0001]:11116/campaign/9QBEYCOSDE6HEX70RLRS'
{
    "clickthroughCount": 2,
    "impressionCount": 5,
    "success": true
}
```
