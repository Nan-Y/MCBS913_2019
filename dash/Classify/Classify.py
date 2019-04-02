#! python3
import sys, os
import statistics
import argparse
from Bio import SeqIO
from Tree import Tree
from Node import Node
from Dash import Dash

#tree = Tree()


def fillTaxonomyLookup(tax_path):
    # expected input is, Accession\tKingdom;Phylum;Class;etc
    taxonomy_lookup = {}
    for line in open(tax_path):
        id, taxonomy = line.rstrip().split('\t')
        taxonomy_lookup[id] = taxonomy
    return taxonomy_lookup


def processQuery(query, distance, cur_tree):
    cur_tree.add(query, distance)


# total classify sequence
def classify_sequence(totalNodes):
    totalNodes.pop("_root")
    taxon = ''
    top_score = 0.0
    #k is name in string type, v is node instance
    for k,v in totalNodes.items():
        distanceList = v.getDistance()
        score = max([float(x) for x in distanceList])
        score = statistics.median([float(x) for x in distanceList])
        print(k,score,sorted(distanceList,reverse=True))
        if score > top_score:
            top_score = score
            taxon = k

    return taxon


def classify_sequenceByName(name):
    distanceList = tree.getDistanceByName(name)
    taxon = ''
    top_score = 0.0
    score = max([float(x) for x in distanceList])
    score = statistics.median([float(x) for x in distanceList])
    print(k,score,sorted(distanceList,reverse=True))


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('target', action='store', help='path to query genome to be compared to database')
    parser.add_argument('-database', '-d', action='store', help='path to genome database')
    parser.add_argument('-path_file', '-p', action='store', help='A Text file with the paths to genomes one per line')
    parser.add_argument('-tax_lookup', '-t', action='store', help='Text file with accessions and associated taxonomy', default="/home/unhTW/share/mcbs913_2019/hash_group/documents/expanded_ncbi_taxonomy.tsv")
    args = parser.parse_args()
    target_genome_path = os.path.abspath(args.target)

    # Parse taxonomy lookup
    print("\nParsing taxonomy database")
    taxonomy_lookup = fillTaxonomyLookup(args.tax_lookup)

    # Sketch the input directory
    print("\nSketching starting database")
    Dash.sketch_database(args.database)

    for seq_record in SeqIO.parse(target_genome_path, "fasta"):
        cur_tree = Tree()
        # grab sequence information
        header = seq_record.id
        sequence = seq_record.seq

        # Create a tmp file named after the contig
        temp_file = header.split('_')[1] + '.fna'
        file_handle = open(temp_file, 'w')
        file_handle.writelines('>' + header + '\n' + sequence + '\n')
        file_handle.close()

        # sketch the new file
        print("Sketching a contig")
        temp_sketch = Dash.sketch_file(temp_file)

        # iterate through the database and calculate distance with dashing
        print("\nDashing contig against database")
        directory_path = os.path.abspath(args.database)

        # PYTHON Threadpool

        out_file = open('my_distances.txt', 'w')

        for genome in [directory_path + '/' + x for x in os.listdir(directory_path) if not x.endswith('hll')]:

            # right here is when a new tree needs to be created, and delete the old tree.

            name = genome.split('/')[-1]
            dist_t = Dash.run_dashing(temp_file, genome)
            distance = dist_t.split('\n')[4].split('\t')[2]

            # Determine taxonomy data
            tax_id = name.split('_')[2]
            taxonomy = taxonomy_lookup[tax_id]
            seven_levels = [0, 1, 2, 5, 8, 10, 12, 13]
            reduced_taxonomy = []
            index = 0
            for t in taxonomy.split(';'):
                if index in seven_levels:
                    reduced_taxonomy.append(t)
                index += 1

            # Add data to classifying tree
            #print (reduced_taxonomy, distance)
            out_file.writelines(':'.join(reduced_taxonomy) + '\t' + str(distance) + '\n')
            processQuery(reduced_taxonomy, distance, cur_tree)

            # output.writelines((temp_file + ',' + name + ',' + dist + '\n'))
        out_file.close()
        # classify sequence
        print("Classifying contig using maximum values")
        cur_tree.getMaxDistPath()

        # Clean up temp files
        os.remove(temp_sketch)
        os.remove(temp_file)

        sys.exit()

    output.close()


    fileName = sys.argv[1]
    original = []
    count = 1
    for line in open(fileName):
        distance,full_tax = line.rstrip().split('\t')
        query = full_tax.split(':')[1:]
        #print(distance,query)
        count+=1
        original.append(query)
        processQuery(query,distance)

    #print(tree.getDistanceByName("Eukaryota"))
    totalNodes = {}
    totalNodes = tree.getTotalNodes()
    #classify_sequence(totalNodes)
    tree.getMaxDistFromChildren()

    #tree.printTree()


    # treePathDir = tree.getPathDir()
    # treeAllPath = tree.getAllPath()

    # checking(original,treePathDir,treeAllPath)
    # diff = 0
    # for x in original:

    # 	flag = tree.check(x)
    # 	if flag ==False:
    # 		diff += 1

    # for x in original:
    # 	print(x)
    # 	tmp = tree.getDistance(x)
    # 	for k,v in tmp.items():
    # 		print(k,v)

    # print(diff)
    # tree.testFuc()

if __name__== "__main__":
    main()
