import time
import praw
import json
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import os
import itertools
import np
import random
from networkx.algorithms import connected_components
from collections import deque

client_id = 'iYHvrbYOEx4LVrGoChcZqQ'
client_secret = 'AD_-Kt72hBMB9i5xEFWqDVTQG9Pzng'
user_agent = 'JavaScrapper/1.0.0'
subreddit_names = ["wallstreetbets", "robinhood", "coinbase",
                   "trading", "pennystocks", "amcstock"]

# Check if file exists
if os.path.exists('subreddits.pickle'):
    # Deserialize/grab subreddits list from file
    with open('subreddits.pickle', 'rb') as f:
        subreddits = pickle.load(f)
    subreddit_commenters_set = set()
    for subreddit in subreddits:
        subreddit_name = subreddit['subreddit_name']
        posts = subreddit['posts']
        commenters = set()
        for post in posts:
            commenters.update(post['comments'])
        subreddit_commenters_set.add((subreddit_name, tuple(commenters)))
    valid_pairs = set()

    # Get all commenters and their associated subreddits
    commenter_subreddit_map = {}
    for subreddit in subreddits:
        for post in subreddit['posts']:
            for commenter in post['comments']:
                if commenter not in commenter_subreddit_map:
                    commenter_subreddit_map[commenter] = set()
                commenter_subreddit_map[commenter].add(subreddit['subreddit_name'])

    # Find valid pairs of commenters starting from a chosen subreddit
    chosen_subreddit = "wallstreetbets"
    if chosen_subreddit in subreddit_names:
        chosen_commenters = list(commenter_subreddit_map.keys())
        for commenter1 in chosen_commenters:
            if commenter1 in commenter_subreddit_map and chosen_subreddit in commenter_subreddit_map[commenter1]:
                for commenter2 in chosen_commenters:
                    if commenter1 != commenter2 and commenter2 in commenter_subreddit_map and chosen_subreddit in \
                            commenter_subreddit_map[commenter2]:
                        common_subreddits = set(commenter_subreddit_map[commenter1]).intersection(
                            set(commenter_subreddit_map[commenter2]))
                        if len(common_subreddits) > 2:
                            pair = (commenter1, commenter2, tuple(common_subreddits))
                            if pair not in valid_pairs:
                                valid_pairs.add(pair)

    if len(valid_pairs) == 0:
        print(f"No valid pairs found for subreddit: {chosen_subreddit}")
    else:
        print(f"Valid pairs of commenters for subreddit {chosen_subreddit}:")
        for pair in valid_pairs:
            commenter1, commenter2, common_subreddits = pair
            print(f"({commenter1}, {commenter2}, common subreddits: {list(common_subreddits)})")


    def custom_similarity(commenter1_subreddits, commenter2_subreddits, all_subreddits, chosen_subreddit):
        # Exclude the chosen_subreddit from the set of all_subreddits
        remaining_subreddits = all_subreddits - {chosen_subreddit}
        num_remaining_subreddits = len(remaining_subreddits)

        common_subreddits = commenter1_subreddits.intersection(commenter2_subreddits)
        common_remaining_subreddits = common_subreddits.intersection(remaining_subreddits)

        similarity = len(common_remaining_subreddits) / num_remaining_subreddits
        return similarity


    def classify_similarity(avg_similarity):
        if avg_similarity > 0.6:
            return "extremely significant"
        elif avg_similarity > 0.3:
            return "significant"
        else:
            return "not significant"


    # Create a new graph
    G = nx.Graph()
    commenter_check = set()

    # Add edges for each valid pair
    for pair in valid_pairs:
        commenter1, commenter2, common_subreddits = pair
        if commenter1 not in commenter_check:
            G.add_node(commenter1)
            commenter_check.add(commenter1)
        if commenter2 not in commenter_check:
            G.add_node(commenter2)
            commenter_check.add(commenter2)
        edge_weight = len(common_subreddits)
        G.add_edge(commenter1, commenter2, weight=edge_weight)

    # Get the connected components
    components = list(nx.connected_components(G))

    # Assign a unique color to each component
    colors = []
    for i in range(len(components)):
        colors.append((random.random(), random.random(), random.random()))
    color_map = {}
    for i, component in enumerate(components):
        for node in component:
            color_map[node] = colors[i]

    # Draw the graph with different colors for each component
    num_nodes = len(G.nodes())
    pos = nx.spring_layout(G, k=num_nodes / 3)

    # Create a figure with two subplots: one for the graph and one for the text
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    ax1.axis('off')
    ax2.axis('off')

    # Draw the graph on the first subplot
    for i, component in enumerate(components):
        nx.draw_networkx_nodes(G, pos, nodelist=component, node_size=100, node_color=[colors[i]], ax=ax1)

    nx.draw_networkx_edges(G, pos, width=0.5, edge_color='gray', ax=ax1)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax1)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax1)

    # Calculate the number of unique graphs
    num_components = len(components)
    # Calculate average similarity between connected nodes
    total_similarity = 0.0
    num_edges = len(G.edges())
    for edge in G.edges():
        commenter1, commenter2 = edge
        subreddits1 = commenter_subreddit_map[commenter1]
        subreddits2 = commenter_subreddit_map[commenter2]
        all_subreddits = set(subreddit_names) - {chosen_subreddit}
        similarity = custom_similarity(subreddits1, subreddits2, all_subreddits, chosen_subreddit)
        print(similarity)
        total_similarity += similarity
    avg_similarity = total_similarity / num_edges
    similarity_classification = classify_similarity(avg_similarity)
    visited = set()
    smallest_edge_weight = float('inf')
    # Bredth first search to find the smallest edge weight
    for node in G.nodes():
        if node not in visited:
            # Create a queue and enqueue the starting node
            queue = deque([node])

            while queue:
                current_node = queue.popleft()
                visited.add(current_node)
                # Check the edge weights of the current node's neighbors
                for neighbor, edge_data in G[current_node].items():
                    weight = edge_data['weight']
                    if weight < smallest_edge_weight:
                        smallest_edge_weight = weight
                    # Enqueue the neighbor if it has not been visited
                    if neighbor not in visited:
                        queue.append(neighbor)

    print("Smallest edge weight:", smallest_edge_weight)
    # Display the text on the second subplot
    text1 = f"The amount of unique graphs: {len(components)}"
    text2 = f"Average similarity between connected nodes: {avg_similarity:.3f}"
    similarity_message = f"The {chosen_subreddit} graph has {similarity_classification} similarity. "
    if similarity_classification == "extremely significant":
        similarity_message += "Meaning that a large amount of its users comment underneath the other subreddits."
    elif similarity_classification == "significant":
        similarity_message += "Meaning that a significant amount of its users comment underneath the other subreddits."
    else:
        similarity_message += "Meaning that a small amount of its users comment underneath the other subreddits."

    start_reddit_explanation = (
        f"The homophily will vary based on the start subreddit, that you have inputted as the key"
        f" the ammount of subreddits and the type of common pairs that you decide to account for. "
        f"In this example, the start subreddit is {chosen_subreddit}. "
        f"The total ammount of subbreddits in our set: {len(subreddit_names)} "
        f"We only added a common pair into the common pairs set if it"
        f" had more than:{smallest_edge_weight - 1} common subreddits"
    )

    # Combine the text and display it in the second subplot
    full_text = f"{text1}\n{text2}\n{similarity_message}\n\n{start_reddit_explanation}"
    ax2.text(0, 1, full_text, verticalalignment='top', wrap=True, fontsize=12)

    plt.tight_layout()
    plt.show()


