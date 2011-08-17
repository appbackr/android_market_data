Using the Android Market Data project
=====================================

What does it do?
------------

This project downloads HTML from the Android Market web site (market.android.com) and extracts information from it. 

To get the data of a single app: 

android_market_data.scrape_and_extract_apps.extract_app('https://market.android.com/details?id=com.halfbrick.fruitninja')  
This will return a dict holding nearly all the data available on that page.  For the return value of that call, see the example_app_data.py file  Currently we're getting most of the data available for an app from its detail page, and making some effort to get email address, twitter handles and contact page urls from the app developer's listed homepage.  

To get the reviews of a single app associated with a particular country and language: android_market_data.scrape_and_extract_apps.extract_app('https://market.android.com/details?id=com.halfbrick.fruitninja')  This will return a dict holding nearly all the data available on that page.  For the return value of that call, see the example_app_data.py file  Currently we're getting most of the data available for an app from its detail page, and making some effort to get email address, twitter handles and contact page urls from the app developer's listed homepage.  


Who is using it?
------------

This is used daily by Appbackr (www.appbackr.com).  Appbackr is actively maintaining and developing it with in-house developers.


Requirements
------------

- BeautifulSoup (tested with version 3.2)


License
------------

This software carries the MIT open source license: http://www.opensource.org/licenses/mit-license.php .

