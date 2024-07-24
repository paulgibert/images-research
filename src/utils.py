from typing import List
import subprocess
import os


def bash(cmd: str) -> str:
    """
    Run a bash command.

    @param cmd: command
    @returns stdout
    """
    try:
        b = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running `{cmd}`: {str(e)}")
        exit(1)
    return b.decode("utf-8")[:-1]


def mkdir(dir_name: str):
    """
    Make a directory, removing the directory first if it
    already exists.
    
    @param dir_name: The directory to create
    """
    os.system(f"rm -rf {dir_name}")
    os.mkdir(dir_name)


def check_equal_size(objs: List[any]):
    """
    Raises an exception if all provided objects
    are not of equal length.

    @param objs: List of objects to compare
    @raises ValueError if there is a size mismatch
    """
    if len(objs) <= 1:
        return
    sz = len(objs[0])
    for o in objs[2:]:
        if len(o) != sz:
            raise ValueError(f"Objects were not of the same size. {len(o)} != {sz}")


def check_equal_contents(its: List[any]):
    """
    Raises an exception if all provided iterables
    are not of equal content.

    @param objs: List of iterables to compare
    @raises ValueError if there is an element mismatch
    """
    if len(its) <= 1:
        return
    for it in its[2:]:
        for elem, ref in zip(it, its[0]):
            if elem != ref:
                raise ValueError(f"Objects differed in content. {elem} != {ref}")


def check_docker_image_exists(image_fullname) -> bool:
    """
    Checks if a docker image exists locally.

    @param image_fullname: The name of the image including registry and tag
    """
    try:
        # Run the docker images command and capture the output
        result = subprocess.run(['docker', 'inspect', image_fullname],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # If the image exists, docker inspect will return exit code 0
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        # Handle errors if the docker command fails
        print(f"Error checking docker image: {e}")
        exit(1)
