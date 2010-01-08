***********************************************
Creating, Reading and Writing Phylogenetic Data
***********************************************

Introduction
============

Phylogenetic data in DendroPy is represented by one or more objects of the following classes:

    |Taxon|
        A representation of an operational taxonomic unit, with an attribute, :attr:`~dendropy.dataobject.taxon.Taxon.label`, corresponding to the taxon label.

    |TaxonSet|
        A collection of |Taxon| objects representing a distinct definition of taxa (for example, as specified explicitly in a NEXUS "TAXA" block, or implicitly in the set of all taxon labels used across a NEWICK tree file).

    |Tree|
        A collection of |Node| and |Edge| objects representing a phylogenetic tree.
        Each |Tree| object maintains a reference to a |TaxonSet| object in its attribute, :attr:`~dendropy.dataobject.tree.Tree.taxon_set`, which specifies the set of taxa that are referenced by the tree and its nodes. Each |Node| object has a :attr:`~dendropy.dataobject.tree.Node.taxon` attribute (which points to a particular |Taxon| object if there is an operational taxonomic unit associated with this node, or is :keyword:`None` if not), a :attr:`~dendropy.dataobject.tree.Node.parent_node` attribute (which will be :keyword:`None` if the |Node| has no parent, e.g., a root node), a |Edge| attribute, as well as a list of references to child nodes, a copy of which can be obtained by calling :meth:`~dendropy.dataobject.tree.Node.child_nodes()`.

    |TreeList|
        A :class:`list` of |Tree| objects. A |TreeList| object has an attribute, :attr:`~dendropy.dataobject.tree.TreeList.taxon_set`, which specifies the set of taxa that are referenced by all member |Tree| elements. This is enforced when a |Tree| object is added to a |TreeList|, with the |TaxonSet| of the |Tree| object and all |Taxon| references of the |Node| objects in the |Tree| mapped to the |TaxonSet| of the |TreeList|.

    |CharacterMatrix|
        Representation of character data, with specializations for different data types: |DnaCharacterMatrix|, |RnaCharacterMatrix|, |ProteinCharacterMatrix|, |StandardCharacterMatrix|, |ContinuousCharacterMatrix|, etc. A |CharacterMatrix| can treated very much like a :class:`dict` object, with
        |Taxon| objects as keys and character data as values associated with those keys.

    |DataSet|
        A meta-collection of phylogenetic data, consisting of lists of multiple |TaxonSet| objects (:attr:`~dendropy.dataobject.DataSet.taxon_sets`), |TreeList| objects (:attr:`~dendropy.dataobject.DataSet.tree_lists`), and |CharacterMatrix| objects (:attr:`~dendropy.dataobject.DataSet.char_matrices`).

Creating New (Empty) Objects
============================

All of the above names are imported into the the the :mod:`dendropy` namespace, and so to instantiate new, empty objects of these classes, you would need to import :mod:`dendropy`::

    >>> import dendropy
    >>> tree1 = dendropy.Tree()
    >>> tree_list11 = dendropy.TreeList()
    >>> dna1 = dendropy.DnaCharacterMatrix()
    >>> dataset1 = dendropy.DataSet()

Or import the names directly::

    >>> from dendropy import Tree, TreeList, DnaCharacterMatrix, DataSet
    >>> tree1 = Tree()
    >>> tree_list1 = TreeList()
    >>> dna1 = DnaCharacterMatrix()
    >>> dataset1 = DataSet()

Creating and Populating New Objects
===================================

The |Tree|, |TreeList|, |CharacterMatrix|-derived, and |DataSet| classes all support ":meth:`get_from_*()`" factory methods that allow for the simultaneous instantiation and population of the objects from a data source:

    - :meth:`get_from_stream(src, schema, **kwargs)`
        Takes a file or file-like object opened for reading the data source as the first argument, and a string specifying the schema as the second.

    - :meth:`get_from_path(src, schema, **kwargs)`
        Takes a string specifying the path to the the data source file as the first argument, and a string specifying the schema as the second.

    - :meth:`get_from_string(src, schema, **kwargs)`
        Takes a string containing the source data as the first argument, and a string specifying the schema as the second.

