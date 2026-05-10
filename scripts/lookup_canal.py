import os, requests, json
YT_CLIENT_ID = os.environ['YT_CLIENT_ID']
YT_CLIENT_SECRET = os.environ['YT_CLIENT_SECRET']
YT_REFRESH_TOKEN = os.environ['YT_REFRESH_TOKEN']
SUPA_URL = os.environ['SUPABASE_URL']
SUPA_KEY = os.environ['SUPABASE_SERVICE_KEY']

r = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id': YT_CLIENT_ID, 'client_secret': YT_CLIENT_SECRET,
    'refresh_token': YT_REFRESH_TOKEN, 'grant_type': 'refresh_token'
}, timeout=20)
token = r.json()['access_token']

# Lookup canal new pelo handle
for handle in ['psidanielacoelho', '@psidanielacoelho']:
    print(f'\n=== Lookup: {handle} ===')
    r = requests.get('https://www.googleapis.com/youtube/v3/channels',
        params={'part':'snippet,statistics,contentDetails,brandingSettings',
                'forHandle': '@'+handle.lstrip('@'),
                'access_token': token}, timeout=20)
    print(f'HTTP {r.status_code}')
    d = r.json()
    if d.get('items'):
        ch = d['items'][0]
        print(f"  ID: {ch['id']}")
        print(f"  Title: {ch['snippet']['title']}")
        print(f"  Custom URL: {ch['snippet'].get('customUrl','?')}")
        print(f"  Subs: {ch['statistics'].get('subscriberCount','?')}")
        print(f"  Views: {ch['statistics'].get('viewCount','?')}")
        print(f"  Videos: {ch['statistics'].get('videoCount','?')}")
        print(f"  Country: {ch['snippet'].get('country','?')}")
        print(f"  Published: {ch['snippet'].get('publishedAt','?')}")
        print(f"  Desc: {ch['snippet'].get('description','')[:300]}")
        # Save to Supabase
        S = requests.Session()
        S.headers.update({'apikey':SUPA_KEY,'Authorization':f'Bearer {SUPA_KEY}','Content-Type':'application/json',
            'Prefer':'resolution=merge-duplicates,return=representation'})
        S.post(f'{SUPA_URL}/rest/v1/viral_channel_research?on_conflict=channel_id', json=[{
            'channel_id': ch['id'],
            'handle': '@psidanielacoelho',
            'title': ch['snippet']['title'],
            'description': ch['snippet'].get('description',''),
            'subscriber_count': int(ch['statistics'].get('subscriberCount',0)),
            'video_count': int(ch['statistics'].get('videoCount',0)),
            'total_view_count': int(ch['statistics'].get('viewCount',0)),
            'country': ch['snippet'].get('country',''),
            'published_at': ch['snippet']['publishedAt'],
            'keywords': 'CANAL_OFICIAL_DESTINO',
            'fetched_at': '2026-05-10T02:30:00Z'
        }], timeout=20)
        print('  ✓ Saved to viral_channel_research')
        break
    else:
        print(f'  ERROR: {json.dumps(d)[:300]}')
