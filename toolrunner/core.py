"""
toolrunner v1.0.0
Author: LLCZ00

Drag and drop the target file to automatically run it through the defined tools.

"""

import subprocess, sys, os   


def get_argv(index=1):
    """Retrieve argument(filepath) from argv[*index*]"""
    try:
        argument = sys.argv[index]
    except IndexError:
        raise Exception("No filepath argument given")
    return argument
    
def run(args, new_proc: bool = False, **kwargs):
    """Wrapper for subprocess.run/Popen"""
    if new_proc:
        return subprocess.Popen(args, **kwargs)
    return subprocess.run(args, **kwargs)


class _OutputHandle:
    """Class for handling the output for subprocess.run/Popen's 'stdout' argument."""   
    def __init__(self, file, dir, ext=".txt", delim="_"):
        self.output_path = None       
        if file is not None:                                      # Turn tool name into output file name 
            self.output_path = f"{file.replace(' ', delim)}{ext}" # Replaces spaces with delimiter, add extension
            if dir is not None:
                if not os.path.exists(dir): # Create output directory if it was defined but doesn't exit            
                    os.mkdir(dir)
                self.output_path = os.path.abspath(os.path.join(dir, self.output_path))
                
    def __enter__(self):
        self.handle = None
        if self.output_path is not None:
            self.handle = open(self.output_path, "w+")
        return self.handle
            
    def __exit__(self, type, val, traceback):
        if self.handle is not None:
            self.handle.close()


class Tools:
    """Class for collecting tool configurations and spawning their processes"""
    default_output_dir = None
    default_tools = {
        "cli" : {}, # GUI tools, no output data, run in new process
        "gui" : {}, # CLI tools, output to file
        "cmd" : {}  # Cmd commands (netstat, tasklist, etc.)
        }
    def __init__(self, target: str = None, output_dir: str = None, config: dict = dict(), verbose: bool = True):
        self.tools = self.default_tools
        self.output_handle = None
        self.target = target
        self.output_dir = output_dir
        self.verbose = verbose
        
        if len(config) != 0:
            if type(config) is not dict:           
                raise Exception("tools argument must be a dictionary")
            self.tools = config
        
        if self.output_dir is None and self.default_output_dir is not None:
            self.output_dir = self.default_output_dir        

    """ Methods for adding tools """
    
    def add_tool(self,
        name: str,
        path: str,
        args: list,
        tool_type: str):
        """Add tool to tools dictionary, by tool type"""
        self.tools[tool_type][name] = [path]
        for arg in args:
            self.tools[tool_type][name].extend(arg.split(" ")) # Spliting arguments by whitespace (if left in)
                                                               # Spaces in arguments will cause undefined behavior in tools
    def cli(self, 
        name: str, 
        path: str, 
        args: list = []):
        """Add CLI tool to tools dictionary"""
        self.add_tool(name=name, path=path, args=args, tool_type="cli")
        
    def gui(self, 
        name: str, 
        path: str, 
        args: list = []):
        """Add CLI tool to tools dictionary"""
        self.add_tool(name=name, path=path, args=args, tool_type="gui")
        
    def cmd(self, 
        name: str, 
        args: list = []):
        """Add cmd/shell command to tools dictionary"""
        self.add_tool(name=name, path=name, args=args, tool_type="cmd")
  
    """ Methods for running tools """
  
    def run_type(self, 
        tool_type: str, 
        input_target: bool, 
        output: bool, 
        new_proc: bool,
        **kwargs):
        """Run all tools of the given tool_type"""
        
        if tool_type not in self.tools.keys():
            return None
        
        for tool in self.tools[tool_type]:
            if self.verbose:
                print(f"[**] Running {tool}...\n")
            
            name = tool
            command = self.tools[tool_type][tool].copy()
            
            if input_target and self.target is not None: # Add target/input file to the end of the command, if applicable
                command.append(self.target)   
            if not output:
                name = None
                
            with _OutputHandle(name, self.output_dir) as stdout: # Either a handle to the output file, or None (stdout)
                if new_proc:
                    subprocess.Popen(command, **kwargs)
                else:
                    subprocess.run(command, stdout=stdout, **kwargs)
            if self.verbose:
                print(f"\n[OK] {tool} complete\n")

    def run_cli(self, 
        input_target: bool = True, 
        output: bool = True, 
        new_proc: bool = False,
        **kwargs):
        """Run all CLI-type tools"""
        self.run_type(tool_type="cli", input_target=input_target, output=output, new_proc=new_proc, **kwargs)
        
    def run_gui(self, 
        input_target: bool = True, 
        output: bool = False, 
        new_proc: bool = True,
        **kwargs):
        """Run all GUI-type tools"""
        self.run_type(tool_type="gui", input_target=input_target, output=output, new_proc=new_proc, **kwargs)
                
    def run_cmd(self, 
        input_target: bool = False, 
        output: bool = True, 
        new_proc: bool = False,
        **kwargs):
        """Run all CLI-type tools"""
        self.run_type(tool_type="cmd", input_target=input_target, output=output, new_proc=new_proc, **kwargs)
    
    def run_all(self, **kwargs):
        """Run all tools"""
        self.run_gui(**kwargs)
        self.run_cli(**kwargs)
        self.run_cmd(**kwargs)
        
    def print_config(self):
        """Print Tools dictionary in copy/pastable format"""
        print("toolrunner_config = {")
        for tool_type in self.default_tools:
            print(f"\t\"{tool_type}\" : {{")
            for tool in self.default_tools[tool_type]:
                print(f"\t\t\"{tool}\" : {self.default_tools[tool_type][tool]},")
            print("\t},")
        print("}")


if __name__ == "__main__":
    pass