All these methods minimally take a source and schema reference as arguments and return a new object of the given type populated from the given source::

    >>> import dendropy
    >>> tree1 = dendropy.Tree.get_from_string("((A,B),(C,D))", schema="newick")
    >>> tree_list1 = dendropy.TreeList.get_from_path("pythonidae.mcmc.nex", schema="nexus")
    >>> dna1 = dendropy.DnaCharacterMatrix.get_from_stream(open("pythonidae.fasta"), "dnafasta")
    >>> std1 = dendropy.StandardCharacterMatrix.get_from_path("python_morph.nex", "nexus")
    >>> dataset1 = dendropy.DataSet.get_from_path("pythonidae.nex", "nexus")

The schema specification can be one of: "nexus", "newick", "nexml", "dnafasta", "rnafasta", "proteinfasta" etc. Not all formats are supported for reading, and not all formats make sense for particular objects (for example, it would not make sense to try and instantiate a |Tree| or |TreeList| object from a FASTA-formatted data source).

Alternatively, you can also pass a file-like object and schema specification to the constructor of these classes using the keyword arguments ``stream`` and ``schema`` respectively::

    >>> import dendropy
    >>> tree1 = dendropy.Tree(stream=open("mle.tre"), schema="newick")
    >>> tree_list1 = dendropy.TreeList(stream=open("pythonidae.mcmc.nex"), schema="nexus")
    >>> dna1 = dendropy.DnaCharacterMatrix(stream=open("pythonidae.fasta"), schema="dnafasta")
    >>> std1 = dendropy.StandardCharacterMatrix(stream=open("python_morph.nex"), schema="nexus")
    >>> dataset1 = dendropy.DataSet(stream=open("pythonidae.nex"), schema="nexus")

Various keyword arguments can also be passed to these methods which customize or control how the data is parsed and mapped into DendroPy object space.
These are discussed below.

Reading and Populating (or Repopulating) Existing Objects
=========================================================

The |Tree|, |TreeList|, |CharacterMatrix|-derived, and |DataSet| classes all support a suite of ":meth:`read_from_*()`" instance methods that parallels the ":meth:`get_from_*()`" factory methods described above:

    - :meth:`read_from_stream(src, schema, **kwargs)`
        Takes a file or file-like object opened for reading the data source as the first argument, and a string specifying the schema as the second.

    - :meth:`read_from_path(src, schema, **kwargs)`
        Takes a string specifying the path to the the data source file as the first argument, and a string specifying the schema as the second.

    - :meth:`read_from_string(src, schema, **kwargs)`
        Takes a string specifying containing the source data as the first argument, and a string specifying the schema as the second.

When called on an existing |TreeList| or |DataSet| object, these methods *add* the data from the data source to the object, whereas when called on an existing |Tree| or |CharacterMatrix| object,  they *replace* the object's data with data from the data source.
As with the ":meth:`get_from_*()`" methods, the schema specification can be any supported and type-apppropriate schema, such as "nexus", "newick", "nexml", "dnafasta", "rnafasta", "proteinfasta" etc.

For example, the following accumulates post-burn-in trees from several different files into a single |TreeList| object (the ``tree_offset`` keyword is discussed `here <Customizing_Tree_Creation_and_Reading>`_)::

    >>> import dendropy
    >>> post_trees = dendropy.TreeList()
    >>> post_trees.read_from_path("pythonidae.nex.run1.t", "nexus", tree_offset=200)
    >>> print(post_trees.description())
    TreeList object at 0x550990 (TreeList5573008): 801 Trees
    >>> post_trees.read_from_path("pythonidae.nex.run2.t", "nexus", tree_offset=200)
    >>> print(post_trees.description())
    TreeList object at 0x550990 (TreeList5573008): 1602 Trees
    >>> post_trees.read_from_path("pythonidae.nex.run3.t", "nexus", tree_offset=200)
    >>> print(post_trees.description())
    TreeList object at 0x550990 (TreeList5573008): 2403 Trees
    >>> post_trees.read_from_path("pythonidae.nex.run4.t", "nexus", tree_offset=200)
    >>> print(post_trees.description())
    TreeList object at 0x5508a0 (TreeList5572768): 3204 Trees

