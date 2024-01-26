import json
import math
import random


def prepare_categories():
    with open('manifest_top100_filtered.json', 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    categories = dict()
    for channel in manifest:
        cats = channel['categories']
        for cat in cats:
            val = categories.setdefault(cat, [])
            val.append(channel)

    for channel in manifest:
        cats = channel['categories']
        i = len(cats)
        while i > 1:
            min_cat_size = 9999
            remove_from = ''
            for cat in cats:
                new_min = min(len(categories[cat]), min_cat_size)
                if new_min < min_cat_size:
                    min_cat_size = new_min
                    remove_from = cat

            categories[remove_from].remove(channel)
            cats.remove(remove_from)
            i -= 1

    with open('manifest_categories.json', 'w', encoding='utf-8') as f:
        json.dump({k: v for k, v in categories.items() if len(v) > 0}, f, ensure_ascii=False)


def sample_channels_from_categories():
    with open('manifest_categories_filtered.json', 'r', encoding='utf-8') as f:
        filtered_categories = json.load(f)

    proportion = 0.2

    sample = []
    for _, channels in filtered_categories.items():
        n = math.ceil(len(channels) * proportion)
        sub_sample = random.sample(channels, n)

        sample.extend(sub_sample)

    with open('manifest_category_sample_20.json', 'w') as f:
        json.dump(sample, f, ensure_ascii=False)


def sample_channels():
    with open('manifest_top100_filtered.json', 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    random.shuffle(manifest)
    sample = random.sample(manifest, 20)
    with open('manifest_sample_20.json', 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False)


def compute_proportions():
    with open('manifest_category_sample_20.json', 'r', encoding='utf-8') as f:
        sample = json.load(f)

    n = 6000
    total_subs = sum([channel['num_subscribers'] for channel in sample])

    props = []
    for channel in sample:
        prop = channel['num_subscribers'] / total_subs
        num_users = round(n * prop)

        props.append({
            "channel_id": channel['channel_id'],
            "channel_name": channel['channel_name'],
            "channel_url": channel['channel_url'],
            "proportion": prop,
            "num_users": num_users
        })

    with open('sample_20_with_props.json', 'w', encoding='utf-8') as f:
        json.dump(props, f, ensure_ascii=False)


compute_proportions()
