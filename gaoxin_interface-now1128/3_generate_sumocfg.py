import os
from utils.config import generate_sumocfg
from utils.config import generate_additional
from utils.config import generate_E2

if __name__ == '__main__':
    project_path = os.path.abspath('./demo')
    project_name = 'new'
    output_files = 'output'
    period = 300
    begin = 0
    end = 3600
    step_length = 1
    threads = 1
    generate_additional(project_path, project_name, output_files, period)
    generate_E2(project_path,project_name,output_files,period)
    generate_sumocfg(project_path, project_name, output_files, begin, end, period, step_length, threads)
