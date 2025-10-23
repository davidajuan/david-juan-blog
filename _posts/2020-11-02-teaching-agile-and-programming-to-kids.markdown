---
layout: post
title: "Teaching Agile and Programming to Kids"
categories: technology
---


<img src="/assets/images/Code-A-Pillar-Kids.jpg.webp" alt="Kids playing with a Code-A-Pillar" class="center">

With most afterschool and extracurricular programs being put on hold or moved to a virtual format, my wife and I have been looking for ways to provide hands-on STEM learning activities for our two daughters.  A few years ago I bought one of my daughters the Fisher Price Code-A-Pillar, which was played with for a few days before being put into long term hibernation in the toy bin.  It finally made it's way back out the other day, and after putting some fresh batteries in it I decided to see if now that my daughter is a few years older there is more interest in learning how to program.

The [Code-a-Pillar](https://amzn.to/3elJTsz) is basically a robot that is fed instructions by connecting modular segments to it's body.  You can sequence the body segments in different orders to navigate the robot through obstacle courses, and have it play music at various points.

<img src="/assets/images/Code-A-Pillar.jpg.webp" alt="Code-A-Pillar" class="center">

I started by setting up a few lego pieces as an obstacle course, and then asking my daughter how she thought she needed to arrange the modules in order to complete it.  She immediately started putting the pieces together in what she thought was going to be the best order, and I could see almost immediately that it wasn't going to work.  I was tempted to stop her and show her where her first error was, but saw the learning opportunity starting to form.  After spending a few minutes putting all of the modules together, she hit the go button and watched the robot go off course and run into the wall.

<img src="/assets/images/Code-A-Pillar-Setup.jpg.webp" alt="Code-A-Pillar" class="center">

I asked her to look at her sequence, and try to pinpoint where it went wrong.  She picked one of the modules, and decided that it needed to be switched to the opposite direction.  This wasn't where the error was, but I told her to try it, since the change was easy, and she would learn within a few seconds after hitting the go button whether or not it worked.  She hit the go button, and watched the robot veer off course and run into the wall again.  I pointed out that with all of the pieces attached, it was hard to follow exactly what the robot was going to do, and that she may have an easier time trying a few pieces at a time.  That is when the light bulb went off for her.  She took all of the pieces apart, and started focusing on getting the first turn in the obstacle course right.  She put together two straight modules and a right turn, hit the go button, and quickly learned that it was going too far.  She removed one straight module, tried again, and saw she was on the right track.  She then continued adding one module at a time, testing, and correcting, until she was able to complete the entire obstacle course.  I then started changing the obstacle course, and adding new requirements (such as stopping to play music at one specific point), to test her ability to adapt the program.

<img src="/assets/images/Code-A-Pillar-Play.jpg.webp" alt="Code-A-Pillar Success" class="center">

So what lessons did she learn?

- **The pitfalls of Waterfall Development.**  When your gather requirements, design the program, build it, and then have one "big bang" style deployment, it's really hard to get things right.
- **When to start fresh.**  After you realize that you've gone down the wrong path, there are times where hitting the reset button (*or git reset --hard HEAD*) and starting with a fresh perspective is easier than sorting through the mess that you've made.
- **Continuous Deployment.**  Break the problem you're trying to solve down as small as possible, and start with the first component.  Before moving on to the next one, release to a production (or production like) environment, and get realtime feedback on how close you are.  Adjust, and then move on to the next component.
- **Algorithms and Procedural Programming.**  Computers will do exactly what they're told to do.  Give them bad instructions, and you'll get bad results.  Give them good instructions, and incredible things can happen.

At the end of the day, the one lesson that I'm hoping that she learns from these types of activities is that solving puzzles is fun.  The feeling that you get every time you watch something work that you created is amazing, and we're fortunate enough to live in a time where people will pay you to do it for a living.

