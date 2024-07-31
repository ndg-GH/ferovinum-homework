### Ferovinum - Homework - Financial Transaction Engine

To test the software, execute the following steps and commands:

1. **Create the local repository**:
  - git clone https://github.com/ndg-GH/ferovinum-homework.git
  - cd ferovinum-homework

2. **Run the application**:
  - ./exec.py all

3**Test the application**:
  - ./exec.py test


The code is structured in 3 directories :

  - build : docker and python requirement files
  - data : csv fles with product prices, client fees and orders
  - src : the application code (ferovinum python package), the database init script and the pytest script

The exec.py script in the root directory is used to execute the commands to manage the application (build / start / stop / test / all)

The test outputs are collected in the test_output folder


Limitations of the implementation:
  - there is an assumption that the clock is monotonic when storing orders

Notes :
  - there is a misspelling in page 5 ("romDate" instead of "toDate")
  - there is an error in the expected result of "GET /balance/product/P-1?date=2021-07-01" (quantity of 850 is expected for client C-1, not 950)
