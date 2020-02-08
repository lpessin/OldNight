import requests
import time
import datetime
import csv


class Stream:
    """
        New comments stream of all claims from a list of channels.

        Finds all discord ids under a channel name and add it as a list to the stream generator.

    """
    @staticmethod
    def get_channels():
        """
        Open the register file and lists unique channel names.

        :return: channels list
        """
        channels = []
        with open('channels_list', mode='r') as C:
            reader = csv.reader(C)
            for item in reader:
                channels.append(item[1])
        channels = list(dict.fromkeys(channels))
        print('Get channels..', channels)
        return channels

    @staticmethod
    def get_name(claim_id):
        """
        Call claim search and find the signing channel name.

        :param claim_id: Claim id (int)
        :return: Signing channel name of the claim (str)
        """
        call = requests.post("http://localhost:5279",
                             json={"method": "claim_search",
                                   "params": {'claim_id': claim_id}}).json()
        response = call['result']['items']
        for item in response:
            name = item['signing_channel']['name']
            return name

    @staticmethod
    def get_url(claim_id):
        """
        Call claim search and find permanent url.

        :param claim_id: Claim id (int)
        :return: Permanent url (str)
        """
        call = requests.post("http://localhost:5279",
                             json={"method": "claim_search",
                                   "params": {'claim_id': claim_id}}).json()
        response = call['result']['items']
        for item in response:
            url = item['permanent_url']
            return url

    @staticmethod
    def get_discord_id(channel):
        """
        Makes a list of all discord ids under a channel

        :param channel: Channel name (str)
        :return: Discord ids (list, str)
        """
        discord_ids = []
        with open('channels_list', mode='r') as C:
            reader = csv.reader(C)
            for row in reader:
                if row[1] == channel:
                    discord_ids.append(row[0])
        return discord_ids

    def get_claims_ids(self):
        """
        Calls claim search and find all claim ids from all unique channels listed.

        :return: Claim ids (generator, int)
        """
        channels = self.get_channels()
        for item in channels:
            try:
                call = requests.post("http://localhost:5279",
                                     json={"method": "claim_search",
                                           "params": {'channel': item,
                                                      'page_size': 99999}}).json()
                response = call['result']['items']
                for claim in response:
                    ids = claim['claim_id']
                    yield ids
            except Exception:
                print(Exception)
                continue

    def get_comments(self, sleep):
        """
        Calls comment list from all claim ids inside get_claims_ids() generator.
        In timestamp blocks, yields a new comment if exists.

        Block size: Sleep time + time to complete the task (gap)

        :param sleep: Sleep time (int)
        :return: New comment (generator)
        """
        gap = 0
        while True:
            head_time = datetime.datetime.now()
            claims_id = self.get_claims_ids()
            start = time.time()
            for claim in claims_id:
                call = requests.post("http://localhost:5279",
                                     json={"method": "comment_list",
                                           "params": {"claim_id": claim,
                                                      "page_size": 99999}}).json()
                try:
                    response = call['result']['items']
                    for comment in response:
                        timestamp = datetime.datetime.fromtimestamp(comment['timestamp'])
                        if timestamp >= head_time - datetime.timedelta(seconds=gap) - datetime.timedelta(seconds=sleep):
                            try:
                                name = comment['channel_name']
                            except Exception:
                                name = '@Anonymous'
                            parent = self.get_name(claim)
                            if name != parent:
                                content = comment['comment']
                                url = self.get_url(claim)
                                discord_ids = self.get_discord_id(parent)
                                result = [timestamp, name, url, content, discord_ids]
                                # print('Getting comments.................\n', result)
                                yield result
                except Exception:
                    print(Exception)
                    continue
            end = time.time()
            gap = end - start
            block_size = sleep + gap
            print('Block Size: {0:.3f}\nGap Size: {1:.3f}'.format(block_size, gap))
            print('Sleeps: ', sleep)
            time.sleep(sleep)

    print('OLD NIGHT: Online ')


