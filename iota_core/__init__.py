from .ext import hot
import sys, getpass, os

class out:
  def __init__(self, c=None):
    self.console = c if c else sys.stdout

  def __call__(self, *args, newline=True) -> int:
    try:
      f_args = []
      for arg in args:
        f_args.append(str(arg))
      f_args = ' '.join(f_args) 
      _ = str(f_args)+'\n' if newline else str(f_args)
      self.console.write(_)
    except Exception as e:
      sys.stderr.write(f'[Failed] -- {e} \n')

class shell:

  def __init__(self, cog_path=None):
    """
    cog_path <- Location of defined cogs
    """
    self.vars           = {}
    self.pout           = out()
    self.user           = getpass.getuser()
    self._stayon        = True
    self.built_in       = self._load_built_ins(cog_path)
  
  def __call__(self) -> str:
    while self._stayon:
      try:
        self.pout(f'({self.user})> ', newline=False)
        _inp = input()
        self._process(_inp)
      except EOFError:
        self.pout(f'\n==> User closed channel, shutting console down...')
        quit()
  
  def _process(self,input) -> dict:
    inp = input.split(' ')
    if inp[0].split('.')[0] in self.built_in:
      # Found the function in a cog, let's get the function
      cog = self.built_in[inp[0].split('.')[0]]
      if '.' in inp[0]:
        func = inp[0].split('.')[1]
      else:
        raise Exception(f"Unkown call to reference {inp[0]}")
      cog[func](' '.join(input.split(' ')[1:]))
    else:
      self.pout(f'[IOTA] Command not found')

  def _load_built_ins(self, path) -> dict:
    imp = hot.importer()
    imp.load_cogs(path) 
    builtins = {}
    for cog in imp.get_cogs():
      builtins[cog] = {}
      for x in imp.get_cogs()[cog]:
        builtins[cog][x] = imp.get_method(cog, x)
        if builtins[cog][x] is None:
          self.pout(f"<WARNING> Method {x} in {cog} has failed to load")
    return builtins

class builder:
  def __init__(self, cog_path=None, config_path=None, shell=None, silent=False):
    """
    cog_path <- Location of defined cogs
    """
    self.vars           = {}
    self.pout           = out()
    self.user           = getpass.getuser()
    self.shell          = shell
    self.config         = self.get_config(config_path)
    self.silent         = silent

  def get_config(self, path):
    config = self.shell.built_in['yaml']['load'](path, quiet=False)
    return config

  def function(self, cog, func, *args, quiet=False):
    return self.shell.built_in[cog][func](*args, quiet=quiet)

  def script(self, script_name, project, args):                          
    if script_name in self.config['scripts'][project]:
      if 'env' in self.config['scripts'][project]:
        env_vars = self.config['scripts'][project]['env']
        for x in os.environ:
          env_vars[x] = os.environ[x]
        env_vars['PATH'] = env_vars['PATH'].replace('${PATH}',os.environ['PATH'])
      else:
        for x in os.environ:
          env_vars[x] = os.environ[x]
        env_vars['PATH'] = env_vars['PATH'].replace('${PATH}',os.environ['PATH'])
      lines = self.config['scripts'][project][script_name].split('\n')
      ret = [1, f'Failed to acquire any return statements, ran lines 0-{len(lines)}. Perhaps the script exited due to invalid formatting?']  
      for _ in lines:
        ######
        ###### TecTone only, requires discord cog
        if not self.silent: 
          self.function('discord','create_hook', f"Executing: {_}").send()
        ######
        ######

        # First we want to check if this is a 
        # shell command or we are calling a cog.
        # Default formatting follows:
        # -------------------------------------
        # | @cog > COG_NAME.FUNC_NAME (ARGS)  | -> Cog
        # -------------------------------------
        # | ANY **                            | -> Shell
        # -------------------------------------
        
        if not _: continue # Make sure it's a valid line

        if _[0] == '@':
          # We have found a cog, process it
          ar: list = _.split('>')[1:] # Remove the "@cog" at ">"
          
          # [TODO]: Shorten this
          cog_name = ar[0].split('.', 1)[0].strip()
          cog_func = ar[0].split('.', 1)[1].split('(')[0] # VERY SMART! LMAO
          cog_args = ar[0].split('.', 1)[1].split('(')[1].strip(')')

          print(
            cog_name,
            cog_func,
            cog_args,
            sep='\n'
          )

          if cog_name in self.shell.built_in and cog_func in self.shell.built_in[cog_name]:
            # If the cog is present, try to execute
            ret = self.shell.built_in[cog_name][cog_func](cog_args)

          else: raise Exception(f"[BUILDER.script] Failed to locate {cog_name}, or {cog_func} in {cog_name}, in {self.shell.built_in.keys()}")

          #self.shell.built_in

        else:
          ret = self.shell.built_in['shell']['execute'](_, quiet=False, vars=[env_vars])

        if ret[0] != 0:
          return ret
    return ret # Should be fine as long as a script that doesn't exist is called