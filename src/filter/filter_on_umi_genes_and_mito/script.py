
import muon
import scanpy as sc

import os
import matplotlib
import scipy.io
import numpy as np

### VIASH START

par = {
    "input": "resources/test/pbmc_1k_protein_v3/pbmc_1k_protein_v3_filtered_feature_bc_matrix.h5mu",
    "output": "out.h5mu",
    "minUMICount": 200,
    "maxUMICount": 500000,
    "minGeneCount": 200,
    "maxGeneCount": 10000,
    "minGeneOccurenceInCell": 3,
    "minFractionMito": .00001,
    "maxFractionMito": .2
}

### VIASH END

minUMICounts = par["minUMICount"]
maxUMICounts = par["maxUMICount"]
minGeneCount = par["minGeneCount"]
maxGeneCount = par["maxGeneCount"]
minGeneOccurenceInCell = par["minGeneOccurenceInCell"]
minFractionMito = par["minFractionMito"]
maxFractionMito = par["maxFractionMito"]

matplotlib.rcParams['figure.figsize'] = [3, 3]

data.var_names_make_unique()

sc.pp.filter_cells(data, min_genes=0) # Hack to generate the n_genes column
sc.pp.filter_genes(data, min_cells=0)

priorFilteringCellCount = data.n_obs
priorFilteringGeneCount = len(data.var[data.var["n_cells"] > 0])

data.obs['n_counts'] = np.ravel(np.sum(data.X, axis=1))

print("Filtering genes occuring in <" + str(self.minGeneOccurenceInCell) + " cells.")
sc.pp.filter_genes(data, min_cells=self.minGeneOccurenceInCell)
print("Filtering cells with zero counts.")
sc.pp.filter_cells(data, min_genes=1) # Hack to generate the n_genes column

mito_genes = data.var_names.str.startswith("MT-")
data.obs['percent_mito'] = np.ravel(np.sum(
data[:, mito_genes].X, axis=1)) / np.ravel(np.sum(data.X, axis=1))

print("Filtering cells with <" + str(self.minGeneCount) + " genes.")
sc.pp.filter_cells(data, min_genes=self.minGeneCount)
print("Filtering cells with >" + str(self.maxGeneCount) + " genes.")
sc.pp.filter_cells(data, max_genes=self.maxGeneCount)

print("Filtering cells based on <" + str(self.minUMICounts) + " and >" + str(self.maxUMICounts) + " UMI counts.")
data = data[data.obs['n_counts'] >= self.minUMICounts, :]
data = data[data.obs['n_counts'] <= self.maxUMICounts, :]
print("Filtering cells based on mitochondrial ratio >" + str(self.maxFractionMito) + ".")
data = data[data.obs['percent_mito'] <= self.maxFractionMito, :]
print("Filtering cells based on mitochondrial ratio <" + str(self.minFractionMito) + ".")
data = data[data.obs['percent_mito'] >= self.minFractionMito, :]

sc.pp.filter_genes(data, min_counts=1)

data.raw = data.copy()

postFilteringCellCount = data.n_obs
postFilteringGeneCount = len(data.var[data.var["n_cells"] > 0])

data.uns["filteringParameters"] = {
    "Filtering: minGeneOccurenceInCell": self.minGeneOccurenceInCell,
    "Filtering: minUMICounts": self.minUMICounts,
    "Filtering: maxUMICounts": self.maxUMICounts,
    "Filtering: minGeneCount": self.minGeneCount,
    "Filtering: maxGeneCount": self.maxGeneCount,
    "Filtering: minFractionMito": self.minFractionMito,
    "Filtering: maxFractionMito": self.maxFractionMito
}

print("Resulting data: " +  str(data))

data = sc.read_h5ad(par["input"])

data = filter.filter(data)

data.write(par["output"], compression = par["compression"])
