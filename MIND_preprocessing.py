import csv
from collections import defaultdict
import pickle
import random

#loading data
dir_data = './MINDsmall_train/'
path_data = dir_data + "behaviors.tsv"
data_file = open(path_data, 'rb')
tsv_file = open(path_data)
behaviors = csv.reader(tsv_file, delimiter="\t")



history_u_lists = defaultdict(list)

users_set = set()
news_set = set()
users_dict = dict()
news_dict = dict()

count = 0
for row in behaviors:
    if(len(users_set) >= 7000):
        break
    users_set.add(row[1])
    count=count+1
    news_list = row[4].split(' ')
    ratings_list = [None] * len(news_list)
    for i in range(len(news_list)):
        ratings_list[i] = ord(news_list[i][-1]) - 48
        news_list[i] = news_list[i][:-2]
        news_set.add(news_list[i])
print("STOPPING TIME = %d" % count)
print(len(users_set))
print(len(news_set))

count = 0
for el in users_set:
    users_dict[el] = count
    count=count+1
print(type(users_dict))

count = 0
for el in news_set:
    news_dict[el] = count
    count=count+1
print(type(news_dict))

with open('./data/users_news_dict.pickle', 'wb') as f:
    pickle.dump(users_dict, f)
    pickle.dump(news_dict, f)
    f.close()

with open('./data/users_news_dict.pickle', 'rb') as f:
    users = pickle.load(f)
    news = pickle.load(f)
    f.close()
print(type(users), type(news))
print(users, news)






"""
string = 'N49180-0 N41020-0 N7319-0 N21656-0 N62360-0 N32544-0 N63970-0 N50675-0 N48019-0 N48046-0 N20069-0 N33619-1'
news_list = string.split(' ')
ratings_list = [None] * len(news_list)
for i in range(len(news_list)):
    ratings_list[i] = ord(news_list[i][-1]) - 48
    news_list[i] = news_list[i][:-2]
    news_set.add(news_list[i])
print(news_list)
print(ratings_list)

"""


#users, news dict
with open('./data/users_news_dict.pickle', 'rb') as f:
    users_dict = pickle.load(f)
    news_dict = pickle.load(f)
    f.close()

#print(news_dict['N55689'])

history_u_lists = defaultdict(list)
history_ur_lists = defaultdict(list)
history_v_lists = defaultdict(list)
history_vr_lists = defaultdict(list)

count = 0
STOPPING_TIME = 7825 #see MIND_preprocessing.py
for row in behaviors:
    if count == STOPPING_TIME:
        break
    user_number = users_dict[row[1]]
    count = count+1

    raw_news_list = row[4].split(' ')
    ratings_list = [None] * len(raw_news_list)
    news_list = []
    for i in range(len(raw_news_list)):
        ratings_list[i] = ord(raw_news_list[i][-1]) - 48
        raw_news_list[i] = raw_news_list[i][:-2]
        #print(raw_news_list[i])
        news_list.append(news_dict[raw_news_list[i]])
        history_v_lists[news_dict[raw_news_list[i]]].append(user_number)
        history_vr_lists[news_dict[raw_news_list[i]]].append(ratings_list[i])

    for i in range(len(news_list)):
        history_u_lists[user_number].append(news_list[i])
        history_ur_lists[user_number].append(ratings_list[i])


print(type(history_u_lists))
history_u_lists_items = list(history_u_lists.items())
history_ur_lists_items = list(history_ur_lists.items())
"""print(list(history_v_lists_items)[:10])
print(list(history_vr_lists_items)[:10])"""

with open('./data/history_u_lists.pickle', 'wb') as f:
    pickle.dump(history_u_lists, f)
    f.close()

num_of_samples = 25000
u = list()
v = list()
r = list()
for i in range(num_of_samples):
    user, related_news = random.choice(history_u_lists_items)
    related_ratings = history_ur_lists[user]
    #print(len(related_news), len(related_ratings))
    selector = random.randint(0, len(related_news) - 1)
    #print(selector)
    news = related_news[selector]
    rating = related_ratings[selector]

    u.append(user)
    v.append(news)
    r.append(rating)

print(type(u), type(v), type(r))
print(u[:20])
print(v[:20])
print(r[:20])

#train test split
split = int(0.8*len(u))
train_u = u[:split]
train_v = v[:split]
train_r = r[:split]

test_u = u[split:]
test_v = v[split:]
test_r = r[split:]

print(len(train_u), len(test_u))

ratings_list = {0.0: 0, 1.0: 1}

#building social graph
THRESHOLD = 10
social_adj_lists = defaultdict(set)
for i in range(len(history_u_lists_items)):
    if i % 100 == 0:
        print("iter = %d\n" % (i))
    for j in range(len(history_u_lists_items)):
        intersection = len(set.intersection(set(history_u_lists[i]), set(history_u_lists[j])))
        if i != j & intersection >= THRESHOLD:
            social_adj_lists[i].add(j)

print(list(social_adj_lists.items())[:10])


data = [history_u_lists, history_ur_lists, history_v_lists, history_vr_lists, train_u, train_v, train_r, test_u, test_v,
        test_r, social_adj_lists, ratings_list]

with open('./data/MIND_small_dataset.pickle', 'wb') as f:
    pickle.dump(data, f)
    f.close()