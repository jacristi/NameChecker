# Name Evaluator


## Main Tab

### Screen Against checkboxes
* These checkboxes allow you to select what category of avoids you would like to check your names against.
	INN, Market Research, and Linguistics are all defined in a master avoids list
	Competitor and Project Avoids are defined within the application on the View/Add Avoids Tab

### Names

* This text area is where a list of names should be entered, each name should be on its own new line to be properly parsed and checked
* The "Check Names" button starts the name evaluation process, the application takes in the list of names entered compares those names against all previously defined avoids for each checked category.
	* Upon completion, the Conflicts area will be populated with a table detailing avoids found in each name broken out by category
* There are 3 tool buttons under the text area: ABC, Abc, abc
	* ABC: sets all names to UPPER CASE
	* Abc: sets all names to Title Case
	* abc: sets all names to lower case

### Confilcts

* Once the "Check Names" button has been clicked, the name evaulation process kicks off and the results will be output to this area.
* Results will be in a sortable table and broken out by avoids category for each name.
* If there are no conflicts, you will simple see "No Conflicts!" - nice job!

### INN Stem Filter
* If there are any specific INN Stems that shoudl be ignored in a search (i.e. the stem names are currently being developed for), they can be entered in this field to be ignored.
* Any letter string entered in here will not show up in the results view.
* You can enter more than 1 letter string, as long they are separated by a comma *e.g. vir,axo,imex)

### Exit
* The exit button closes the application, but not before asking if you really want to exit.

-----

## View/Add Avoids Tab

### Project Avoids to Add and Competitor to Add
* These text areas offers a space to define avoids per project/session. Anything entered in these spaces will be parsed out and added to a temporary master list of avoids which can be viewed in the All Avoids table to the right.
* There are several types of avoids that can be defined, so long as the correct syntax is used (note that some of the syntax is flexible and can be defined in the configuration file, more on this below)
	* prefix: define prefix avoids by appending a dash (-) to the end of a letter string
	* infix: define an infix avoid by wrapping a letter string in dash (-)
	* suffix: define a suffix avoid by starting a letter string with a dash (-)
	* anywhere: define an anywhere avoid by wrapping a letter string in quotes (") or asterisk (*)
	* string_compare: define a string compare avoid by not including any fix or anywhere signifieres as mentioned above (-, *, ")
* The "Save Avoids" button saves all avoids entered in the project/competitor text spaces to the temporary master list of avoids. These avoids can be found in the All Avoids table
	* Tip: type User in the filter avoids text line to see all of your project and competitor avoids, you can use this to check that they were added and assigned the correct type.
* The "Clear Avoids" button clears all avoids from the Project and Competitor text areas and reloads the avoids from the master avoids file.
	* Project and Competitor avoids will be saved across sessions, so long as they have not been cleared or manually removed from the configuration file.

### All Avoids
* The All Avoids table shows the complete list of all avoids that will be used by the application when evaluating names. This includes values from the master avoids file as well as any user entered-values
* This table can be filtered quickly by typing in the Filter avoids text line below the table. This filter looks at values in all fields but can be configured to only filter by the "value" field by setting the value "filter_avoids_on_value_only" in the configuration file to 1
* The "Reload Avoids" button will remove all avoids from the current total list of avoids and reload only the avoids from the master file.

-----

## Maintaining the Master Avoids File
* The master avoids file contains all avoids for categories "INN - USAN," 'Linguistic," and "Market Research" - each category has its own sheet in the file.
* The path to the master file can be configured in the NameEvaluator_Conf file with value: `path_to_avoids_file`
* Each sheet must have at least the fields `value`, `type`, and `description` - these are required for the application to read and parse the avoids.
    * value: this field is for the actual letter string of the avoid (e.g. vir, mab, or tox)
    * type: this field defines what type of avoid the value is and how it should be checked against, there are 5 avoid types that can be defined:
        * prefix: checks for the avoid letter string at the beginning of a name
        * infix: checks for the avoid letter string between the first and last letter (i.e. first and last letter are not included in the check)
        * suffix: checks for the avoid letter string at the end of a name
        * anywhere: checks for the avoid letter string anywhere in the name
        * string_compare: performs multiple checks on a name:
            * combo: this checks if the avoid string shares the name first letter and last 3 letters
            * compare n letters: this checks if the name and avoid letter string share a string of length n, n can be any number between the minimum defined in the config (string_compare_minimum) and the length of the name.
* Additional field can be added in the avoids master for any of the sheets as desired, and each can be different as long as the above 3 remain consistent across all.

-----

## Technical Notes

Package dependencies
-----
* see req.txt

Relevant commands
-----
Convert a UI file generated by QT Designer into a python file
* `pyuic5 -x ui_file_name.ui -o py_file_name.py`
* `pyuic5 -x .\src\UI\UILBBNameEvaluator.ui -o .\src\UI\ui_lbb_name_evaluator.py `

Simple pyinstaller command to package the code into an exe
* `pyinstaller run.py --onefile --noconsole -i "app.ico"`
* `pyinstaller run.spec` (if spec file is set up)
