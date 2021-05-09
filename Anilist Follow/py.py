import requests, re, time, random

# your remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d cookie
cookie = ""

with requests.Session() as session:
    session.cookies["remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d"] = cookie

def token():
    return re.findall(r"token = \"(.+)\";", session.get("https://anilist.co/user/vev/").text)[0]

def activity(id):
    data = {
        "query": "query($id:Int,$type:ActivityType,$page:Int){Page(page:$page,perPage:25){pageInfo{total perPage currentPage lastPage hasNextPage}activities(userId:$id,type:$type,sort:ID_DESC){... on ListActivity{id type replyCount status progress isLocked isSubscribed isLiked likeCount createdAt user{id name avatar{large}}media{id type status(version:2)isAdult bannerImage title{userPreferred}coverImage{large}}}... on TextActivity{id type text replyCount isLocked isSubscribed isLiked likeCount createdAt user{id name avatar{large}}}... on MessageActivity{id type message replyCount isPrivate isLocked isSubscribed isLiked likeCount createdAt user:recipient{id}messenger{id name donatorTier donatorBadge moderatorStatus avatar{large}}}}}}",
        "variables": {"id": id}
    }

    r = session.post('https://anilist.co/graphql', headers={'x-csrf-token': token()}, json=data).json()
    activity = [i["createdAt"] for i in r["data"]["Page"]["activities"]]
    return sorted(activity)

def follow(id):
    headers = {
        'sec-fetch-mode': 'cors',
        'origin': 'https://anilist.co',
        'schema': 'default',
        'x-csrf-token': token(),
        'accept-language': 'en-US,en;q=0.9,es;q=0.8',
        'sec-fetch-dest': 'empty',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'content-type': 'application/json',
        'accept': '*/*',
        'referer': 'https://anilist.co/b1a3107d3ca41c0d3808.worker.js',
        'authority': 'anilist.co',
        'sec-fetch-site': 'same-origin',
    }

    data = {
        "query": "mutation($id:Int){ToggleFollow(userId:$id){id name isFollowing}}",
        "variables": {"id": id}
    }

    r = session.post('https://anilist.co/graphql', headers=headers, json=data).json()
    print(r)
    if "errors" in r:
        if "Too many follows" in r["errors"][0]["message"]:
            print("ratelimit reached, trying to follow user again.")
            return follow(id)
    with open(".id", "w") as f:
        f.write(f"{id}")

with open(".id", "r") as f:
    lastId = int(f.readline())

lastFollow = int(time.time())
timeWaited = 0
for i in range(lastId + 1, 1000000):
    try:
        act = activity(i)
        print(act)
        if act: # check if list isnt empty
            if act[-1] > 1614934132: # check if less than a month ago
                follow(i)
                time.sleep(35)
    except Exception as e:
        print(e)