else:
    # Fetch data from Reddit

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    post_limit = 100
    subreddits = []
    for subreddit_name in subreddit_names:
        subreddit = reddit.subreddit(subreddit_name)

        posts = []
        count = 0
        for submission in subreddit.top(time_filter='all', limit=20):
            if count == post_limit:
                break
            post = {
                'title': submission.title,
                'score': submission.score,
                'url': submission.url,
                'comments': []
            }

            submission.comments.replace_more(limit=10)

            for comment in submission.comments:
                if comment.author is not None:
                    post['comments'].append(comment.author.name)
            posts.append(post)
            count += 1
            time.sleep(1)
        subreddits.append({
            'subreddit_name': subreddit_name,
            'posts': posts
        })
    # Serialize/add subreddits list to file
    with open('subreddits.pickle', 'wb') as f:
        pickle.dump(subreddits, f)

    # print(json.dumps(subreddits))

    # Get all commenters and their associated subreddits
    commenter_subreddit_map = {}
    for subreddit in subreddits:
        for post in subreddit['posts']:
            for commenter in post['comments']:
                if commenter not in commenter_subreddit_map:
                    commenter_subreddit_map[commenter] = set()
                commenter_subreddit_map[commenter].add(subreddit['subreddit_name'])


    def getCommenters(subreddit_name):
        """
        Returns a set of commenters in the given subreddit.
        """
        subreddit = reddit.subreddit(subreddit_name)
        commenters = set()
        for submission in subreddit.top(time_filter='all', limit=40):
            submission.comments.replace_more(limit=10)
            for comment in submission.comments:
                if hasattr(comment, "author") and comment.author is not None:
                    commenters.add(comment.author.name)
        return commenters


    # Get valid pairs of commenters
    valid_pairs = set();
    # chosen_subreddit = input("Enter a subreddit name to find valid pairs of commenters: ")
    chosen_subreddit = "wallstreetbets"
    if chosen_subreddit in subreddit_names:
        chosen_commenters = list(getCommenters(chosen_subreddit))
        for commenter1 in chosen_commenters:
            if commenter1 in commenter_subreddit_map:
                for commenter2 in commenter_subreddit_map:
                    if commenter1 != commenter2 and commenter2 in commenter_subreddit_map:
                        common_subreddits = set(commenter_subreddit_map[commenter1]).intersection(
                            set(commenter_subreddit_map[commenter2]))
                        if len(common_subreddits) > 3:
                            pair = frozenset([commenter1, commenter2, tuple(common_subreddits)])
                            if pair not in valid_pairs:
                                valid_pairs.add(pair)
                                print(
                                    f"{commenter1} and {commenter2} are in the same subreddit(s): {', '.join(common_subreddits)}")
    else:
        print(f"{chosen_subreddit} is not a valid subreddit name.")
    if len(valid_pairs) == 0:
        print(f"No valid pairs found for subreddit: {chosen_subreddit}")
    else:
        print(f"{chosen_subreddit} had valid pairs.")
    # Create a new graph
    G = nx.Graph()
    # set that contains all the commenters
    commenter_set = set()
    # Add edges for each valid pair
    for pair in valid_pairs:
        commenter1, commenter2, common_subreddits = pair
        if commenter1 not in commenter_set:
            G.add_node(commenter1)
            commenter_set.add(commenter1)
        if commenter2 not in commenter_set:
            G.add_node(commenter2)
            commenter_set.add(commenter2)
        G.add_node(commenter2)
        edge_weight = len(common_subreddits)
        G.add_edge(commenter1, commenter2, weight=edge_weight)

    # Draw the graph
    num_nodes = len(G.nodes())
    pos = nx.spring_layout(G, k=num_nodes / 3)
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_labels(G, pos, font_size=10)
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    # Show the graph
    plt.axis('off')
    plt.show()
    print("end of code")
