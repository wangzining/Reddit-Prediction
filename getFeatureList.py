import csv
import json
from collections import defaultdict
import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from operator import itemgetter

def load_data():
    data = []
    label = ['image_id','unixtime','rawtime','title','total_votes','reddit_id','number_of_upvotes',\
    'subreddit','number_of_downvotes','localtime','score','number_of_comments','username',\
    'undefined1','undefined2', 'undefined3']

    with open('submissions.csv') as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            if row[0] == '#image_id':
                continue
            d = {}
            for i,elem in enumerate(row):
                if label[i]=='total_votes' or label[i]=='number_of_upvotes' or label[i]=='number_of_downvotes' or label[i]=='score' or label[i]=='number_of_comments':
                    d[label[i]] = int(elem)
                else:
                    d[label[i]] = elem
                    #judge if element it is empty
            data.append(d)
    return data

data = load_data()
comments_sorted_data = sorted(data, key=itemgetter('number_of_comments'), reverse=True)
votes_sorted_data = sorted(data, key=itemgetter('total_votes'), reverse=True)
#score_sorted_data = sorted(data, key=itemgetter('score'),reverse=True)
#upvotes_sorted_data = sorted(data, key=itemgetter('number_of_upvotes'),reverse=True)
#downvotes_sorted_data = sorted(data, key=itemgetter('number_of_downvotes'),reverse=True)


#title keyword feature
def title():
    wordCount = defaultdict(int)
    punctuation = set(string.punctuation)

    # word count in top 25000 titles with most comment numbers
    for d in comments_sorted_data[0:25000]:
        r = ''.join([c for c in d['title'].lower() if not c in punctuation])
        for w in r.split():
            wordCount[w] += 1

    # remove English stopwords
    for w in stopwords.words("english"):
        if w in wordCount:
            wordCount.pop(w)

    #print(len(wordCount))
    counts = [(wordCount[w], w) for w in wordCount]
    counts.sort()
    counts.reverse()

    # take top 1000 words to be targets
    words = [x[1] for x in counts[:1000]]
    wordId = dict(zip(words, range(len(words))))
    wordSet = set(words)

    title_comment_list = []
    for d in data:
        title_comment_num = 0
        for i,w in enumerate(words):
            if w in d['title']:
                title_comment_num = title_comment_num + (1000-i)
        title_comment_list.append(title_comment_num)

    return title_comment_list


# submission time feature
def submission():
    ID = '-1'
    submission_list = []

    # original data is sorted in image_ID, count submission times before current submission
    for d in data:
        if d['image_id'] == ID:
            count = count + 1
            d['submission_time'] = count
        else:
            count = 0
            ID = d['image_id']
            d['submission_time'] = count

    for d in data:
        submission_list.append(d['submission_time'])

    return submission_list



def get_username_profile():
    data = load_data()
    user_post_num = defaultdict(int)
    user_down_vote = defaultdict(int)
    user_up_vote = defaultdict(int)
    user_vote = defaultdict(int)
    user_comment_num = defaultdict(int)

    # get average submission popularity of users' all submissions
    for record in data:
        user_name = record.get('username')
        user_post_num[user_name] += 1
        user_comment_num[user_name] += int(record.get('number_of_comments'))
        user_down_vote[user_name] += int(record.get('number_of_downvotes'))
        user_up_vote[user_name] += int(record.get('number_of_upvotes'))
        user_vote[user_name] += int(record.get('total_votes'))

    def user_profile(user_name):
        profile = {
            'username': user_name,
            'num_of_post': user_post_num[user_name],
            'avg_comments': float(user_comment_num[user_name]) / user_post_num[user_name],
            'avg_downvotes': float(user_down_vote[user_name]) / user_post_num[user_name],
            'avg_upvotes': float(user_up_vote[user_name]) / user_post_num[user_name],
            'avg_votes': float(user_vote[user_name]) / user_post_num[user_name]
        }
        return profile

    all_user_profile = [user_profile(user) for user in user_post_num.keys()]

    with open('all_user_profile.json', 'w') as f:
        json.dump(all_user_profile, f)

#get_username_profile()


# username feature
def username():
    with open('all_user_profile.json', 'r') as f:
        all_user_profile = json.load(f)
    #post_list = []
    #user_votes_list = []
    #user_votes_dict = {}
    user_comment_list = []
    user_comment_dict = {}
    for user in all_user_profile:
        #post_list.append(user.get('num_of_post'))
        #user_votes_dict[user.get('username')] = user.get('avg_votes')
        user_comment_dict[user.get('username')] = user.get('avg_comments')

    for d in data:
        if d['username']=='':
            user_comment_list.append(d['number_of_comments'])
        elif d['username'] in user_comment_dict:
            user_comment_list.append(user_comment_dict[d['username']])
        #if d['username'] in user_votes_dict:
            #user_votes_list.append(user_votes_dict[d['username']])

    return user_comment_list




def get_subreddit_profile():
    data = load_data()
    sub_post_num = defaultdict(int)
    sub_down_vote = defaultdict(int)
    sub_up_vote = defaultdict(int)
    sub_vote = defaultdict(int)
    sub_comment_num = defaultdict(int)

    for d in data:
        sub = d.get('subreddit')
        sub_post_num[sub] += 1
        sub_comment_num[sub] += int(d.get('number_of_comments'))
        sub_down_vote[sub] += int(d.get('number_of_downvotes'))
        sub_up_vote[sub] += int(d.get('number_of_upvotes'))
        sub_vote[sub] += int(d.get('total_votes'))

    def subreddit_profile(sub):
        profile = {
            'subreddit': sub,
            'num_of_post': sub_post_num[sub],
            'avg_comments': float(sub_comment_num[sub]) / sub_post_num[sub],
            'avg_downvotes': float(sub_down_vote[sub]) / sub_post_num[sub],
            'avg_upvotes': float(sub_up_vote[sub]) / sub_post_num[sub],
            'avg_votes': float(sub_vote[sub]) / sub_post_num[sub]
        }
        return profile

    all_subreddit_profile = [subreddit_profile(sub) for sub in sub_post_num.keys()]
    with open('all_subreddit_profile.json', 'w') as f:
        json.dump(all_subreddit_profile, f)


#subreddit feature
def subreddit():
    with open('all_subreddit_profile.json', 'r') as f:
        all_subreddit_profile = json.load(f)
    #post_list = []
    sub_comment_list = []
    sub_comment_dict = {}
    sub_votes_list = []
    sub_votes_dict = {}
    for sub in all_subreddit_profile:
        # post_list.append(sub.get('num_of_post'))
        #sub_votes_dict[sub.get('subreddit')] = sub.get('avg_votes')
        sub_comment_dict[sub.get('subreddit')] = sub.get('avg_comments')

    for d in data:
        if d['subreddit']=='':
            sub_comment_list.append(d['number_of_comments'])
        elif d['subreddit'] in sub_comment_dict:
            sub_comment_list.append(sub_comment_dict[d['subreddit']])
        #if d['subreddit'] in sub_votes_dict:
            #sub_votes_list.append(sub_votes_dict[d['subreddit']])

    return sub_comment_list


title_comment_list = title()
submission_list = submission()
user_comment_list = username()
sub_comment_list = subreddit()

comment_feature_list = []
comment_label_list = []
for i in range(len(data)):
    comment_feature_list.append([title_comment_list[i],submission_list[i],user_comment_list[i],sub_comment_list[i]])
    comment_label_list.append(data[i]['number_of_comments'])

print "feature[title_keyword,submission_time,username,subreddit]:",comment_feature_list[0]
print "label[comment_number]:",comment_label_list[0]