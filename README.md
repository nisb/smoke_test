## Introduction
The smoke_test.py script is a [Sikuli-based](http://www.sikuli.org/) test for the OS X platform. It is designed to test software by taking screenshots of a new version of a program and comparing them with the correct ones (standard). So, this is a regression test.

Originally, the script was intended to check if a document containing text and graphics (like MS Word or Apple Pages) was rendered on the canvas correctly. Thanks to Sikuli, which provides access to program's GUI, one can verify not only the content of the canvas but other windows and panels as well.

In the same way, one can verify the program interface itself (e.g. detect missing or incorrectly initialized controls).

Screenshots are taken by the means of OS X (macOS).

Dependencies: [Sikuli](http://www.sikuli.org/).

## How to Create a Sikuli Project?
1. Create a new folder.
2. Place the script inside the folder.
3. Rename the folder to a name you prefer and add `.sikuli` to the end.

OS X will recognize '.sikuli' as a file name extension associated with Sikuli, and turn the folder into a bundle (with the script inside).

## How to Run the Script?
These two command lines are used to run the script in one of two modes correspondingly.

Test mode:  
`/Applications/SikuliX/runsikulix -r '/../smoke_test.sikuli' --args -p '/../smoke_test_folder'`

Here:  
/Applications/SikuliX/runsikulix - path inside the Sikuli.app bundle. If this software is installed on your computer not in the Applications folder, just put the correct path instead of 'Applications'.

-r '/../smoke_test.sikuli' - this parameter defines the path to the Sikuli project we created earlier.

-p '/../smoke_test_folder' - this parameter defines the path to a folder containing the script settings and test documents. What's inside the test folder will be explained later.

In the test mode, the script takes screenshots of a program version which is under test, and compares each screenshot with a standard one taken from a stable version of the program.

Standard screenshot updating mode:  
`/Applications/SikuliX/runsikulix -r '/../smoke_test.sikuli' --args -p '/../smoke_test_folder' -u`

Here is the same command line as in the test mode plus the -u key. Once it is present, the script creates new standard screenshots. Old standard screenshots will be overwritten.

Obviously, you run the script with the -u key first in order to create standard screenshots. Then you can run it in the test mode as many times as you need.

## What Actually the Script Does?
The script picks a test document from the test folder, opens it in the program you test, takes a screenshot, and compares the latter with the standard screenshot related to the same document. If the screenshots are exactly the same, a test passes. Otherwise, the test fails. The output in the Terminal will tell you which tests passed and which didn't. Then the script closes the document and opens the next one until all of them are checked.

Screenshots of failed tests will be saved in the 'Failed' folder for further examination. Passed ones will be removed.

## The Test Folder
The test folder contains all the data linked to one test session (a series of test documents).

The test folder can have any name since you indicate the path to it as a command line argument.

The structure of the test folder (after a few failed tests):  

    smoke_test  
        documents  
            document1.doc  
            document1.png  
            document2.doc  
            document2.png  
            document3.doc  
            document3.png  
        Failed_Tests_2016_5_22_17_40  
            document1.png  
        Failed_Tests_2016_5_22_17_43  
            document3.png  
        run_script.command  
        setup.txt

The 'documents' folder stores test documents and standard screenshots. It's name is constant.

The standard and failed screenshots have the same name as the respective document.

'Failed\_Tests_' folders are created automatically. They contain screenshots of failed tests.

'run_script.command' just contains a command line to run the script. This file is arbitrary, you can keep it anywhere.

'setup.txt' is used for script settings.

Once the script is launched, it uses the path given in the command line to find 'setup.txt' and 'documents'.

## Setup.txt
This file contains these details:
- Path to a stable version of the program.
- Path to a program you are going to test.
- Document file name extension.
- Screenshot file name extension.
- Delay parameter which lets you adjust timeouts in the script.
