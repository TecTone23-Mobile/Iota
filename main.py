# IOTA - Management toolkit for TecTone 23
# Author: Artur Z  (HUSKI3 @ gh)
# Date: 10/12/2021

from iota_core import shell, builder
import sys
from time import sleep

# Config locations
config = "android.yaml"
cogs   = "cogs.json"

# Source
# Moved from android.yaml to here due to Bash being dumb
import os, subprocess
if os.path.isfile("build/envsetup.sh"):
    command = 'env -i sh -c "source build/envsetup.sh && env"'
    for line in subprocess.getoutput(command).split("\n"):
        key, value = line.split("=")
        os.environ[key]= value

# Here we can modify the builder to our heart's content
class AndroidBuilder(builder):
  
  def __init__(self, config_path, cog_path, shell) -> None:
    # Init Shell
    self.shell = shell
    # Init our builder
    builder.__init__(self,
      config_path=config_path,
      cog_path=cogs,
      shell=self.shell
    )

    def print(*args):
      x = []
      for i in args:
        x.append(str(i))
      for_discord = ' '.join(x)
      # Sleep to remove rate limiting on webhook
      sleep(1)
      self.function('discord','create_hook', for_discord).send()
      self.shell.pout(*args)

    # Process our config
    # Use proc_load to process our custom yaml syntax first into pre
    print(f'Loading Config at {config_path}')
    pre = self.function('yaml','proc_load',config, self.config)

    
    # Prep for build
    # create_hook
    print(f'Getting repos to build')
    try:
      self.repos = self.function('repo','get_repos','TecTone23-Mobile')
      self.tobuild = self.repos.tagged('autobuild')
      for repo in self.tobuild:
        print(repo, self.tobuild[repo])
    except Exception as e:
      self.function('discord','create_hook', f"Failed due to {e}").send()
      print('Skipping repos due to GitHub rate-limiting')
      
    
    
    # Now we have a dictionary of repos that we need to build
    #

      # Let's convert them to a folder structure using the folders cog
      #path = self.function('folders','from_name',
      #              repo,     # Folder to create
      #              '_',      # Seperator
      #              './.',    # Ignore this case
      #              'platform' 
      #             )
      #self.tobuild[repo].clone(path)

  def run(self):    
    self.function('discord','create_hook', f"Target: [Build]").send()
    ret = self.script('build','mono',None)
    if ret[0] == 1:
      self.function('discord','create_hook', f"Failed due to {ret[1]}").send()

_ = shell(cog_path=cogs)
builder = AndroidBuilder(config, cogs, _)

if __name__ == "__main__":
  args = sys.argv[1:]
  if args:
    builder.run()
  else:
    _.pout("==> Loaded in console mode")
    _()