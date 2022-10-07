# BearWise
This is a simple sync between ReadWise and Bear Notes so I am able to use Bear as my second brain.
It must run on a mac, but should be able to with all the default python installs.

I used a library x-call from https://github.com/robwalton/python-xcall
there is just a copy of that in this repository.

## Build your own executable
```
pyinstaller --clean bearwise.spec
```
Shoudl be enough to get you a dist folder with an executable. 


## Templates
There are two template files that you can change to a degree,
```
Book.MD //but do not change the title
Highlight.md // but it must contain the {{ID}} somewhere or you will get duplicates.
```