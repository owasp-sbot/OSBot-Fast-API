from setuptools import setup, find_packages

with open("README.md", "r") as file_readme:
    long_description = file_readme.read().strip()

with open("osbot_fast_api/version", "r") as file_version:
    version = file_version.read().strip()

setup(
    version                       = version                                         ,
    name                          = "osbot_fast_api"                                ,
    author                        = "Dinis Cruz"                                    ,
    author_email                  = "dinis.cruz@owasp.org"                          ,
    description                   = "OWASP Security Bot - Fast API"                 ,
    long_description              = long_description                                ,
    long_description_content_type = " text/markdown"                                ,
    url                           = "https://github.com/owasp-sbot/OSBot-Fast-API"  ,
    packages                      = find_packages()                                 ,
    classifiers                   = [ "Programming Language :: Python :: 3"         ,
                                      "License :: OSI Approved :: MIT License"      ,
                                      "Operating System :: OS Independent"          ])
