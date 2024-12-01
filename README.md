# Spotify Wrapped

> ### Disclaimer:
> This project was developed as part of Team 36's project for 2340-B project for **November 2024**. It is intended to showcase software development skills and explore new ways to visualize Spotify music listening data. The application provides a fun and interactive way for users to view their music habits and share them with friends.

## Overview:
Spotify Wrapped is a web application that allows users to explore and interact with detailed insights about their Spotify music listening habits. Users can generate fun, colorful summaries of their musical tastes over short, medium, and long timeframes. They can save their Spotify wraps, play creative games, and share their wraps on their socials.

## Features:
### A. User Authentication
- Users can create an account and log in to access personalized features such as saving and viewing past Spotify wraps.
- Users can log out, and their account information is persisted after exiting the website.
- Users can create wraps from different spotify accounts withint he same local account
- Users can delete their account and their wraps.

### B. Spotify Wrap Generation
- Users can generate a colorful, creative presentation of their Spotify listening habits based on the data parsed from their account.
- The wrap is divided into at 8 distinct slides, each displaying a different aspect of the user's listening habits and music tastes.

### C. Games
- Users can engage with fun games embedded in their Spotify Wrapped experience, including a quiz regarding a lyric from one of your most listened to songs.

### D. Mobile-Friendly UI
- The website is designed to be responsive and works well on both desktop and mobile devices.

### E. Dark Mode & Theme Customization
- Users can toggle a dark mode for the entire UI.

### F. Social Media Sharing
- Users can easily share their Spotify Wrapped on social media platforms like Instagram, LinkedIn, and X (formerly Twitter).


## Project Setup
### Prerequisites:
- Python 3.x
- Django
- Spotify API key (for fetching user data)

### Installation:
1. Clone the repository:
```sh
git clone https://github.com/your-repo/spotify-wrapped.git](https://github.com/CS2340-Team-36/spotify_wrapper.git
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Set up environment variables (such as the Spotify API key) in your .env file:
```sh
SPOTIFY_API_KEY=your_api_key
```

4. Run migrations to set up the database:
```sh
python manage.py migrate
```

5. To start the development server:
```sh
python manage.py runserver
```


## Built with
* [![JavaScript][JavaScript.com]][JavaScript-url]
* [![HTML][HTML.com]][HTML-url]
* [![CSS][CSS.com]][CSS-url]
* [![Python][Python.org]][Python-url]


[JavaScript.com]: https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript
[JavaScript-url]: https://www.javascript.com/

[HTML.com]: https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5
[HTML-url]: https://developer.mozilla.org/en-US/docs/Web/HTML

[CSS.com]: https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3
[CSS-url]: https://developer.mozilla.org/en-US/docs/Web/CSS

[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python
[Python-url]: https://www.python.org/

## Links:
1. Team Website: 
2. GitHub Repository: https://github.com/CS2340-Team-36/spotify_wrapper
3. Kanban Board: https://trello.com/b/PjyDzB6w/2340-project-2-team-36


## Contributors:
1. Akshay Bhave (Full-Stack Developer)
2. Ananya Pattamatta (Back-End Developer)
3. Jahnavi Manglik (Product Owner, Developer)
4. Manan Khanna (Full-Stack Developer)
5. Vasanth Gogineni (Scrum Master, Front-End Developer)

