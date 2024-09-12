# Random Product Picker

## Setup

1. Download [Pycharm](https://www.jetbrains.com/pycharm/download/?section=mac) and [Python](https://www.python.org/downloads/?fbclid=IwAR35p70YwPCDXSMJ-ftJ_FcKX7-6HN_UKy5oTsjOlX2QvUX0LGtszD4_2RU)
2. Open Pycharm and click "**Get from VCS**" in the top right
3. **Directory:** Choose the place on your computer where you want the folder to be*
4. **URL:** https://github.com/jkreiss/RSA-Product-Picker
5. Click clone
6. Open *package_installer.py* and click the play button

*If you choose the directory before you paste the URL it will automatically pick a folder name for you. \
If you put the URL in before you pick the directory the path will be along the lines of */user/admin/Desktop* and it 
will fail to clone. To fix this just add the name you want the folder to be after the last place in the path i.e. 
*/user/admin/Desktop/Product-Picker* 

## Running the program
1. Put the Excel file in the same folder that was just cloned
2. Open *main.py* and navigate to line 55 
3. Type in the parameters based on the instructions
4. Click the play button

If you're having issues make sure its an excel file and you can see the file on the left hand side under project.
Also make sure it has *tags* and *type* somewhere in the headers 

## Pulling updates
1. Click *Git* on the toolbar at the top
2. Pull
3. Click the blue *Modify Options*
4. Click the one that says *rebase*
5. Then pull


This will update anywhere in the code where local changes have not been made.
If it's not working, in the bottom right of the pycharm window theres a box with >_ in it called terminal, run these 
commands in this order:

`git fetch origin` \
`git reset --hard origin/main` \
`git pull origin main` 

But it's probably easier to just delete the folder and reclone it



