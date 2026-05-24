"""
University: University of Isfahan
Faculty: Mathematics and Statistics
Branch: Computer Science
Course: Artificial Intelligence
Professor: Dr. Faria Nasiri Mofakham
TAs: MehrAzin Marzough, Mohammad Karimi, Anahita Honarmandian
Project: Implementing Informed and Uninformed Search Algorithms for a
Fully Observable, Deterministic, Sequential, Static, Discrete, Multi-Agent Environment
"""



from env import play
from search.a_star import a_star
from search.bfs import bfs
from search.dls import dls
from search.ucs import ucs


if __name__ == "__main__":
    play("easy-no-weapon", bfs, delay=200)
