Run setup instructions to install required packages.
Make sure to change the chmod of setup.sh to make it executable by running:
  chmod +x setup.sh
Then run the setup script:
  ./setup.sh
This will create a virtual environment and install the required packages listed in requirements.txt.

Activate the virtual environment:
  source venv/bin/activate

Do unzip the dataset if not already done.


Now run the main script to execute the PageRank algorithm:
  python3 graph.py
