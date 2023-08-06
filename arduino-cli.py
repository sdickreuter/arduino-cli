import subprocess, sublime, sublime_plugin
import os
import glob

SKETCH_FILE_EXTENSTION = ".ino"
SKETCH_FILE_PATTERN = "*.ino"

def get_setting(name):
    settings = sublime.load_settings('arduino-cli.sublime-settings')
    return sublime.active_window().active_view().settings().get(name, settings.get(name))

class ArduinocliCommand(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        sublime.set_timeout_async(lambda: self.go(kwargs), 0)

    def _find_ino_file(self, filename):
        project_dir = os.path.dirname(filename)
        
        # The .ino file is probably in the current directory,
        # but maybe it's in the parent directory
        for d in [".", ".."]:
            ino_files = glob.glob(os.path.join(project_dir, d, SKETCH_FILE_PATTERN))
            if len(ino_files) == 1:
                return os.path.normpath(ino_files[0])
        
        raise ValueError("There should be exactly one .ino file in the project directory")
        
    def _get_filename(self):
        return sublime.active_window().active_view().file_name()
        
    def _set_ino_file(self, cmd):
        filename = self._get_filename()
        cmd[cmd.index(filename)] = self._find_ino_file(filename)
        
    def _is_ino_file(self):
        return self._get_filename().endswith(SKETCH_FILE_EXTENSTION)
        
    def go(self, options):

        exec_path = get_setting('path')
        if "?" in exec_path or "*" in exec_path:
            exec_paths = glob.glob(exec_path)
            assert len(exec_paths) == 1, "There should be only one compiler matching the given path (See arduino-cli (Platform).sublime-settings file"
            exec_path = exec_paths[0]

        args = [exec_path]
        args += ["--no-color"]

        board = get_setting('board')
        port = get_setting('port')
        libs = get_setting("libraries")

        if options["cmd"][0] == "build":
            args += ["compile"]
            args += ["--fqbn", board]
            for lib in libs:
                args += ["--library", lib]

        elif options["cmd"][0] == "upload":
            args += ["upload"]
            args += ["--fqbn", board]
            args += ["-p", port]

        elif options["cmd"][0] == "monitor":
            args += ["monitor"]
            args += ["-p", port]

        cmd = options['cmd']
        
        if not self._is_ino_file():
            self._set_ino_file(cmd)
        
        print(options['cmd'])
        print(args)

        options['cmd'] = args

        self.window.run_command("exec", options)
