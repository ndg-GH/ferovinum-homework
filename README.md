### Ferovinum - Homework - Financial Transaction Engine

To test the software, execute the following steps and commands:

1. **Create the local repository**:
  - git clone https://github.com/ndg-GH/ferovinum-homework.git
  - cd ferovinum-homework

2. **Run the application**:
  - ./exec.py all


The code is structured in 4 directories :

  - build : docker and python requirement files
  - data : csv fles with product prices, client fees and orders
  - src : the application code (ferovinum python package) and the database init script
  - test : the pytest files

and the exec.py script in the root directory is used to execute the commands to manage the application (build / start / stop / load / test / all)


Limitations of the implementation:


Trade-offs or design decisions:


Notes :
  - I have assumed that there is a misspelling in page 5 ("romDate" instead of "fromDate")

