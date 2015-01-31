import random
from bintrees import AVLTree


class BinTree:
	tree = None

	def __init__(self):

		self.tree = AVLTree()

	def insert(self, rating, username):
		if not rating in self.tree:
			self.tree[rating] = set()
		self.tree[rating].add(username)

	def remove(self, rating, username):
		if rating in self.tree:
			self.tree[rating].remove(username)
			if len(self.tree[rating]) == 0:
				self.tree.discard(rating)

	def all_pairs_inbetween(self, low, high):
		pairs = []
		for k, v in self.tree[low: high].items():
			for u in v:
				pairs.append((k, u))
		return pairs

if __name__ == "__main__":
	t = BinTree()
	for i in range(100):
		t.insert(i, str(i))
	print t.all_pairs_inbetween(10, 15)
	t.remove(11, "11")
	print t.all_pairs_inbetween(10, 15)