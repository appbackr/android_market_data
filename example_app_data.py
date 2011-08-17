# this code:
from android_market_data import scrape_and_extract_apps
scrape_and_extract_apps.extract_app('https://market.android.com/details?id=com.halfbrick.fruitninja')
# returned the following dict, as of August 17, 2011: 

{
'application_name': u'Fruit Ninja',
 'application_updated': u'February 1, 2011',
 'category': u'Arcade &amp; Action',
 'content_rating': u'Everyone',
 'description': u'The worldwide smash hit game Fruit Ninja is now available on Android!Fruit Ninja is a juicy action game with squishy, splatty and satisfying fruit carnage! Become the ultimate bringer of sweet, tasty destruction with every slash.Swipe up across the screen to deliciously slash fruit like a true ninja warrior. With three games modes in single player and worldwide leaderboards using Openfeint, the addictive gameplay will keep you coming back for even higher scores.Fruit Ninja features three packed gameplay modes - Classic, Zen and the new Arcade, featuring powerups including Freeze, Frenzy and Double Score! The bonus Dojo section includes unlockable blades and backgrounds, and you can also unlock achievements and post scores to the online leaderboards with Openfeint.Fruit Ninja is the original and the best slasher on Android!',
 'developer_homepage_url': 'http://www.halfbrick.com/Contact-us/',
 'developer_name': u'Halfbrick Studios',
 'developer_page_url': u'http://market.android.com/developer?pub=Halfbrick+Studios',
 'email_contacts': [],
 'install_size': u'10M',
 'installs': u'500,000 - 1,000,000',
 'logos': [u'https://ssl.gstatic.com/android/market/com.halfbrick.fruitninja/hi-124-6'],
 'normalized_daily_installs_chart': u'https://chart.googleapis.com/chart?cht=lxy&chd=e:AACIERGZIiKqMzO7RETMVVXdZmbud3f.iIkQmZohqqsyu7xDzM1U3d5l7u92,zM22884EzMwwttpcqqo1lyivhhiIiIj9jWgTfFgTjWkko1pcoOj9lLmZlyqq&chds=0.0,1.0&chs=105x75&chma=1,0,1,1&chco=42b6c9ff&chls=2.5,1.0,0.0&chxl=0:%7C%7C1:%7C%7C2:%7C',
 'price': u'$1.24',
 'rating': u'4.5',
 'rating_count': u'23,367',
 'requires_android': u'1.6 and up',
 'screenshots': [u'https://ssl.gstatic.com/android/market/com.halfbrick.fruitninja/ss-320-0-6',
                 u'https://www.gstatic.com/android/market/com.halfbrick.fruitninja/ss-320-1-6'],
 'twitter_contacts': [],
 'unique_package': 'com.halfbrick.fruitninja',
 'version': u'1.5.4'}