The |TreeList| object automatically handles taxon management, and ensures that all appended |Tree| objects share the same |TaxonSet| reference. Thus all the |Tree| objects created and aggregated from the data sources in the example will all share the same |TaxonSet| and |Taxon| objects, which is important if you are going to be carrying comparisons or operations between multiple |Tree| objects.

In contrast to the aggregating behavior of :meth:`read_from_*()` of |TreeList| and |DataSet| objects, the :meth:`read_from_*()` methods of |Tree|- and |CharacterMatrix|-derived objects show replacement behavior. For example, the following changes the contents of a |Tree| by re-reading it::

    >>> import dendropy
    >>> t = dendropy.Tree()
    >>> t.read_from_path('pythonidae.mle.nex', 'nexus')
    >>> print(t.description())
    Tree object at 0x79c70 (Tree37413776: '0'): ('Python molurus':0.0779719244,(('Python sebae':0.1414715009,((((('Morelia tracyae':0.0435011998,('Morelia amethistina':0.0305993564,(('Morelia nauta':0.0092774432,'Morelia kinghorni':0.0093145395):0.005595,'Morelia clastolepis':0.005204698):0.023435):0.012223):0.025359,'Morelia boeleni':0.0863199106):0.019894,(('Python reticulatus':0.0828549023,'Python timoriensis':0.0963051344):0.072003,'Morelia oenpelliensis':0.0820543043):0.002785):0.00274,(((('Morelia viridis':0.0925974416,('Morelia carinata':0.0943697342,('Morelia spilota':0.0237557178,'Morelia bredli':0.0357358071):0.041377):0.005225):0.004424,('Antaresia maculosa':0.1141193265,(('Antaresia childreni':0.0363195704,'Antaresia stimsoni':0.0188535952):0.043287,'Antaresia perthensis':0.0947695442):0.019148):0.007921):0.022413,('Leiopython albertisii':0.0698883547,'Bothrochilus boa':0.0811607602):0.020941):0.007439,(('Liasis olivaceus':0.0449896545,('Liasis mackloti':0.0331564496,'Liasis fuscus':0.0230286886):0.058253):0.016766,'Apodora papuana':0.0847328612):0.008417):0.006539):0.011557,('Aspidites ramsayi':0.0349772256,'Aspidites melanocephalus':0.0577536309):0.042499):0.036177):0.016859,'Python brongersmai':0.1147218285):0.001271,'Python regius':0.1800489093):0.0
    >>> t.read_from_path('pythonidae.mcmc-con.nex', 'nexus')
    >>> print(t.description())
    Tree object at 0x79c70 (Tree37414064: 'con 50 majrule'): ('Python regius':0.212275,('Python sebae':0.176816,(((((('Antaresia maculosa':0.127351,('Antaresia perthensis':0.108378,('Antaresia stimsoni':0.021372,'Antaresia childreni':0.038155):0.046446):0.025262):0.012957,('Morelia carinata':0.101145,('Morelia bredli':0.038563,'Morelia spilota':0.025643):0.050967):0.010472,'Morelia viridis':0.098541):0.023291,('Bothrochilus boa':0.091928,'Leiopython albertisii':0.080986):0.031583):0.008347,((('Liasis fuscus':0.026601,'Liasis mackloti':0.034524):0.069881,'Liasis olivaceus':0.047727):0.023758,'Apodora papuana':0.096097):0.01474):0.010084,(('Python timoriensis':0.101865,'Python reticulatus':0.095018):0.0922,('Morelia boeleni':0.093309,('Morelia tracyae':0.04727,('Morelia amethistina':0.034936,(('Morelia nauta':0.011,'Morelia kinghorni':0.011198):0.006932,'Morelia clastolepis':0.008103):0.025987):0.017415):0.033886):0.027519,'Morelia oenpelliensis':0.092143):0.006779):0.018238,('Aspidites ramsayi':0.030898,'Aspidites melanocephalus':0.068553):0.049525):0.050607):0.023304,('Python brongersmai':0.132193,'Python molurus':0.08872):0.011466)

