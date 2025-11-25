import uproot

file_path = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251027T0850_40.root"

with uproot.open(file_path) as f:
    tree = f["daq"]
    print("Branch names:")
    for branch_name in tree.keys():
        print(branch_name)
