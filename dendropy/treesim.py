#! /usr/bin/env python

###############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2009 Jeet Sukumaran and Mark T. Holder.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

"""
Tree simulation and generation.
"""

import sys
import copy
import math

from dendropy.utility import GLOBAL_RNG
from dendropy import coalescent
from dendropy import dataobject

def star_tree(taxon_set):
    "Builds and returns a star tree from the given taxa block."
    star_tree = dataobject.Tree(taxon_set)
    for taxon in taxon_set:
        star_tree.seed_node.new_child(node_taxon=taxon)
    return star_tree

def uniform_pure_birth(taxon_set,
                       birth_rate=1.0,
                       ultrametricize=True,
                       rng=None):
    "Generates a uniform-rate pure-birth process tree. "
    if rng is None:
        rng = GLOBAL_RNG # use the global rng by default
    tree = dataobject.Tree(taxon_set)

    leaf_nodes = tree.leaf_nodes()
    count = 0
    while len(leaf_nodes) < len(taxon_set):
        parent_node = rng.choice(leaf_nodes)
        edge_length = rng.expovariate(len(leaf_nodes)/birth_rate)
        child1 = dataobject.Node()
        child2 = dataobject.Node()
        child1.node_id = 'n' + str(count+1)
        child2.node_id = 'n' + str(count+2)
        child1.edge.length = edge_length
        child2.edge.length = edge_length
        parent_node.add_child(child1)
        parent_node.add_child(child2)
        count = count + 2
        leaf_nodes = tree.leaf_nodes()
    leaf_nodes = tree.leaf_nodes()
    for idx, leaf in enumerate(leaf_nodes):
        leaf.taxon = taxon_set[idx]
    if ultrametricize:
        max_distance_from_root = max([node.distance_from_root() for node in leaf_nodes])
        for node in leaf_nodes:
            node.edge.length = node.edge.length + (max_distance_from_root - node.distance_from_root())
    tree.is_rooted = True
    return tree

def pop_gen_tree(tree=None,
                 taxon_set=None,
                 ages=None,
                 num_genes=None,
                 pop_sizes=None,
                 num_genes_attr = 'num_genes',
                 pop_size_attr = 'pop_size',
                 rng=None):
    """
    This will simulate and return a tree with edges decorated with
    population sizes and leaf nodes decorated by the number of genes
    (samples or lineages) in each leaf.

    If `tree` is given, then this is used as the tree to be decorated.
    Otherwise, a Yule tree is generated based on the given taxon_set.
    Either `tree` or `taxon_set` must be given.

    The timing of the divergences can be
    controlled by specifying a vector of ages, `ages`. This should be
    sequences of values specifying the ages of the first, second,
    third etc. divergence events, in terms of time from the present,
    specified either in generations (if the pop_sizes vector is given)
    or population units (if the pop_size vector is not given). If an
    ages vector is given and there are less than num_pops-1 of these, then
    an exception is raised.

    The number of gene lineages per population can be specified through
    the 'num_genes', which can either be an scalar integer or a list.
    If it is an integer, all the population get the same number of
    genes. If it is a list, it must be at least as long as num_pops.

    The population sizes of each edge can be specified using the
    `pop_sizes` vector, which should be a sequence of values
    specifying the population sizes of the edges in postorder. If the
    pop_size vector is given, then it must be at least as long as
    there are branches on a tree (=2 * num_pops + 1), otherwise it is an
    error. If it is not given, then the branch lengths of the population
    trees will be in population units.

    This function first generates a tree using a pure-birth model with
    a uniform birth rate of 1.0. If an ages vector is given, it then
    sweeps through the internal nodes, assigning branch lengths such
    that the divergence events correspond to the ages in the
    vector. If a population sizes vector is given, it then visits all
    the edges in postorder, assigning population sizes to the
    attribute 'pop_size' (which is persisted as an annotation). During
    this, if an ages vector was *not* given, then the edge lengths are
    multiplied by the population size of the edge so the branch length
    units will be in generations. If an ages vector was given, then it
    is assumed that the ages are already in the proper scale/units.
    """

    # get our random number generator
    if rng is None:
        rng = GLOBAL_RNG # use the global rng by default

    # get a yule tree
    if not tree:
        if taxon_set:
            tree = uniform_pure_birth(taxon_set=taxon_set,
                                      rng=rng)
        else:
            raise Exception("Either tree or taxa block must be given")

    num_pops = len(tree.leaf_nodes())

    # basic idiot-checking
    if ages is not None and len(ages) < (num_pops - 1):
        msg = "Too few ages specified."
        raise Exception(msg)
    if num_genes is not None:
        if isinstance(num_genes, list):
            if len(num_genes) < num_pops:
                msg = "Too few number of gene samples specified"
                raise Exception(msg)
            else:
                samples = num_genes
        else:
            samples = [num_genes for tax in range(num_pops)]
    else:
        samples = None
    if pop_sizes is not None and len(pop_sizes) < (2 * num_pops + 1):
        msg = "Too few population sizes specified."
        raise Exception(msg)

    # set the ages
    if ages is not None:

        # get the internal nodes on the tree in reverse branching
        # order, so that newest nodes are returned first
        nodes = tree.nodes(cmp_fn = lambda x, y : \
                           int((y.distance_from_root()-x.distance_from_root())*10e+6),
                           filter_fn = lambda x : not x.is_leaf())
        # assign the ages
        for index, node in enumerate(nodes):
            for child in node.child_nodes():
                child.edge.length = ages[index] - child.distance_from_tip()

    # set the gene samples
    if samples is not None:
        for index, leaf in enumerate(tree.leaf_iter()):
            setattr(leaf, num_genes_attr, samples[index])
            leaf.annotate(num_genes_attr)

    # set the population sizes
    if pop_sizes is not None:
        index = 0
        for edge in tree.postorder_edge_iter():
            setattr(edge, pop_size_attr, pop_sizes[index])
            edge.annotate(pop_size_attr)
            if ages is None:
                edge.length = edge.length * getattr(edge, pop_size_attr)
            index = index + 1

    return tree

