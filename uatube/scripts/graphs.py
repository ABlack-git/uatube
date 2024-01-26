import json

from tqdm import tqdm
from uatube.models import Subscription
import networkx as nx
from mongoengine import connect


def build_cosubs_graph():
    connect(db='uatube', host='localhost', port=51999)
    min_subs = 3
    channels = get_unique_channels(min_subs)
    subscribers = get_subscribers()

    filter_channels(channels, subscribers)

    graph = nx.Graph()

    for channel in tqdm(channels, desc="Adding nodes to graph"):
        graph.add_node(channel['_id'], channel_title=channel['channel_title'], num_subscribers=channel['count'])

    for sub in tqdm(subscribers, desc='Adding edges to graph'):
        subscriptions = sub['channels']
        num_subs = len(subscriptions)
        for i in range(num_subs):
            if i == num_subs - 1:
                break
            u = subscriptions[i]['channel_id']
            for j in range(i + 1, num_subs):
                v = subscriptions[j]['channel_id']
                if graph.has_edge(u, v):
                    graph.edges[u, v]['num_cooccurrences'] += 1
                else:
                    graph.add_edge(u, v, num_cooccurrences=1)

    json_data = nx.adjacency_data(graph)

    with open('coocurence_graph.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False)


def get_unique_channels(min_subs):
    pipeline = [
        {
            '$group': {
                '_id': '$channel_id',
                'count': {
                    '$count': {}
                },
                'channel_title': {
                    '$first': '$channel_title'
                }
            }
        }, {
            '$match': {
                'count': {
                    '$gte': min_subs
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ]

    cursor = Subscription.objects().aggregate(pipeline)
    return list(cursor)


def get_subscribers():
    pipeline = [
        {
            '$group': {
                '_id': '$subscriber_id',
                'channels': {
                    '$push': {
                        'channel_id': '$channel_id',
                        'channel_title': '$channel_title'
                    }
                },
                'total_channels': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'total_channels': -1
            }
        }
    ]

    cursor = Subscription.objects().aggregate(pipeline)
    return list(cursor)


def filter_channels(channels, subscribers):
    channel_ids = {c['_id'] for c in channels}
    for sub in subscribers:
        sub['channels'] = list(filter(lambda x: x['channel_id'] in channel_ids, sub['channels']))
        sub['total_channels'] = len(sub['channels'])
