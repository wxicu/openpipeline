nextflow.enable.dsl=2

workflowDir = params.rootDir + "/workflows"
targetDir = params.rootDir + "/target/nextflow"

include { leiden } from targetDir + '/cluster/leiden/main.nf'
include { scanorama } from targetDir + '/integrate/scanorama/main.nf'
include { umap } from targetDir + '/dimred/umap/main.nf'
include { move_obsm_to_obs } from targetDir + '/metadata/move_obsm_to_obs/main.nf'
include { find_neighbors } from targetDir + '/neighbors/find_neighbors/main.nf'

include { readConfig; helpMessage; preprocessInputs; channelFromParams } from workflowDir + "/utils/WorkflowHelper.nf"
include { setWorkflowArguments; getWorkflowArguments; passthroughMap as pmap } from workflowDir + "/utils/DataflowHelper.nf"

config = readConfig("$workflowDir/multiomics/integration/scanorama_leiden/config.vsh.yaml")

workflow {
  helpMessage(config)

  channelFromParams(params, config)
    | view { "Input: $it" }
    | run_wf
    | view { "Output: $it" }
}

workflow run_wf {
  take:
  input_ch

  main:
  output_ch = input_ch
    | preprocessInputs("config": config)
    // split params for downstream components
    | setWorkflowArguments(
      scanorama: [
        "obsm_input": "X_pca",
        "obs_batch": "sample_id",
        "obsm_output": "obsm_integrated",
        "modality": "modality"
      ],
      neighbors: [
        "uns_output": "uns_neighbors",
        "obsp_distances": "obsp_neighbor_distances",
        "obsp_connectivities": "obsp_neighbor_connectivities",
        "obsm_input": "obsm_integrated",
        "modality": "modality"

      ],
      clustering: [
        "obsp_connectivities": "obsp_neighbor_connectivities",
        "obs_name": "obs_cluster",
        "resolution": "leiden_resolution",
        "modality": "modality"

      ],
      umap: [ 
        "uns_neighbors": "uns_neighbors",
        "output": "output",
        "obsm_output": "obsm_umap",
        "modality": "modality"

      ],
      move_obsm_to_obs_leiden: []
    )
    | getWorkflowArguments(key: "scanorama")
    | scanorama
    | getWorkflowArguments(key: "neighbors")
    | find_neighbors
    | getWorkflowArguments(key: "clustering")
    | leiden.run(args: [obsm_name: "leiden"])
    | getWorkflowArguments(key: "umap")
    | umap
    | getWorkflowArguments(key: "move_obsm_to_obs_leiden")
    | move_obsm_to_obs.run(
        args: [ obsm_key: "leiden", output_compression: "gzip" ],     
        auto: [ publish: true ]
    )

    // remove splitArgs
    | map { tup ->
      tup.take(2) + tup.drop(3)
    }

  emit:
  output_ch
}

workflow test_wf {
  // allow changing the resources_test dir
  params.resources_test = params.rootDir + "/resources_test"

  // or when running from s3: params.resources_test = "s3://openpipelines-data/"
  testParams = [
    param_list: [
      [
        id: "foo",
        input: params.resources_test + "/pbmc_1k_protein_v3/pbmc_1k_protein_v3_mms.h5mu",
        layer: "log_normalized",
        leiden_resolution: [1, 0.25]
      ]
    ]
  ]

  output_ch =
    channelFromParams(testParams, config)
    | view { "Input: $it" }
    | run_wf
    | view { output ->
      assert output.size() == 2 : "outputs should contain two elements; [id, file]"
      assert output[1].toString().endsWith(".h5mu") : "Output file should be a h5mu file. Found: ${output_list[1]}"
      "Output: $output"
    }
    | toList()
    | map { output_list ->
      assert output_list.size() == 1 : "output channel should contain 1 event"
      assert (output_list.collect({it[0]}) as Set).equals(["foo"] as Set): "Output ID should be same as input ID"
    }
    //| check_format(args: {""}) // todo: check whether output h5mu has the right slots defined
}