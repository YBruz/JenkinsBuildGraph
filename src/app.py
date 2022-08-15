import os
import sys
import getopt
from jenkinsfunc import JenkinsWrapper
import plotly.express as px
import pandas as pd

def print_help():
    print('application usage documentation:')
    print('--url="http://foobar/"   : url to jenkins server')
    print('--agents="foo,bar"       : comma seperated list of agents')
    print('--builds=50              : amount of builds to parse per agent')
    print('-h                       : prints this usage documentation')

def main(argv):

    print('running application ...')

    # params
    url = ''
    agents = []
    maxBuilds = 50

    # parse commandline args
    print('parsing commandline arguments ...')
    try:
        opts, args = getopt.getopt(argv, "", ["help",  "url=", "agents=", "builds="])
    except:
        print('failed to start application, unable to parse commandline arguments.')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--help':
            print_help()
            sys.exit()
        elif opt == '--url':
            url = arg
        elif opt == '--agents':
            agents = arg.strip('\"').split(',')
        elif opt == '--builds':
            maxBuilds = int(arg)

    # connect to jenkins
    print('')
    jenkins = JenkinsWrapper(url)
    jenkins.connect()

    print('\nretrieving jenkins agents')
    jenkins.getAgents()

    print('\nretrieving jenkins agents build history')
    for agent in jenkins.agents:
        if len(agents) == 0 or agent in agents:
            jenkins.getAgentBuildData(agent, maxBuilds)

    print(f'finished retrieving {len(jenkins.buildData)} builds')

    # setup dataframe
    df = pd.DataFrame([vars(c) for c in jenkins.buildData])
    print(df)

    fig = px.timeline(
        df, 
        title="Jenkins Build Graph",
        x_start="start", 
        x_end="end",    
        y="executor", 
        hover_data=['executor', 'title', 'duration', 'result'], 
        color='result',
        color_discrete_map={ "SUCCESS": "Green", "FAILURE": "Red", "None": "Gray"},
        template="simple_white"
    )

    fig.update_yaxes(
        dtick=0,
        ticklen=10,
        fixedrange=True
    )

    fig.show()

    htmlfile = f"{os.path.dirname(__file__)}\JenkinsBuildGraph.html"
    print(f"writing graph to file \'{htmlfile}\'")
    fig.write_html(htmlfile)

if __name__ == "__main__":
    main(sys.argv[1:])

    