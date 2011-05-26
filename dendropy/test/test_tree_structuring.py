#! /usr/bin/env python

##############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2010 Jeet Sukumaran and Mark T. Holder.
##  All rights reserved.
##
##  See "LICENSE.txt" for terms and conditions of usage.
##
##  If you use this work or any portion thereof in published work,
##  please cite it as:
##
##     Sukumaran, J. and M. T. Holder. 2010. DendroPy: a Python library
##     for phylogenetic computing. Bioinformatics 26: 1569-1571.
##
##############################################################################

"""
Tests native tree structuring routines.
"""

import unittest
from dendropy.test.support import pathmap
from dendropy.utility import messaging
from dendropy.test.support import extendedtest
import dendropy

_LOG = messaging.get_logger(__name__)

class TestTreeLadderization(unittest.TestCase):

    def testLadderizeLeft(self):
        """
        Dummy test!
        """
        tree = dendropy.Tree.get_from_path(pathmap.tree_source_path('pythonidae.mle.nex'), "nexus")
        tree.ladderize()

    def testLadderizeRight(self):
        """
        Dummy test!
        """
        tree = dendropy.Tree.get_from_path(pathmap.tree_source_path('pythonidae.mle.nex'), "nexus")
        tree.ladderize(right=True)

class TreeMidpointRootingTest(extendedtest.ExtendedTestCase):

    def testMidpointRooting(self):
        taxa = dendropy.TaxonSet()
        test_trees = dendropy.TreeList.get_from_path(pathmap.tree_source_path('pythonidae.random.bd0301.randomly-rooted.tre'),
                "nexus",
                taxon_set=taxa,
                as_rooted=True)
        expected_trees = dendropy.TreeList.get_from_path(pathmap.tree_source_path('pythonidae.random.bd0301.midpoint-rooted.tre'),
                "nexus",
                taxon_set=taxa,
                as_rooted=True)
        for idx, test_tree in enumerate(test_trees):
            expected_tree = expected_trees[idx]
            test_tree.reroot_at_midpoint(update_splits=True)
            self.assertEqual(test_tree.symmetric_difference(expected_tree), 0)
            for split in test_tree.split_edges:
                if test_tree.split_edges[split].head_node is test_tree.seed_node:
                    continue
                self.assertAlmostEqual(test_tree.split_edges[split].length, expected_tree.split_edges[split].length, 3)

if __name__ == "__main__":
    unittest.main()