As with the :meth:`get_from_*()` methods, keyword arguments can be used to provide control on the data source parsing.

Customizing Data Creation and Reading
=====================================
When specifying a data source from which to create or populate data objects using the :meth:`get_from_*()`, :meth:`read_from_*()`, or passing a data source stream to a constructor, you can also specify keyword arguments that provide fine-grained control over how the data source is parsed.
Some of these keyword arguments apply generally, regardless of the schema of the data source or the data object being created, while others are specific to the data object type or the data source schema.

Probably the most import general keyword is the ``taxon_set`` keyword, which passes a |TaxonSet| object to the parser to use to manage all taxon definitions and reference in the data source.
If not specified, every time a data source is parsed, at least one new |TaxonSet| object will be created for each definition of taxa (e.g., a NEXUS "TAXA" block), and all taxon definitions or references in the data source will be mapped to |Taxon| objects within that |TaxonSet| object.
If the taxa in the data source correspond to taxa already defined in an existing |TaxonSet| object, you would use the ``taxon_set`` keyword to ensure that this correspondence is maintained within DendroPy.

With NEXUS and NEWICK data sources, you can also specify ``preserve_underscores=True``.
The NEXUS standard dictates that underscores are equivalent to spaces, and thus any underscore found in any unquoted label in a NEXUS/NEWICK data source will be substituted for spaces.
Specifying ``preserve_underscores=True`` will force DendroPy to keep the underscores.

Other keyword arguments to customize data creation and reading, such as ``tree_offset``, ``collection_offset``, ``as_rooted``/``as_unrooted``, ``exclude_trees``, ``exclude_chars``, etc., are discussed in detail in specific sections: :ref:`Customizing_Tree_Creation_and_Reading`, :ref:`Customizing_Character_Creation_and_Reading`,  :ref:`Customizing_Data_Set_Creation_and_Reading`.

Writing or Saving Data
======================

The |Tree|, |TreeList|, |CharacterMatrix|-derived, and |DataSet| classes all support the following instance methods for writing data:

    - :meth:`write_to_stream(dest, schema, **kwargs)`
        Takes a file or file-like object opened for writing the data as the first argument, and a string specifying the schema as the second.

    - :meth:`write_to_path(dest, schema, **kwargs)`
        Takes a string specifying the path to the file as the first argument, and a string specifying the schema as the second.

    - :meth:`as_string(schema, **kwargs)`
        Takes a string specifying the schema as the first argument, and returns a string containing the formatted-representation of the data.

As above, the schema specification can be any supported and type-apppropriate schema, such as "nexus", "newick", "nexml", "dnafasta", "rnafasta", "proteinfasta" etc.

Converting Between Data Formats
===============================

Any data in a schema that can be read by DendroPy, can be saved to files in any schema that can be written by DendroPy.
Converting data between formats is simply a matter of calling readers and writers of the appropriate type.

Converting from FASTA schema to NEXUS::

    >>> import dendropy
    >>> cytb = dendropy.DnaCharacterMatrix.get_from_path("pythonidae_cytb.fasta", "dnafasta")
    >>> cytb.write_to_path("pythonidae_cytb.nexus", "nexus")

Converting a collection of trees from NEXUS schema to NEWICK::

    >>> import dendropy
    >>> mcmc = dendropy.TreeList.get_from_path("pythonidae.mcmc.nex", "nexus")
    >>> mcmc.write_to_path("pythonidae.mcmc.newick", "newick")

