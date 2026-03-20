# Cloud Workstations terminal basics you actually need (15 minutes)

## What the terminal is
In this hackathon, the terminal is the text-based shell inside **GCP Cloud Workstations**. You are not expected to use a local machine terminal as your main environment.

In the hackathon you may use it to:
- move into the project folder
- install dependencies
- run the app
- view errors
- confirm where you are inside the workstation

## The minimum commands to recognize
- `pwd` -> shows where you are
- `ls` -> lists files and folders
- `cd folder-name` -> moves into a folder
- `cd ..` -> moves up one folder

## Three truths beginners need
- The Cloud Workstations terminal cares about the current folder.
- The same command can work in one workstation folder and fail in another.
- Error text is often helpful, not hostile.

## Example
If the README says `npm install`, first check:
- are you in the repo folder?
- does `ls` show files like `package.json`?
- are you running the command inside the workstation terminal rather than somewhere else?

## Common messages and what they often mean
- `command not found` -> the tool is not installed or the command is misspelled
- `No such file or directory` -> the path or folder name is wrong
- `Permission denied` -> your account cannot do that action

## Optional videos
Watch: **What is Cloud Workstations?**
https://www.youtube.com/watch?v=E1cblFqb8nk

Watch: **How to use the Google Cloud Console**
https://www.youtube.com/watch?v=27Pb5g7bEAA