class OldNight:
    """
        Perform calls on lbry-sdk

    """
    @staticmethod
    def get_channel_info(channel):
        """
        Feeds !lookchannel

        :param channel:
        :return:
        """
        try:
            call = requests.post("http://localhost:5279",
                                 json={"method": "claim_search",
                                       "params": {'channel': channel,
                                                  'page_size': 99999}}).json()
            response = call['result']['items']

            channel_data = response[0]['signing_channel']
            address = channel_data['address']
            camount = channel_data['amount']
            curl = channel_data['short_url']
            cid = channel_data['claim_id']
            op = channel_data['claim_op']
            txid = channel_data['txid']
            #
            channel_value = channel_data['value']
            try:
                site = channel_data['website_url']
            except Exception:
                site = ''
            try:
                email = channel_data['email']
            except Exception:
                email = ''
            public_key = channel_value['public_key']
            public_key_id = channel_value['public_key_id']
            try:
                thumb = channel_value['thumbnail']['url']
            except Exception:
                thumb = ''
            #
            channel_meta = channel_data['meta']
            height = channel_meta['activation_height']
            claims = channel_meta['claims_in_channel']
            since = datetime.datetime.fromtimestamp(channel_meta['creation_timestamp'])
            eamount = channel_meta['effective_amount']
            reposts = channel_meta['reposted']
            samount = channel_meta['support_amount']
            trending_gl = channel_meta['trending_global']
            trending_gr = channel_meta['trending_group']
            trending_lo = channel_meta['trending_local']
            trending_mx = channel_meta['trending_mixed']
            trend = [trending_gl, trending_gr, trending_lo, trending_mx]
            #
            timestamp = []
            amount_in_claims = 0
            support_in_claims = 0
            for claim in response:
                amount = float(claim['amount'])
                support_amount = float(claim['meta']['support_amount'])
                amount_in_claims += amount
                support_in_claims += support_amount
                timestamp.append(datetime.datetime.fromtimestamp(claim['timestamp']))

            last_publish = max(timestamp)

            return [[address, 'Channel address:'],
                    [since, 'Created:'],
                    [last_publish, 'Last Publish:'],
                    [claims, 'Total Claims Under Channel:'],
                    [curl, 'LBRY Channel url:'],
                    [site, 'Web Site:'],
                    [email, 'E-mail'],
                    [camount, 'Channel Amount (LBC):'],
                    [samount, 'Channel Support Amount (LBC):'],
                    [eamount, 'Channel Effective Amount (LBC)'],
                    [amount_in_claims, 'Total amount in claims (LBC):'],
                    [support_in_claims, 'Total support in claims (LBC):'],
                    [trend, 'Trending Index (Global, Group, Local, Mixed):'],
                    [height, 'Channel Height:'],
                    [cid, 'Channel Claim id:'],
                    [txid, 'Channel txid:'],
                    [public_key, 'Channel Public Key:'],
                    [public_key_id, 'Channel Public Key id:'],
                    [op, 'Channel Claim op:'],
                    [reposts, 'Reposted:'],
                    [thumb, 'Thumbnail:']]
        except Exception:
            return False

    @staticmethod
    def get_claim_info(name):
        name = name.replace('lbry://', '')
        e = name.find('/') + 1
        name = name[e:]
        e = name.find('#')
        name = name[:e]
        try:
            call = requests.post("http://localhost:5279",
                                 json={"method": "claim_search",
                                       "params": {'name': name,
                                                  'page_size': 99999}}).json()
            claim_data = call['result']['items'][0]
            address = claim_data['address']
            amount = claim_data['amount']
            op = claim_data['claim_op']

            claim_meta = claim_data['meta']
            created = datetime.datetime.fromtimestamp(claim_meta['creation_timestamp'])
            support = claim_meta['support_amount']
            height = claim_meta['take_over_height']
            trend_gl = claim_meta['trending_global']
            trend_gr = claim_meta['trending_group']
            trend_lo = claim_meta['trending_local']
            trend_mx = claim_meta['trending_mixed']
            trend = [[trend_gl, 'Trending Global:'],
                     [trend_gr, 'Trending Group'],
                     [ trend_lo, 'Trendind Local'],
                     [trend_mx, 'Trending Mixed']]

            try:
                owner = claim_data['signing_channel']['name']
            except Exception:
                owner = '@Anonymous'
            #
            claim_value = claim_data['value']
            stream_type = claim_value['stream_type']
            media_type = claim_value['source']['media_type']
            sd_hash = claim_value['source']['sd_hash']
            try:
                tags = claim_value['tags']
            except Exception:
                tags = ['none']
            try:
                thumb = claim_value['thumbnail']['url']
            except Exception:
                thumb = 'none'
            title = claim_value['title']
            try:
                email = claim_data['signing_channel']['value']['email']
            except Exception:
                email = 'none'
            try:
                license = claim_value['license']
            except Exception:
                license = 'none'

            return [[title, 'Title:'],
                    [owner, 'Claim Owner:'],
                    [created, 'Created:'],
                    [amount, 'Amount on Stream (LBC):'],
                    [support, 'Support on Stream (LBC):'],
                    [trend, 'Trending Index (Global, Group, Local, Mixed):'],
                    [tags, 'Tags:'],
                    [stream_type, 'Stream Type:'],
                    [media_type, 'Media Type:'],
                    [sd_hash, 'sd_hash:'],
                    [license, 'license'],
                    [op, 'Claim op:'],
                    [email, 'email'],
                    [height, 'Claim Height:'],
                    [address, 'Stream Address:'],
                    [thumb, 'Thumbnail:']]
        except Exception:
            return False
