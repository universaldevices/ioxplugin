import argparse
import shutil
import os
from .log import init_ext_logging, IoXPluginLoggedException, PLUGIN_LOGGER


assets=[
    'install.sh',
    'tar.it',
    'POLYGLOT_CONFIG.md'
]

def create_project():
    parser = argparse.ArgumentParser(description="the path IoX plugin files")
    
    # Required positional argument
    parser.add_argument('project_path', type=str, help='path to the project directory')
    parser.add_argument('vscode_path', type=str, help='path to vscode extension files')
    
    args = parser.parse_args()

    vscode_path = args.vscode_path
    project_path = args.project_path

    # Ensure the project path exists and if not create it 
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    
    init_ext_logging(project_path)
    PLUGIN_LOGGER.info(f'creating a new project in {project_path}, assets_path is {vscode_path}')

    for asset in assets:
        try:
            shutil.copy(os.path.join(vscode_path, 'assets', asset), os.path.join(project_path,asset))
        except Exception as ex: 
            IoXPluginLoggedException('critical', "failed copying assets")


if __name__ == "__main__":
    create_project()

