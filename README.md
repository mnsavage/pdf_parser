# pdf-parser
This repository includes our code and logic dedicated to parsing and validating PDFs. Additionally, we utilize Docker to containerize this program, enabling it to run as a batch job on AWS.

## github actions:
- In this repository, a GitHub Action is triggered whenever a pull request (PR) is made. This Action performs checks for linting and ensures that all unit tests pass.

## install requirements:
- run the make command `make install`

## install test requirements:
- run the make command `make install_test`

## run unit tests:
- run the make command `make test`(Note: you must have test requirements install)

## run linter:
- run the make command `make lint`(Note: you will need to install tools can run make command `make install_tools`)

# Notes to next group working on this project:
- The current code for parsing PDFs lacks efficiency and accuracy in validation. It is advisable to consider a different library, language, or tool for more effective PDF validation. Additionally, if you choose to proceed with executing the code as AWS batch jobs, it will be necessary to containerize the code using a tool like Docker.