Converting a single tree from NEWICK schema to NEXUS::

    >>> import dendropy
    >>> mle = dendropy.Tree.get_from_path("pythonidae.mle.newick", "newick")
    >>> mle.write_to_path("pythonidae.mle.nex", "nexus")

Collecting data from multiple sources and writing to a NEXUS-formatted file::

    >>> import dendropy
    >>> ds = dendropy.DataSet()
    >>> ds.read_from_path("pythonidae_cytb.fasta", "dnafasta")
    >>> ds.read_from_path("pythonidae_aa.nex", "nexus", taxon_set=ds.taxon_sets[0])
    >>> ds.read_from_path("pythonidae_morphological.nex", "nexus", taxon_set=ds.taxon_sets[0])
    >>> ds.read_from_path("pythonidae.mle.tre", "nexus", taxon_set=ds.taxon_sets[0])
    >>> ds.write_to_path("pythonidae_combined.nex", "nexus")

Note how, after the first data source has been loaded, the resulting |TaxonSet| (i.e., the first one) is passed to the subsequent :meth:`read_from_path()` statements, to ensure that the same taxa are referenced as objects corresponding to the additional data sources are created. Otherwise, as each data source is read, a new |TaxonSet| will be created, and this will result in multiple |TaxonSet| objects in the |DataSet|, with the data from each data source associated with their own, distinct |TaxonSet|.

A better way to do this is to use the "attached taxon set" mode |DataSet| object::

    >>> import dendropy
    >>> ds = dendropy.DataSet(attached_taxon_set=True)
    >>> ds.read_from_path("pythonidae_cytb.fasta", "dnafasta")
    >>> ds.read_from_path("pythonidae_aa.nex", "nexus")
    >>> ds.read_from_path("pythonidae_morphological.nex", "nexus")
    >>> ds.read_from_path("pythonidae.mle.tre", "nexus")
    >>> ds.write_to_path("pythonidae_combined.nex", "nexus")

Examining Data Objects
======================

