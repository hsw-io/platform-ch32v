from os.path import isdir, isfile, join, dirname, realpath
from string import Template
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
# import default build settings
env.SConscript("_bare.py")

FRAMEWORK_DIR = platform.get_package_dir("framework-ch32v003-sdk")
assert isdir(FRAMEWORK_DIR)


def get_flag_value(flag_name:str, default_val:bool):
    flag_val = board.get(f"build.{flag_name}", default_val)
    flag_val = str(flag_val).lower() in ("1", "yes", "true")
    return flag_val


# the linker script also uses $ on it, so we can't use that as the
# variable identifier for the substitution engine.
class CustomTemplate(Template):
    delimiter = "#"


def render_linker_script(mcu: str):
    ram = board.get("upload.maximum_ram_size", 0)
    flash = board.get("upload.maximum_size", 0)
    flash_start = int(board.get("upload.offset_address", "0x00000000"), 0)
    stack_size = int(board.get("build.stack_size", "256"))

    template_file = join(FRAMEWORK_DIR, "platformio", "ldscripts", "Link.tpl")
    content = ""

    with open(template_file) as fp:
        data = CustomTemplate(fp.read())
        content = data.substitute(
            stack=hex(0x20000000 + ram), # 0x20000000 - start address for RAM
            ram=str(int(ram/1024)) + "K",
            flash=str(int(flash/1024)) + "K",
            flash_start=hex(flash_start),
            stack_size=stack_size
        )

    ld_script_path = join(env.subst("$BUILD_DIR"), "Link.ld")
    with open(ld_script_path, "w") as fp:
        fp.write(content)

    return ld_script_path


if get_flag_value("use_lto", False):
    env.Append(LINKFLAGS=["-flto"], CCFLAGS=["-flto"])


env.Append(
    CPPPATH=[
        join(FRAMEWORK_DIR, "Core"),
        join(FRAMEWORK_DIR, "Peripheral", "inc"),
        join(FRAMEWORK_DIR, "Peripheral", "src")
        # Paths for startup and system are addeed later if wanted
    ],
    LIBS=env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkNoneOSVariant"),
        join(FRAMEWORK_DIR, "Peripheral", "src"),
    ),
)

env.BuildSources(
    join("$BUILD_DIR", "FrameworkNoneOSCore"),
    join(FRAMEWORK_DIR, "Core")
)

if not board.get("build.ldscript", ""):
    linker_script_path = render_linker_script(board.get("build.mcu"))
    env.Replace(LDSCRIPT_PATH=linker_script_path)


if get_flag_value("use_builtin_startup_file", True):
    env.Append(CPPPATH=[join(FRAMEWORK_DIR, "Startup")])
    startup_filename = "startup_ch32v00x.S"
    startup_file_filter = f"-<*> +<{startup_filename}>"
    env.BuildSources(
        join("$BUILD_DIR", "FrameworkNoneOSStartup"),
        join(FRAMEWORK_DIR, "Startup"),
        startup_file_filter
    )

# for clock init etc.
if get_flag_value("use_builtin_system_code", True):
    env.Append(CPPPATH=[join(FRAMEWORK_DIR, "System")])
    env.BuildSources(
        join("$BUILD_DIR", "FrameworkNoneOSSSystem"),
        join(FRAMEWORK_DIR, "System")
    )

# By default, include the Debug.h/.c code.
# practically every example needs it. Can be turned of in the platformio.ini.
if get_flag_value("use_builtin_debug_code", True):
    env.Append(CPPPATH=[join(FRAMEWORK_DIR, "Debug")])
    env.BuildSources(
        join("$BUILD_DIR", "FrameworkNoneOSDebug"),
        join(FRAMEWORK_DIR, "Debug")
    )
