import jenkins
import feedparser
import requests
import json
import datetime

class JenkinsBuildEntry:
    executor = ''
    title = ''
    url = ''
    buildNumber = 0
    isBuilding = False
    result = ''
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime(1970, 1, 1)
    duration = 0.0
    
    def __init__(self, executor, title, url, buildNumber, isBuilding, result, start, duration):
        self.executor = executor
        self.title = title
        self.url = url
        self.buildNumber = buildNumber
        self.isBuilding = isBuilding
        self.result = result

        self.duration = duration
        self.start = datetime.datetime.fromtimestamp(start/1000.0)
        self.end = self.start + datetime.timedelta(milliseconds=self.duration)

class JenkinsWrapper:
    
    server = None
    agents = ["(built-in)"]
    buildData = []
    url = ''

    def __init__(self, url):
        self.url = url
    
    def connect(self):
        print('connecting to jenkins server...')
        self.server = jenkins.Jenkins(self.url)
        version = self.server.get_version()
        print(f'connected to jenkins {version} running on {self.url}')

    def getAgents(self):
        nodes = self.server.get_nodes()
        for node in nodes:
            if node['offline'] == False:
                agent_name = node['name']               
                if self.server.node_exists(agent_name):
                    print(f'found agent: {agent_name}')
                    self.agents.append(agent_name)

                

    def getAgentBuildData(self, agent, maxEntries = 25):
        print(f'retrieving RSS builds for agent \'{agent}\' ...')
        if agent not in self.agents:
            print(f'unable to retrieve RSS builds, agent \'{agent}\' not found.')
            return

        try:
            rss = self.server.jenkins_open(requests.Request("GET", f"{self.url}/computer/{agent}/rssAll"), add_crumb=False)
            allbuilds = feedparser.parse(rss)
        except:
            print('failed to retrieve RSS builds.')
            return

        count = 0
        for build in allbuilds.entries:
            if count >= maxEntries:
                break
            try:
                title = build['title']
                url =  build['link']
                buildNum = int(url.split('/')[-2])

                print(f'retrieving info for build \'{title}\' #{buildNum} ...')

                buildInfo = self.server.jenkins_open(requests.Request("GET", f"{url}/api/json"), add_crumb=False)
                buildInfo = json.loads(buildInfo)
                title = buildInfo['fullDisplayName'].split('»')[-1].split('#')[0]
                isBuilding = bool(buildInfo['building'])
                result = buildInfo['result']
                timestamp = buildInfo['timestamp']
                duration = buildInfo['duration']
                if isBuilding:
                    duration = buildInfo['estimatedDuration']

                self.buildData.append(JenkinsBuildEntry(agent, title, url, buildNum, isBuilding, result, timestamp, duration))
                count += 1
            except Exception as e:
                print(f'failed to retrieve/parse build info with exception:\n{e}.')