def pure_kingman(taxon_set, pop_size=1, rng=None):
    """
    Generates a tree under the unconstrained Kingman's coalescent process.
    """

    # get our random number generator
    if rng is None:
        rng = GLOBAL_RNG # use the global rng by default

    nodes = [dataobject.Node(taxon=t) for t in taxon_set]
    seed_node = coalescent.coalesce(nodes=nodes,
                                    pop_size=pop_size,
                                    period=None,
                                    rng=rng)[0]
    tree = dataobject.Tree(taxon_set, seed_node=seed_node)
    return tree

def constrained_kingman(pop_tree,
                        gene_tree_list=None,
                        rng=None,
                        gene_node_label_func=None,
                        num_genes_attr='num_genes',
                        pop_size_attr='pop_size',
                        decorate_original_tree=False):
    """
    Given a population tree, `pop_tree` this will return a *pair of
    trees*: a gene tree simulated on this population tree based on
    Kingman's n-coalescent, and population tree with the additional
    attribute 'gene_nodes' on each node, which is a list of
    uncoalesced nodes from the gene tree associated with the given
    node from the population tree.

    `pop_tree` should be a DendroPy Tree object or an object
    of a class derived from this with the following attribute
    `num_genes` -- the number of gene samples from each population in the
    present.  Each edge on the tree should also have the attribute
    `pop_size` -- the effective size of the population at this time.

    If `gene_tree_list` is given, then the gene tree is added to the
    tree block, and the tree block's taxa block will be used to manage
    the gene tree's `taxa`.

    `gene_node_label_func` is a function that takes two arguments (a string
    and an integer, respectively, where the string is the containing species
    taxon label and the integer is the gene index) and returns a label for
    the corresponding the gene node.

    if `decorate_original_tree` is True, then the list of uncoalesced nodes at
    each node of the population tree is added to the original (input) population
    tree instead of a copy.
    """

    # get our random number generator
    if rng is None:
        rng = GLOBAL_RNG # use the global rng by default

    if gene_tree_list is not None:
        gtaxa = gene_tree_list.taxon_set
    else:
        gtaxa = dataobject.TaxonSet()

    if gene_node_label_func is None:
        gene_node_label_func = lambda x, y: "%s_%02d" % (x, y)

    # we create a set of gene nodes for each leaf node on the population
    # tree, and associate those gene nodes to the leaf by assignment
    # of 'taxon'.
    for leaf_count, leaf in enumerate(pop_tree.leaf_iter()):
        gene_nodes = []
        for gene_count in range(getattr(leaf, num_genes_attr)):
            gene_node = dataobject.Node()
            gene_node.taxon = gtaxa.require_taxon(label=gene_node_label_func(leaf.taxon.label, gene_count+1))
            gene_nodes.append(gene_node)
        leaf.gene_nodes = gene_nodes

    # We iterate through the edges of the population tree in post-order,
    # i.e., visiting child edges before we visit parent edges. For
    # each edge visited, we take the genes found in the child nodes,
    # and run the coalescent simulation on them bounded by the length
    # of the edge. Any genes that have not yet coalesced at the end of
    # this period are added to the genes of the tail (parent) node of
    # the edge.

    if decorate_original_tree:
        working_poptree = pop_tree
    else:
        # start with a new (deep) copy of the population tree so as to not
        # to change the original tree
        working_poptree = copy.deepcopy(pop_tree)

    # start with a new tree
    gene_tree = dataobject.Tree()
    gene_tree.taxon_set = gtaxa
    for edge in working_poptree.postorder_edge_iter():
        edge.head_node.gene_nodes = edge.head_node.gene_nodes

        # if mrca root, run unconstrained coalescent
        if edge.head_node.parent_node is None:
            if len(edge.head_node.gene_nodes) > 1:
                final = coalescent.coalesce(nodes=edge.head_node.gene_nodes,
                                            pop_size=pop_size,
                                            period=None,
                                            rng=rng)
            else:
                final = edge.head_node.gene_nodes
            gene_tree.seed_node = final[0]
        else:

            if hasattr(edge, pop_size_attr):
                pop_size = getattr(edge, pop_size_attr)
            else:
                # this means all our time will be in population units
                pop_size = 1

            uncoal = coalescent.coalesce(nodes=edge.head_node.gene_nodes,
                                         pop_size=pop_size,
                                         period=edge.length,
                                         rng=rng)
            if not hasattr(edge.tail_node, 'gene_nodes'):
                edge.tail_node.gene_nodes = []
            edge.tail_node.gene_nodes.extend(uncoal)

    gene_tree.is_rooted = True
    if gene_tree_list is not None:
        gene_tree_list.append(gene_tree)
        return gene_tree, working_poptree
    else:
        return gene_tree, working_poptree
