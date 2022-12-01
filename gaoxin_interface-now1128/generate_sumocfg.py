import os
from optparse import OptionParser
import sys
from utils.config import generate_sumocfg
from utils.config import generate_additional
from utils.config import generate_E2

def get_index(args=None):
    optParser = OptionParser()
    optParser.add_option("-p","--period",dest="period",type=int,help="the period/s of simulation")
    (options,args) = optParser.parse_args(args=args)
    if options.period is None:
        sys.exit(1)
    return options.period


if __name__ == '__main__':
    """
    默认存在本地
    """
    project_path = os.path.abspath('./demo')
    project_name = 'new'
    output_files = 'output'
    period = int(get_index())
    #period = 300 # 在sumocfg中无用 additional有用
    begin = 0
    end = begin + period
    step_length = 1
    threads = 1
    generate_additional(project_path, project_name, output_files, period)
    generate_E2(project_path,project_name,output_files,period)
    generate_sumocfg(project_path, project_name, output_files, begin, end, period, step_length, threads)
