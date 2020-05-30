from setuptools import setup, find_packages

setup(
    name="nice_translator_tui",
    version="0.2.0",
    
    # a list of strings specifying the packages that setuptools will manipulate
    packages=find_packages(),

    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "nice_translator_tui": ["*.json"]
    },
    
    # project dependences
    install_requires=[
        'prompt-toolkit',
        'requests'
    ],

    entry_points={
        'console_scripts':[
            'tran=nice_translator_tui.main:run',
            'tranconfigpath=nice_translator_tui.main:get_config_file_path'
        ]
    },

    # PyPI    
    author="youyinnn",
    author_email="youyinnn@gmail.com",
    url="https://github.com/youyinnn/nice_translator_tui"

)