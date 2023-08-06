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

    def _find_ino_file(self):
        project_dir = os.path.dirname(self._get_filename())

        # The .ino file is probably in the current directory,
        # but maybe it's in the parent directory
        for i in range(3):
            ino_files = glob.glob(os.path.join(project_dir, SKETCH_FILE_PATTERN))
            if len(ino_files) == 1:
                return os.path.normpath(ino_files[0])
            project_dir = os.path.dirname(project_dir)
        
        raise ValueError("There should be exactly one .ino file in the project directory")
        
    def _get_filename(self):
        return sublime.active_window().active_view().file_name()
        
    def _is_ino_file(self):
        return self._get_filename().endswith(SKETCH_FILE_EXTENSTION)
        
    def go(self, options):

        exec_path = get_setting('path')
        if "?" in exec_path or "*" in exec_path:
            exec_paths = glob.glob(exec_path)
            assert len(exec_paths) == 1, "There should be only one compiler matching the given path (See arduino-cli (Platform).sublime-settings file"
            exec_path = exec_paths[0]

        if self._is_ino_file():
            ino_file = self._get_filename()
        else:
            ino_file = self._find_ino_file()

        project_dir = os.path.dirname(ino_file)

        args = [exec_path]
        args += ["--no-color"]

        board = get_setting('board')
        port = get_setting('port')
        libs = get_setting("libraries")

        if options["cmd"][0] == "build":
            args += ["compile"]
            args += ["--fqbn", board]
            for lib in libs:
                if os.path.exists(os.path.abspath(lib)):
                    args += ["--library", os.path.abspath(lib)]
                else:
                    args += ["--library", os.path.abspath(os.path.join(project_dir, lib))]

        elif options["cmd"][0] == "upload":
            args += ["upload"]
            args += ["--fqbn", board]
            args += ["-p", port]

        elif options["cmd"][0] == "monitor":
            args += ["monitor"]
            args += ["-p", port]

        
        args += [ino_file]

        options['cmd'] = args

        print(options)
        #print(args)


        self.window.run_command("exec", options)