High-level summaries of the contents of DendroPy phylogenetic data objects are given by the :meth:`description()` instance method of the |Tree|, |TreeList|, |CharacterMatrix|-derived, and |DataSet| classes.
This method optionally takes a numeric value as its first argument that determines the level of detail (or depth) of the summary::

    >>> import dendropy
    >>> d = dendropy.DataSet.get_from_path('pythonidae.nex', 'nexus')
    >>> print(d.description())
    DataSet object at 0x79dd0: 1 Taxon Sets, 0 Tree Lists, 1 Character Matrices
    >>> print(d.description(3))
    DataSet object at 0x79dd0: 1 Taxon Sets, 0 Tree Lists, 1 Character Matrices
        [Taxon Sets]
            [0] TaxonSet object at 0x5a4a20 (TaxonSet5917216): 29 Taxa
                [0] Taxon object at 0x22c0fd0 (Taxon36442064): 'Python regius'
                [1] Taxon object at 0x22c0f10 (Taxon36441872): 'Python sebae'
                [2] Taxon object at 0x22c0ed0 (Taxon36441808): 'Python brongersmai'
                [3] Taxon object at 0x22c0f70 (Taxon36441968): 'Antaresia maculosa'
                [4] Taxon object at 0x22c0f30 (Taxon36441904): 'Python timoriensis'
                [5] Taxon object at 0x22c0f50 (Taxon36441936): 'Python molurus'
                [6] Taxon object at 0x22c0ff0 (Taxon36442096): 'Morelia carinata'
                [7] Taxon object at 0x23ae050 (Taxon37412944): 'Morelia boeleni'
                [8] Taxon object at 0x23ae030 (Taxon37412912): 'Antaresia perthensis'
                [9] Taxon object at 0x23ae070 (Taxon37412976): 'Morelia viridis'
                [10] Taxon object at 0x23ae090 (Taxon37413008): 'Aspidites ramsayi'
                [11] Taxon object at 0x23ae0b0 (Taxon37413040): 'Aspidites melanocephalus'
                [12] Taxon object at 0x22c0fb0 (Taxon36442032): 'Morelia oenpelliensis'
                [13] Taxon object at 0x23ae0d0 (Taxon37413072): 'Bothrochilus boa'
                [14] Taxon object at 0x23ae130 (Taxon37413168): 'Morelia bredli'
                [15] Taxon object at 0x23ae110 (Taxon37413136): 'Morelia spilota'
                [16] Taxon object at 0x23ae150 (Taxon37413200): 'Antaresia stimsoni'
                [17] Taxon object at 0x23ae0f0 (Taxon37413104): 'Antaresia childreni'
                [18] Taxon object at 0x23ae1b0 (Taxon37413296): 'Leiopython albertisii'
                [19] Taxon object at 0x23ae170 (Taxon37413232): 'Python reticulatus'
                [20] Taxon object at 0x23ae190 (Taxon37413264): 'Morelia tracyae'
                [21] Taxon object at 0x23ae1d0 (Taxon37413328): 'Morelia amethistina'
                [22] Taxon object at 0x23ae230 (Taxon37413424): 'Morelia nauta'
                [23] Taxon object at 0x23ae250 (Taxon37413456): 'Morelia kinghorni'
                [24] Taxon object at 0x23ae210 (Taxon37413392): 'Morelia clastolepis'
                [25] Taxon object at 0x23ae290 (Taxon37413520): 'Liasis fuscus'
                [26] Taxon object at 0x23ae2b0 (Taxon37413552): 'Liasis mackloti'
                [27] Taxon object at 0x23ae270 (Taxon37413488): 'Liasis olivaceus'
                [28] Taxon object at 0x23ae2f0 (Taxon37413616): 'Apodora papuana'
        [Character Matrices]
            [0] DnaCharacterMatrix object at 0x22c0f90 (DnaCharacterMatrix36442000):  29 Sequences
                [Taxon Set]
                    TaxonSet object at 0x5a4a20 (TaxonSet5917216): 29 Taxa
                [Characters]
                    [0] Python regius : 1114 characters
                    [1] Python sebae : 1114 characters
                    [2] Python brongersmai : 1114 characters
                    [3] Antaresia maculosa : 1114 characters
                    [4] Python timoriensis : 1114 characters
                    [5] Python molurus : 1114 characters
                    [6] Morelia carinata : 1114 characters
                    [7] Morelia boeleni : 1114 characters
                    [8] Antaresia perthensis : 1114 characters
                    [9] Morelia viridis : 1114 characters
                    [10] Aspidites ramsayi : 1114 characters
                    [11] Aspidites melanocephalus : 1114 characters
                    [12] Morelia oenpelliensis : 1114 characters
                    [13] Bothrochilus boa : 1114 characters
                    [14] Morelia bredli : 1114 characters
                    [15] Morelia spilota : 1114 characters
                    [16] Antaresia stimsoni : 1114 characters
                    [17] Antaresia childreni : 1114 characters
                    [18] Leiopython albertisii : 1114 characters
                    [19] Python reticulatus : 1114 characters
                    [20] Morelia tracyae : 1114 characters
                    [21] Morelia amethistina : 1114 characters
                    [22] Morelia nauta : 1114 characters
                    [23] Morelia kinghorni : 1114 characters
                    [24] Morelia clastolepis : 1114 characters
                    [25] Liasis fuscus : 1114 characters
                    [26] Liasis mackloti : 1114 characters
                    [27] Liasis olivaceus : 1114 characters
                    [28] Apodora papuana : 1114 characters

If you want to see the data in a particular schema, you can call the :meth:`as_string()` method, passing it a schema-specification string ("nexus", "newick", "fasta", "phylip", etc.), as well as other optional arguments specific to varous formats::

    >>> import dendropy
    >>> d = dendropy.DataSet.get_from_path('pythonidae.nex', 'nexus')
    >>> print(d.as_string("nexus"))
    >>> print(d.as_string("fasta"))
    >>> print(d.as_string("phylip"))


