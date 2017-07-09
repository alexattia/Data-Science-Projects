# Twitter Parsing
After spending some time on Twitter, following Machine Learning, Deep Learning and Data Science "influencers". I have found some interesting stuff.  
I decided to download some of those tweets. For example, @chrisalbon writes (draws would be more relevant) interesting Machine Learning flash cards.  
I am using Selenium to parse and download those flash cards and I create a daemon to parse and send me about new flash cards every day.  

`com.alexattia.machinelearning.downloadflashcards.plist` is the plist file to copy into /Library/LaunchDaemons/
`run.sh` is the script to launch every day
`download_pics.py`is the Python script