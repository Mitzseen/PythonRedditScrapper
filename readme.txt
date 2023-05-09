README
Project Description
This project is designed to analyze the similarity between subreddits by examining their commenters. The program extracts comment data from the Reddit API using PRAW (Python Reddit API Wrapper) and stores it in a Python dictionary. It then uses a breadth-first search algorithm to find the subreddits that commenters in a specified subreddit are also commenting on, and calculates the similarity between these subreddits using a custom similarity function. The results are displayed in a graph using the NetworkX library.

pom.xml:
dependency file, named pom.xml, is a Maven project file that specifies the dependencies required for
the project to run. The file contains a list of dependencies, including their group IDs,
artifact IDs, and versions, that the project needs to compile and run successfully.

Installation:
In order to run this program, you will need to have Python 3 installed on your system. The following packages are also required and can be installed via pip:
-praw
-pandas
-networkx
-matplotlib
:
Usage
1. Open the config.py file and add your Reddit API credentials.
2. Run the get_comments.py script to extract comment data from the Reddit API and store it in a Python dictionary.
3. Run the analyze_comments.py script to analyze the comment data and calculate similarity between subreddits.
4. The results will be displayed in a graph using the NetworkX library.

Implementation
-get_comments.py
-PRAW library is imported to access Reddit API.
-pickle library is imported to store the comments data as a Python dictionary.
-os library is imported to check if the comments data has already been stored in a pickle file.
-time library is imported to limit the number of API requests.
-get_comments() function is defined to extract comments from the Reddit API using PRAW and store them in a Python dictionary.
-if os.path.exists('subredditsLong.pickle'): is used to check if the comments data has already been stored in a pickle file.
-time.sleep() is used to limit the number of API requests per minute.

analyze_comments.py:
-pandas library is imported to create a DataFrame for the comment data.
-networkx library is imported to create a graph to visualize the similarity between subreddits.
-custom_similarity() function is defined to calculate the similarity between two subreddits using their commenters.
-if len(common_subreddits) > 1: is used to only include subreddits with more than one commenter in the similarity calculation.
-Breadth-first search algorithm is used to find the subreddits that commenters in a specified subreddit are also commenting on.
-The results are displayed in a graph using the NetworkX library.
Credits
This project was created by Mitzseen Joseph.
Special thanks to the creators of the PRAW, pandas, networkx, and matplotlib libraries for their
contributions to this project.