Taxa and Taxon Management
=========================

Operational taxonomic units in DendroPy are represented by |Taxon| objects, and distinct collections of operational taxonomic units are represented by |TaxonSet| objects.

Every time a definition of taxa is encountered in a data source, for example, a "TAXA" block in a NEXUS file, a new |TaxonSet| object is created and populated with |Taxon| objects corresponding to the taxa defined in the data source.
Some data formats do not have explicit definition of taxa, e.g. a NEWICK tree source.
These nonetheless can be considered to have an implicit definition of a collection of operational taxonomic units given by the aggregate of all operational taxonomic units referenced in the data (i.e., the set of all distinct labels on trees in a NEWICK file).

Every time a reference to a taxon is encountered in a data source, such as a taxon label in a tree or matrix statement in a NEXUS file, the current |TaxonSet| object is searched for corresponding |Taxon| object with a matching label (see below for details on how the match is made). If found, the |Taxon| object is used to represent the taxon. If not, a new |Taxon| object is created, added to the |TaxonSet| object, and used to represent the taxon.

DendroPy maps taxon definitions encountered in a data source to |Taxon| objects by the taxon label.
The labels have to match **exactly** for the taxa to be correctly mapped, with the match being **case-sensitive**.
Thus, "Python regius", "PYTHON REGIUS", "python regious", "P. regius", etc. will all be considered as referring to distinct and different taxa.

Further quirks may arise due to some schema-specific idiosyncracies.
For example, the NEXUS standard dictates that an underscore ("_") should be substituted for a space in all labels.
Thus, when reading a NEXUS or NEWICK source, the taxon labels "Python_regius" and "Python regius" are exactly equivalent, and will be mapped to the same |Taxon| object.

However, this underscore-to-space mapping does **not** take place when reading, for example, a FASTA schema file.
Here, underscores are preserved, and thus "Python_regius" does not map to "Python regius".
This means that if you were to read a NEXUS file with the taxon label, "Python_regius", and later a read a FASTA file with the same taxon label, i.e., "Python_regius", these would map to different taxa!
This is illustrated by the following:

.. literalinclude:: /examples/taxon_labels1.py
    :linenos:

Which produces the following, almost certainly incorrect, result::

    TaxonSet object at 0x43b4e0 (TaxonSet4437216): 4 Taxa
        [0] Taxon object at 0x22867b0 (Taxon36202416): 'Python regious'
        [1] Taxon object at 0x2286810 (Taxon36202512): 'Python sebae'
        [2] Taxon object at 0x22867d0 (Taxon36202448): 'Python_regious'
        [3] Taxon object at 0x2286830 (Taxon36202544): 'Python_sebae'

Even more confusingly, if this file is written out in NEXUS schema, it would result in the space/underscore substitution taking place, resulting in two pairs of taxa with the same labels.

If you plan on mixing sources from different formats, it is important to keep in mind the space/underscore substitution that takes place by default with NEXUS/NEWICK formats, but does not take place with other formats.

You could simply avoid underscores and use only spaces instead:

.. literalinclude:: /examples/taxon_labels2.py
    :linenos:

Which results in::

    TaxonSet object at 0x43b4e0 (TaxonSet4437216): 2 Taxa
        [0] Taxon object at 0x22867b0 (Taxon36202416): 'Python_regious'
        [1] Taxon object at 0x2286810 (Taxon36202512): 'Python_sebae'

Or use underscores in the NEXUS-formatted data, but spaces in the non-NEXUS data:

.. literalinclude:: /examples/taxon_labels2b.py
    :linenos:

Which results in the same as the preceding example::

    TaxonSet object at 0x43b4e0 (TaxonSet4437216): 2 Taxa
        [0] Taxon object at 0x22867b0 (Taxon36202416): 'Python regious'
        [1] Taxon object at 0x2286810 (Taxon36202512): 'Python sebae'

You can also wrap the underscore-bearing labels in the NEXUS/NEWICK source in quotes, which preserves them from being substituted for spaces:

