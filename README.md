# SocialsBot
Forwards content from social media to Discord


# Why?
I made SocialsBot because the alternative is IfTTT with Zapier, which doesn't always work, presumably due to the amount of API calls it has to make to work for everyone.  This bot was made with uploading it to GitHub for anyone to take and host on their own in mind, so that they only have to worry about their own API calls.  I could be completely wrong here and wasting time, but at least it's something I know inside and out.

# Installation
- Clone the repo into a server
- Remove ".example" from "config.ini.example"
- Change the config.ini to your bot key, as well as change the command key to whatever you prefer
- Run socialsbot.py eternally

# Usage
## `create <platform> <id>`
  Creates a Social object to be modified for pull from the platform <platform>, referred to with <id>
### Example
  `create youtube man` 
  
## `user <id> <social_id>`
  Adds a social id for targetting to <id>
  
  For youtube it's the part that appears after "channel" in https://www.youtube.com/channel/UCBGB0j2CKF189raLT8DM33w
### Example
  `user man UCBGB0j2CKF189raLT8DM33w`
  This makes the youtube social with ID: man link to https://www.youtube.com/channel/UCBGB0j2CKF189raLT8DM33w
  
## `channel <id>`
  Has the bot ask which channel/s you would like to have the Social send to
### Example
  `channel man`
  Bot: Which channel?
  User: #adiscordchannel
  
## `message <id>`
  Has the bot ask what message you would like to have sent with the automation
### Example
  `message man` 
  Bot: What message?
  User: @ping new video is out!
  
## `socials`
  Gives a list of Socials
### Example
  `socials` 
  
## `check id`
  Checks the values of a Social
### Example
  `check Social` 
 
## `delete id`
  Deletes a Social from the list
### Example
  `delete man` 
  
  
  
  
