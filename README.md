# WindowsTimelineParser
Parses the windows timeline data to extract user behavior analytics. 

I recently read this [article from TrustedSec](https://www.trustedsec.com/blog/oh-behave-figuring-out-user-behavior/). I have a particular research interest in AV/EDR evasion and this article caught my eye due to it's intersting premise: understanding user behavior is extremly important when attempting to defeat next generation EDRs using fancy A.I. and machine learning. A big thanks to [Oddvar Moe at TrustedSec](https://www.trustedsec.com/team/oddvar-moe/) and, as discovered through Mr Moe's article, [Kacos2000](https://www.linkedin.com/in/kacos2000/) for doing all the hard parts for me and highlighting this treasure trove of data. 

Like when I was first made aware that major web browsers store saved passwords in an unencrypted SQLLite database, I am so surprised that such detailed information on our behavior isn't encrypted or protected in any way. Mr Moe was very kind in walking us through his research on the data contained here and the possible use cases, but he stops short of open sourcing his code that parsed the data withing the ActivityCache.db database. That is proprietary code for TrustedSec. 

Having access to this telemetry should be in every red team toolkit for testing evasion techniques, and you'll definetely need it as your organisation's security posture increasingly matures thanks to your testing. So I made this parser for that purpose. I started off by copying the ActivityCache.db file and investigating the database structure, all of it's tables and fields, to see what information is useful. I then wrote a this parsing script in Python to extract every useful piece of information and generate reports for the benefit of everyone... everyone except the user that is having their privacy invaded of course 😊.

*This project is nowhere near finished*. Right now it generates the following:
- A CSV file containing the amount of time a user is activiely using each application.
- A CSV file containing the launch time and parameters used to start each activity.
- A PDF report with a bar and pie chart to visualise the most used applications.

I will continue to work on this in my free time until I feel I have extracted everything useful from it.
