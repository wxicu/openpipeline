# Openpipeline - design 
## Version 20211013


__Questions:__

1. What with metadata on the cells?
2. How do we define cell ids? At the moment we use the default as in scanpy BCODE-DIGIT-SAMPLEID
3. Bookkeeping
4. Where do we do Ab/lipid/vcf demultiplexing? (After the count step?)
5. Meta-cells
6. Count imputations
7. Compute environment awareness ==> GPUs/TPUs/...

## Pipeline architecture overview

![Global overview](figures/pipelines-target-p3.png)
_Overview single cell processing pipelines in openpipeline. Every rectangle is a pipeline or component by itself of which multiple versions can exist. Data aggregation is performed in the circles. The major parts of the pipeline consist of Ingestion, Per sample processing, Integration, Transformation and Reporting._ 


## Ingestion

Purpose: Convert raw sequencing data or count tables into h5ad data for further processing. 

Pipelines list: 
- seq_demultiplex: Converts BCL to read data
- [read_mapping](pipeline/read_mapping.md): Converts reads/UMIs to count matrices
- input_conversion: Converts count matrices from different formats into h5ad data objects containing a single modality and sample
- vdj_mapping: Converts reads to clonotypes

## Per sample processing

Purpose: Per modality fitering pipelines are available to select true from false cells. At the final stage of this part the different modalities are merged into a single muon object. Merging can be performed by combining the different filterings or only using a single filtering.

Pipelines list: 
- [ps_tx_processing](pipeline/ps_tx_processing.md): Filters raw transcriptomics count data using the count profiles
- ps_adt_processing: Filters raw adt count data using the count profiles
- ps_atac_processing: Filters raw atac count/peak data 
- ps_rna_velo_processing: Filters raw transcriptomics count data with splicing variants using the count profiles 
- merge: Combine the data from different single modalities for a single sample into a merged dataset. This implies that there is a method to merge the data, i.e. intersection, union, or master, i.e. only retain cells in a specific modality.

### Concat

Purpose: Combining different samples together over different modalities.

Pipeline list: 
- [concat](pipeline/concat.md): Takes multiple single sample muons and combines them together into a single multi-sample muon object.

### Integration

Purpose: Performs an integration pipeline for single cell data based on a single or multiple modalities. 

Pipeline list: 
- [integration](pipeline/integration.md): Takes a multi-sample muon data object and generates a projection over the data for the mulitple samples in the object.

### Transformation

Purpose: Perform transformations on the initial multi-sample muon object to generate novel annotations onto the dataset for further analysis.

Pipeline list:
- [Clustering](pipeline/clustering.md)
- TI: Trajectory inference
- GRN: Gene regulatory network reconstruction
- Celltyping
- ...


### Annotation

Purpose: Take different dataset annotations and combine them together into a single enriched dataset. The idea is to have a diff_muon object, i.e. a muon object containing the changes of the original object where data from the diff_muon will be pushed to the original muon object. 

__!!! Remark, this is what we did a time ago and it has the drawback that it could make everything very slow. So we need to be able to aggregate diffs before adding them to the final object.__

Pipeline list:
- annotation: Takes as input (1) a master muon object and (2) at least one diff_muon object that contains new annotations. All annotations from the different diff_muon objects are merged and added to the master muon object.


### Reporting

Purpose: Provide standardized reporting on the final dataset.

Pipeline list: 
- qc: General QC report on the data.
- pseudobulk: Differential expression report/pipeline.
- compositional analysis: Describing and comparing the distributions of different annotations. 
- ...

__This can be very flexible, we now use a ipynb that we can add to the pipelines that gets generated with the resulting data. As such we can reuse some standardized notebooks. The difficulty here is the dependency managment in the notebook.__


### Data definition

![Data flow overview](figures/data-flow.png)

## Version 20210929

![Overview single cell processing pipelines - version 20210919](figures/pipelines-target-p1.png)
_Overview single cell processing pipelines._

Remarks:
1. What with multi-modal data integration? 
2. RNA-velocity is starting at the wrong location since it is only a different mapping step.
3. Muon objects to be used for the multi-modal data.