.. literalinclude:: /examples/taxon_labels3.py
    :linenos:

Which will result in::

    TaxonSet object at 0x43c780 (TaxonSet4441984): 2 Taxa
        [0] Taxon object at 0x2386770 (Taxon37250928): 'Python_regious'
        [1] Taxon object at 0x2386790 (Taxon37250960): 'Python_sebae'

Finally, you can also override the default behavior of DendroPy's NEXUS/NEWICK parser by passing the keyword argument ``preserve_underscores=True`` to any :meth:`read_from_*`, :meth:`get_from_*` or stream-parsing constructor. For example:

.. literalinclude:: /examples/taxon_labels4.py
    :linenos:

will result in::

    TaxonSet object at 0x43c780 (TaxonSet4441984): 2 Taxa
        [0] Taxon object at 0x2386770 (Taxon37250928): 'Python_regious'
        [1] Taxon object at 0x2386790 (Taxon37250960): 'Python_sebae'

This may seem the simplest solution, in so far as it means that you need not maintain lexically-different taxon labels across files of different formats, but a gotcha here is that if writing to NEXUS/NEWICK schema, any label with underscores will be automatically quoted to preserve the underscores (again, as dictated by the NEXUS standard), which will mean that: (a) your output file will have quotes, and, as a result, (b) the underscores in the labels will be "hard" underscores if the file is read by PAUP* or DendroPy. So, for example, continuing from the previous example, the NEXUS-formatted output would look like::

    >>> print(d.as_string('nexus'))
    #NEXUS

    BEGIN TAXA;
        TITLE TaxonSet5736800;
        DIMENSIONS NTAX=2;
        TAXLABELS
            'Python_regious'
            'Python_sebae'
      ;
    END;

    BEGIN CHARACTERS;
        TITLE DnaCharacterMatrix37505040;
        LINK TAXA = TaxonSet5736800;
        DIMENSIONS  NCHAR=5;
        FORMAT DATATYPE=DNA GAP=- MISSING=? MATCHCHAR=.;
        MATRIX
    'Python_regious'    ACGTA
    'Python_sebae'      ACGTA
        ;
    END;

    BEGIN CHARACTERS;
        TITLE DnaCharacterMatrix37504848;
        LINK TAXA = TaxonSet5736800;
        DIMENSIONS  NCHAR=4;
        FORMAT DATATYPE=DNA GAP=- MISSING=? MATCHCHAR=.;
        MATRIX
    'Python_regious'    AAAA
    'Python_sebae'      ACGT
        ;
    END;

Note that the taxon labels have changed semantically between the input and the NEXUS output, as, according to the NEXUS standard, "Python_regius", while equivalent to "Python regius", is **not** equivalent to "'Python_regius'".
To control this, you can pass the keyword argument ``quote_underscores=False`` to any :meth:`write_to_*`, or :meth:`as_string()` method, which will omit the quotes even if the labels contain underscores::

    >>> print(d.as_string('nexus', quote_underscores=False))
    #NEXUS

    BEGIN TAXA;
        TITLE TaxonSet5736800;
        DIMENSIONS NTAX=2;
        TAXLABELS
            Python_regious
            Python_sebae
      ;
    END;

    BEGIN CHARACTERS;
        TITLE DnaCharacterMatrix37505040;
        LINK TAXA = TaxonSet5736800;
        DIMENSIONS  NCHAR=5;
        FORMAT DATATYPE=DNA GAP=- MISSING=? MATCHCHAR=.;
        MATRIX
    Python_regious    ACGTA
    Python_sebae      ACGTA
        ;
    END;

    BEGIN CHARACTERS;
        TITLE DnaCharacterMatrix37504848;
        LINK TAXA = TaxonSet5736800;
        DIMENSIONS  NCHAR=4;
        FORMAT DATATYPE=DNA GAP=- MISSING=? MATCHCHAR=.;
        MATRIX
    Python_regious    AAAA
    Python_sebae      ACGT
        ;
    END;