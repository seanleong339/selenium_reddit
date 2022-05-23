import praw

reddit = praw.Reddit(
    client_id="1aMqUjUXh1_OU_iV2lTBmQ",
    client_secret="YmB7r_gGFj1zX5XMvGo4bS1aSeOiXw",
    user_agent="linux:tryingitout:1 (by /u/georgefoo782)",
)

url = "https://www.reddit.com/r/singapore/comments/uvcwkl/the_international_11_dota2_will_be_hosted_in/"
submission = reddit.submission(url=url)

for top_level_comment in submission.comments:
    print(top_level_comment.body)