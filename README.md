# AnyPosts-Blog
A simple yet fully featured blogging application using Python(Flask).
![Preview](wip.png)

## Setup

- Install dependencies
  - `pip install -r requirements.txt`

- Run
  - `python app.py`

## Features

  - Users can register for an account and login.
  - Once logged in a user can:
  
    - `Update their information and change their profile picture from the default picture.`
    - `Create a new post, update a post they posted and delete a post.`
    - `like and comment on other peoples posts.`
    
  - If a user has forgotten their password, they can request a password reset and a link will be send out to the email they used to register.
  
  - I have implemented pagination to limit to a number of 5 posts per page.
  
  - Every user can View posts from other users and can also filter posts by a specific user.
